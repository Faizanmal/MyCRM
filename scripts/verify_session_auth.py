#!/usr/bin/env python
"""
Verification Script: 02-session-auth
Validates:
1. HttpOnly Session Cookie issuance and access:
   - Login sets HttpOnly access_token & refresh_token cookies with SameSite=Lax.
   - Protected API endpoints authenticate via HttpOnly cookie alone.
   - JavaScript cannot access session credentials in storage.
2. CSRF Strategy:
   - Mutative requests via HttpOnly cookie without CSRF token are rejected with 403 Forbidden.
   - Mutative requests with valid CSRF token header succeed.
3. Refresh Token Rotation & Replay Attack Defense:
   - Refresh token is rotated to new cryptographic value.
   - Replay attempt with old/blacklisted refresh token is denied.
   - Tampered refresh token is denied.
4. 2FA Gating, TOTP & Backup Recovery Codes:
   - 2FA gating challenges login and suppresses full tokens.
   - Valid TOTP code exchanges challenge for full session tokens.
   - Backup recovery code works for account recovery and is consumed upon use (single-use).
   - Reusing a consumed backup code is denied.
5. Immediate Revocation on Logout:
   - Logout immediately blacklists refresh token and clears session cookies.
6. SSO Hardening:
   - OAuth state verification prevents OAuth CSRF attacks.
   - Redirect URI validation rejects open redirectors.
   - Cross-tenant SSO binding enforcement blocks foreign tenant users.
"""
import os
import sys
import django

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import pyotp
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.middleware.csrf import _get_new_csrf_string, _mask_cipher_secret
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from multi_tenant.models import Organization, OrganizationMember
from multi_tenant.middleware import reset_tenant_context
from user_management.models import UserProfile
from user_management.views import generate_backup_codes
from sso_integration.models import SSOProvider
from sso_integration.services import OAuth2Service, SSOAuthenticationService

User = get_user_model()


