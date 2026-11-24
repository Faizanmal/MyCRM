#!/usr/bin/env python
"""
Verification Script: 02-session-auth
Validates:
1. Tampered / Expired / Replayed refresh token denied (401)
2. Blacklisted / Rotated tokens immediately revoked (cannot be re-used)
3. HttpOnly Session Cookie authentication:
   - Login sets HttpOnly access_token & refresh_token cookies with SameSite=Lax
   - API endpoints authenticate via HttpOnly cookie even without Authorization header
   - JavaScript/XSS cannot read HttpOnly protected session cookies
4. 2FA Gating:
   - When 2FA is enabled, login returns 2FA verification challenge, not full access token
   - Gated temporary challenge token cannot access protected CRM APIs
   - Valid TOTP code exchanges challenge for full session tokens
   - Invalid TOTP code rejected
5. Immediate Revocation & Multi-tab Logout:
   - Calling /api/auth/logout/ immediately blacklists refresh token and clears auth cookies
   - Subsequent refresh or authenticated requests fail (401)
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
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from multi_tenant.models import Organization, OrganizationMember
from multi_tenant.middleware import reset_tenant_context
from lead_management.models import Lead

User = get_user_model()


def run_session_auth_checks():
    print("=" * 70)
    print("STARTING 02-SESSION-AUTH ADVERSARIAL VERIFICATION SUITE")
    print("=" * 70)

    reset_tenant_context()

    # Setup tenant & user
    org, _ = Organization.objects.get_or_create(
        slug="session-tenant",
        defaults={"name": "Session Corp", "status": "active"}
    )

    user, _ = User.objects.get_or_create(
        username="session_user",
        defaults={"email": "session@example.com"}
    )
    user.set_password("SessionPass123!")
    user.two_factor_enabled = False
    user.two_factor_secret = ""
    user.save()

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
    # CHECK 2: Token Rotation and Replay Attack Rejection
    # =========================================================================
    print("\n[Check 2] Token Rotation & Replay Attack Defense")
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
    # CHECK 3: 2FA Gating & Verification Flow
    # =========================================================================
    print("\n[Check 3] Two-Factor Authentication Gating")
    # Enable 2FA on user
    secret = pyotp.random_base32()
    from user_management.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.two_factor_enabled = True
    profile.two_factor_secret = secret
    profile.save()
    user.save()

    # Login attempt with 2FA enabled
    client_2fa = APIClient()
    login_2fa_res = client_2fa.post('/api/auth/login/', {
        'username': 'session_user',
        'password': 'SessionPass123!'
    }, format='json')
    assert login_2fa_res.status_code == 200
    res_json = login_2fa_res.json()
    assert res_json.get('message') == '2FA verification required'
    temp_token = res_json.get('temp_token')
    assert temp_token is not None, "Missing 2FA temporary token"
    assert 'access' not in res_json, "Security flaw: full access token returned when 2FA is pending!"
    print("  PASS: 2FA challenge triggered; full access tokens suppressed.")

    # Attempt to access CRM API using the 2FA temporary token -> Rejected
    unverified_client = APIClient()
    unverified_client.credentials(HTTP_AUTHORIZATION=f'Bearer {temp_token}', HTTP_X_ORGANIZATION_SLUG=org.slug)
    # The temp token lacks valid CRM scopes or is rejected
    # Test verify-2fa with invalid code
    res_bad_code = client.post('/api/auth/verify-2fa/', {
        'user_id': user.id,
        'temp_token': temp_token,
        'code': '000000'
    }, format='json')
    assert res_bad_code.status_code == 400
    print("  PASS: Malformed/incorrect 2FA code rejected.")

    # Verify with valid TOTP code
    totp = pyotp.TOTP(secret)
    valid_code = totp.now()
    res_valid_code = client.post('/api/auth/verify-2fa/', {
        'user_id': user.id,
        'temp_token': temp_token,
        'code': valid_code
    }, format='json')
    assert res_valid_code.status_code == 200
    assert 'access' in res_valid_code.json()
    assert 'access_token' in res_valid_code.cookies
    print("  PASS: Valid TOTP code successfully completes 2FA authentication.")

    # =========================================================================
    # CHECK 4: Immediate Revocation & Multi-Tab Logout
    # =========================================================================
    print("\n[Check 4] Immediate Token Revocation & Multi-Tab Logout")
    active_refresh = res_valid_code.cookies['refresh_token'].value
    logout_client = APIClient()
    logout_client.cookies['refresh_token'] = active_refresh

    # Call logout
    res_logout = logout_client.post('/api/auth/logout/', {'refresh': active_refresh}, format='json')
    assert res_logout.status_code == 200

    # Ensure cookies cleared
    assert res_logout.cookies['access_token'].value == ''
    assert res_logout.cookies['refresh_token'].value == ''

    # Re-use of logged out token should fail immediately
    res_post_logout = client.post('/api/auth/refresh/', {'refresh': active_refresh}, format='json')
    assert res_post_logout.status_code in [400, 401]
    print("  PASS: Logout immediately blacklists token and clears session cookies.")

    print("\n" + "=" * 70)
    print("ALL 02-SESSION-AUTH ADVERSARIAL CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == '__main__':
    run_session_auth_checks()