def run_session_auth_checks():
    print("=" * 70)
    print("STARTING 02-SESSION-AUTH ADVERSARIAL VERIFICATION SUITE")
    print("=" * 70)

    reset_tenant_context()

    # 1. Setup Tenant & Users
    org, _ = Organization.objects.get_or_create(
        slug="session-tenant",
        defaults={"name": "Session Corp", "status": "active"}
    )
    foreign_org, _ = Organization.objects.get_or_create(
        slug="foreign-session-tenant",
        defaults={"name": "Foreign Session Corp", "status": "active"}
    )

    user, _ = User.objects.get_or_create(
        username="session_user",
        defaults={"email": "session@example.com"}
    )
    user.set_password("SessionPass123!")
    user.two_factor_enabled = False
    user.two_factor_secret = ""
    user.role = "sales_rep"
    user.save()

    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.two_factor_enabled = False
    profile.two_factor_secret = ""
    profile.two_factor_backup_codes = []
    profile.save()

    mem = OrganizationMember.objects.filter(user=user, organization=org).first()
    if not mem:
        OrganizationMember.objects.create(
            organization=org,
            user=user,
            role="admin",
            is_active=True
        )

    # =========================================================================
    # CHECK 1: HttpOnly Cookie Authentication & Login Flow
    # =========================================================================
    print("\n[Check 1] HttpOnly Cookie Generation & Authentication")
    client = APIClient()
    login_res = client.post('/api/auth/login/', {
        'username': 'session_user',
        'password': 'SessionPass123!'
    }, format='json')
    assert login_res.status_code == 200, f"Login failed: {login_res.status_code}"

    # Verify cookies
    cookies = login_res.cookies
    assert 'access_token' in cookies, "Missing access_token cookie"
    assert 'refresh_token' in cookies, "Missing refresh_token cookie"
    assert cookies['access_token']['httponly'] is True, "access_token must be HttpOnly"
    assert cookies['refresh_token']['httponly'] is True, "refresh_token must be HttpOnly"
    assert cookies['access_token']['samesite'] == 'Lax', "Cookie must have SameSite=Lax"
    print("  PASS: Login response issues HttpOnly, SameSite=Lax session cookies.")

    # Access protected CRM endpoint using ONLY HttpOnly cookie (no Authorization header)
    cookie_client = APIClient()
    cookie_client.cookies['access_token'] = cookies['access_token'].value
    cookie_client.credentials(HTTP_X_ORGANIZATION_SLUG=org.slug)
    res_cookie_auth = cookie_client.get('/api/v1/leads/')
    assert res_cookie_auth.status_code == 200, f"Expected 200 via HttpOnly cookie auth, got {res_cookie_auth.status_code}"
    print("  PASS: Protected CRM API accessed successfully via HttpOnly session cookie.")

    # =========================================================================
    # CHECK 2: CSRF Protection on Cookie Authentication
    # =========================================================================
    print("\n[Check 2] CSRF Protection on Cookie-Authenticated Mutative Requests")
    csrf_check_client = APIClient(enforce_csrf_checks=True)
    csrf_check_client.cookies['access_token'] = cookies['access_token'].value
    csrf_check_client.credentials(HTTP_X_ORGANIZATION_SLUG=org.slug)

    # Mutative request without CSRF token -> Rejected (403)
    res_no_csrf = csrf_check_client.post('/api/v1/leads/', {
        'first_name': 'Attacker',
        'last_name': 'Lead',
        'company_name': 'AttackerCo',
        'email': 'attacker@bad.local'
    }, format='json')
    assert res_no_csrf.status_code == 403, f"Expected 403 for missing CSRF, got {res_no_csrf.status_code}"
    print("  PASS: Mutative request without CSRF token rejected with 403 Forbidden.")

    # Mutative request with valid CSRF cookie and X-CSRFToken header -> Success
    raw_secret = _get_new_csrf_string()
    masked_token = _mask_cipher_secret(raw_secret)
    valid_csrf_client = APIClient(enforce_csrf_checks=True)
    valid_csrf_client.cookies['access_token'] = cookies['access_token'].value
    valid_csrf_client.cookies['csrftoken'] = masked_token
    valid_csrf_client.credentials(
        HTTP_X_ORGANIZATION_SLUG=org.slug,
        HTTP_X_CSRFTOKEN=masked_token
    )
    res_with_csrf = valid_csrf_client.post('/api/v1/leads/', {
        'first_name': 'Verified',
        'last_name': 'CSRF',
        'company_name': 'VerifiedCo',
        'email': 'verified_csrf@example.local'
    }, format='json')
    assert res_with_csrf.status_code == 201, f"Expected 201 with valid CSRF, got {res_with_csrf.status_code}"
    print("  PASS: Mutative request with valid X-CSRFToken header accepted.")

    # =========================================================================
    # CHECK 3: Token Rotation and Replay Attack Rejection
    # =========================================================================
    print("\n[Check 3] Token Rotation & Replay Attack Defense")
    raw_refresh = cookies['refresh_token'].value

    # First rotation attempt -> succeeds
    refresh_client = APIClient()
    refresh_client.cookies['refresh_token'] = raw_refresh
    res_rot_1 = refresh_client.post('/api/auth/refresh/', {}, format='json')
    assert res_rot_1.status_code == 200, f"Expected 200 for refresh rotation, got {res_rot_1.status_code}"
    new_refresh = res_rot_1.cookies['refresh_token'].value
    assert new_refresh != raw_refresh, "Refresh token was not rotated!"
    print("  PASS: Refresh token rotated to new cryptographic secret.")

    # Replay attack: attempt to use the OLD (blacklisted) refresh token again
    replay_client = APIClient()
    replay_client.cookies['refresh_token'] = raw_refresh
    res_replay = replay_client.post('/api/auth/refresh/', {}, format='json')
    assert res_replay.status_code in [400, 401], f"Expected 401/400 for replayed refresh token, got {res_replay.status_code}"
    print("  PASS: Replayed / blacklisted refresh token strictly rejected.")

    # Tampered refresh token
    tampered_client = APIClient()
    tampered_client.cookies['refresh_token'] = raw_refresh[:-4] + "fake"
    res_tampered = tampered_client.post('/api/auth/refresh/', {}, format='json')
    assert res_tampered.status_code in [400, 401]
    print("  PASS: Tampered refresh token denied.")

    # =========================================================================
    # CHECK 4: 2FA Gating, TOTP & Backup Recovery Codes
    # =========================================================================
    print("\n[Check 4] Two-Factor Authentication Gating & Backup Recovery Codes")
    # Enable 2FA on user with backup codes
    secret = pyotp.random_base32()
    plain_codes, hashed_codes = generate_backup_codes(count=8)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.two_factor_enabled = True
    profile.two_factor_secret = secret
    profile.two_factor_backup_codes = hashed_codes
    profile.save()

    # Login attempt with 2FA enabled -> Challenge issued, full tokens suppressed
    client_2fa = APIClient()
    login_2fa_res = client_2fa.post('/api/auth/login/', {
        'username': 'session_user',
        'password': 'SessionPass123!'
    }, format='json')
    assert login_2fa_res.status_code == 200
    data_2fa = login_2fa_res.json()
    assert data_2fa.get('message') == '2FA verification required'
    assert 'access' not in data_2fa
    temp_token = data_2fa.get('temp_token')
    print("  PASS: 2FA challenge triggered; full access tokens suppressed.")

    # Invalid code rejected
    res_bad = client_2fa.post('/api/auth/verify-2fa/', {
        'user_id': user.id,
        'temp_token': temp_token,
        'code': '999999'
    }, format='json')
    assert res_bad.status_code == 400
    print("  PASS: Malformed/incorrect 2FA code rejected.")

    # Valid backup recovery code succeeds
    used_backup_code = plain_codes[0]
    res_backup_login = client_2fa.post('/api/auth/verify-2fa/', {
        'user_id': user.id,
        'temp_token': temp_token,
        'code': used_backup_code
    }, format='json')
    assert res_backup_login.status_code == 200
    assert 'access' in res_backup_login.json()
    assert 'access_token' in res_backup_login.cookies
    print("  PASS: Valid backup recovery code successfully authenticates and issues full session.")

    # Re-using the consumed backup code is rejected
    login_2fa_res_2 = client_2fa.post('/api/auth/login/', {
        'username': 'session_user',
        'password': 'SessionPass123!'
    }, format='json')
    temp_token_2 = login_2fa_res_2.json().get('temp_token')

    res_reuse_backup = client_2fa.post('/api/auth/verify-2fa/', {
        'user_id': user.id,
        'temp_token': temp_token_2,
        'code': used_backup_code
    }, format='json')
    assert res_reuse_backup.status_code == 400
    print("  PASS: Consumed backup recovery code rejected upon replay attempt.")

    # Valid TOTP code succeeds
    totp = pyotp.TOTP(secret)
    res_valid_totp = client_2fa.post('/api/auth/verify-2fa/', {
        'user_id': user.id,
        'temp_token': temp_token_2,
        'code': totp.now()
    }, format='json')
    assert res_valid_totp.status_code == 200
    print("  PASS: Valid TOTP code successfully completes 2FA authentication.")

    # =========================================================================
    # CHECK 5: Immediate Server-Side Revocation on Logout
    # =========================================================================
    print("\n[Check 5] Immediate Token Revocation & Logout")
    session_refresh = res_valid_totp.cookies['refresh_token'].value
    res_logout = client.post('/api/auth/logout/', {'refresh': session_refresh}, format='json')
    assert res_logout.status_code == 200
    assert res_logout.cookies['access_token'].value == ''
    assert res_logout.cookies['refresh_token'].value == ''

    # Re-using logged-out refresh token fails
    res_relogin = client.post('/api/auth/refresh/', {'refresh': session_refresh}, format='json')
    assert res_relogin.status_code in [400, 401]
    print("  PASS: Logout immediately blacklists token and clears session cookies.")

    # =========================================================================
    # CHECK 6: SSO State, Redirect URI & Tenant Binding Hardening
    # =========================================================================
    print("\n[Check 6] SSO State, Redirect URI & Cross-Tenant Binding Validations")
    sso_provider, _ = SSOProvider.objects.get_or_create(
        organization=org,
        provider_name="Test Google SSO",
        defaults={
            'provider_type': 'oauth2_google',
            'client_id': 'sso_client_id_test',
            'client_secret': 'sso_secret_test',
            'authorization_url': 'https://accounts.google.com/o/oauth2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'user_info_url': 'https://openidconnect.googleapis.com/v1/userinfo',
            'scope': 'openid email profile',
            'status': 'active',
            'auto_create_users': False,
            'created_by': user,
            'last_used_at': timezone.now()
        }
    )

    oauth_svc = OAuth2Service(sso_provider)

    # State validation
    assert oauth_svc.validate_state("secure_state", "secure_state") is True
    assert oauth_svc.validate_state("secure_state", "forged_state") is False
    print("  PASS: OAuth state validation successfully verified.")

    # Redirect URI validation
    assert oauth_svc.validate_redirect_uri(sso_provider.get_redirect_uri()) is True
    assert oauth_svc.validate_redirect_uri("https://evil.com/callback") is False
    print("  PASS: Redirect URI validation successfully verified.")

    # Cross-tenant SSO binding defense
    foreign_user, _ = User.objects.get_or_create(
        username="foreign_session_user",
        defaults={"email": "foreign_session@outside.local"}
    )
    OrganizationMember.objects.get_or_create(
        organization=foreign_org,
        user=foreign_user,
        defaults={"role": "member", "is_active": True}
    )

    try:
        SSOAuthenticationService.authenticate_user(
            provider=sso_provider,
            user_data={'email': foreign_user.email}
        )
        assert False, "Cross-tenant SSO should have been blocked!"
    except ValueError as e:
        assert "Cross-tenant SSO denied" in str(e)
        print("  PASS: Cross-tenant SSO authentication blocked with explicit explanation.")

    print("\n" + "=" * 70)
    print("ALL 02-SESSION-AUTH ADVERSARIAL CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == '__main__':
    run_session_auth_checks()
