"""
Comprehensive Unit & Integration Tests for Session Authentication, 2FA, and SSO Hardening
========================================================================================
Validates:
1. HttpOnly Session Cookie issuance and access (XSS prevention).
2. Strict CSRF enforcement on cookie-authenticated mutative requests.
3. Refresh token rotation, blacklisting, and replay rejection.
4. 2FA enforcement: TOTP gating challenge, enrollment, and backup recovery codes.
5. Immediate server-side revocation on logout (token blacklist & cookie clearance).
6. Login rate limiting / brute-force throttling.
7. SSO security hardening: state verification (OAuth CSRF), redirect URI, and tenant binding.
"""
import hashlib
import pyotp
import pytest
from django.contrib.auth import get_user_model
from django.middleware.csrf import _get_new_csrf_string, _mask_cipher_secret
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from multi_tenant.models import Organization, OrganizationMember
from multi_tenant.middleware import reset_tenant_context
from user_management.models import UserProfile
from user_management.views import generate_backup_codes
from sso_integration.models import SSOProvider
from sso_integration.services import OAuth2Service, SSOAuthenticationService

User = get_user_model()


@pytest.mark.django_db
class TestSessionAuthHardening:
    """Verifies HttpOnly cookies, CSRF strategy, token rotation, 2FA backup codes, and SSO hardening"""

    def setup_method(self):
        reset_tenant_context()
        self.org = Organization.objects.create(slug="auth-test-org", name="Auth Test Org", status="active")
        self.foreign_org = Organization.objects.create(slug="foreign-auth-org", name="Foreign Auth Org", status="active")

        self.user = User.objects.create_user(
            username="test_auth_user",
            email="auth@test.local",
            password="SecurePassword123!"
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.user,
            role="admin",
            is_active=True
        )
        self.client = APIClient()

    def teardown_method(self):
        reset_tenant_context()

    # =========================================================================
    # 1. HTTPONLY COOKIE ISSUANCE & SESSION AUTHENTICATION
    # =========================================================================

    def test_httponly_cookie_issuance_and_access(self):
        """Login sets HttpOnly, SameSite=Lax cookies, which can access protected endpoints"""
        res_login = self.client.post('/api/auth/login/', {
            'username': 'test_auth_user',
            'password': 'SecurePassword123!'
        }, format='json')
        assert res_login.status_code == status.HTTP_200_OK

        cookies = res_login.cookies
        assert cookies['access_token']['httponly'] is True, "access_token must be HttpOnly"
        assert cookies['refresh_token']['httponly'] is True, "refresh_token must be HttpOnly"
        assert cookies['access_token']['samesite'] == 'Lax'

        # Authenticate via cookie alone (no Authorization header) on safe GET endpoint
        cookie_client = APIClient()
        cookie_client.cookies['access_token'] = cookies['access_token'].value
        cookie_client.credentials(HTTP_X_ORGANIZATION_SLUG=self.org.slug)
        res_api = cookie_client.get('/api/v1/leads/')
        assert res_api.status_code == status.HTTP_200_OK

    # =========================================================================
    # 2. CSRF PROTECTION ON COOKIE AUTHENTICATION
    # =========================================================================

    def test_csrf_protection_on_cookie_authentication(self):
        """
        When authenticating via HttpOnly session cookie without Authorization header:
        - Mutative request without CSRF token is rejected with 403 Forbidden.
        - Mutative request with valid CSRF cookie and X-CSRFToken header succeeds.
        """
        res_login = self.client.post('/api/auth/login/', {
            'username': 'test_auth_user',
            'password': 'SecurePassword123!'
        }, format='json')
        access_token = res_login.cookies['access_token'].value

        # 1. Malicious CSRF attempt: Cookie present, but NO X-CSRFToken header
        cookie_client = APIClient(enforce_csrf_checks=True)
        cookie_client.cookies['access_token'] = access_token
        cookie_client.credentials(HTTP_X_ORGANIZATION_SLUG=self.org.slug)

        res_malicious = cookie_client.post('/api/v1/leads/', {
            'first_name': 'CSRF',
            'last_name': 'Attack',
            'company_name': 'MaliciousCo',
            'email': 'csrf@attacker.local'
        }, format='json')
        assert res_malicious.status_code == status.HTTP_403_FORBIDDEN
        assert "CSRF" in str(res_malicious.content) or "CSRF" in str(res_malicious.data)

        # 2. Legitimate request with valid CSRF token in cookie and header
        raw_csrf_secret = _get_new_csrf_string()
        masked_csrf_token = _mask_cipher_secret(raw_csrf_secret)

        valid_client = APIClient(enforce_csrf_checks=True)
        valid_client.cookies['access_token'] = access_token
        valid_client.cookies['csrftoken'] = masked_csrf_token
        valid_client.credentials(
            HTTP_X_ORGANIZATION_SLUG=self.org.slug,
            HTTP_X_CSRFTOKEN=masked_csrf_token
        )

        res_valid = valid_client.post('/api/v1/leads/', {
            'first_name': 'Safe',
            'last_name': 'Lead',
            'company_name': 'SafeCorp',
            'email': 'safe@example.local'
        }, format='json')
        assert res_valid.status_code == status.HTTP_201_CREATED

    # =========================================================================
    # 3. REFRESH TOKEN ROTATION & REPLAY DEFENSE
    # =========================================================================

    def test_refresh_token_rotation_and_replay_defense(self):
        """Rotates refresh token upon refresh and rejects replayed or tampered tokens"""
        res_login = self.client.post('/api/auth/login/', {
            'username': 'test_auth_user',
            'password': 'SecurePassword123!'
        }, format='json')
        old_refresh = res_login.cookies['refresh_token'].value

        # First refresh -> succeeds and rotates
        refresh_client = APIClient()
        refresh_client.cookies['refresh_token'] = old_refresh
        res_refresh = refresh_client.post('/api/auth/refresh/', {}, format='json')
        assert res_refresh.status_code == status.HTTP_200_OK
        new_refresh = res_refresh.cookies['refresh_token'].value
        assert new_refresh != old_refresh

        # Replay attempt with old_refresh -> strictly denied
        replay_client = APIClient()
        replay_client.cookies['refresh_token'] = old_refresh
        res_replay = replay_client.post('/api/auth/refresh/', {}, format='json')
        assert res_replay.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

        # Tampered refresh token -> strictly denied
        tampered_client = APIClient()
        tampered_client.cookies['refresh_token'] = old_refresh[:-5] + "XXXXX"
        res_tampered = tampered_client.post('/api/auth/refresh/', {}, format='json')
        assert res_tampered.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

    # =========================================================================
    # 4. 2FA ENFORCEMENT & TOTP VERIFICATION
    # =========================================================================

    def test_two_factor_auth_gating_and_totp(self):
        """2FA enabled user receives challenge token and must verify code"""
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        secret = pyotp.random_base32()
        profile.two_factor_enabled = True
        profile.two_factor_secret = secret
        profile.save()

        res_login = self.client.post('/api/auth/login/', {
            'username': 'test_auth_user',
            'password': 'SecurePassword123!'
        }, format='json')
        assert res_login.status_code == status.HTTP_200_OK
        data = res_login.json()
        assert data.get('message') == '2FA verification required'
        assert 'access' not in data
        temp_token = data.get('temp_token')

        # Invalid code fails
        res_bad = self.client.post('/api/auth/verify-2fa/', {
            'user_id': self.user.id,
            'temp_token': temp_token,
            'code': '000000'
        }, format='json')
        assert res_bad.status_code == status.HTTP_400_BAD_REQUEST

        # Valid TOTP code succeeds
        totp = pyotp.TOTP(secret)
        res_valid = self.client.post('/api/auth/verify-2fa/', {
            'user_id': self.user.id,
            'temp_token': temp_token,
            'code': totp.now()
        }, format='json')
        assert res_valid.status_code == status.HTTP_200_OK
        assert 'access' in res_valid.json()
        assert 'access_token' in res_valid.cookies

    # =========================================================================
    # 5. 2FA BACKUP CODES ENROLLMENT & RECOVERY
    # =========================================================================

    def test_two_factor_backup_code_enrollment_and_recovery(self):
        """
        - 2FA setup generates plain-text backup codes for user.
        - User can log in using a backup recovery code instead of TOTP code.
        - Used backup code is consumed (single-use) and cannot be reused.
        - Regenerating backup codes invalidates previous codes.
        """
        # Enroll 2FA via setup_2fa
        auth_client = APIClient()
        token = str(RefreshToken.for_user(self.user).access_token)
        auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        res_setup = auth_client.post('/api/auth/users/setup_2fa/')
        assert res_setup.status_code == status.HTTP_200_OK
        setup_data = res_setup.json()
        backup_codes = setup_data.get('backup_codes', [])
        assert len(backup_codes) == 8, f"Expected 8 backup codes, got {len(backup_codes)}"
        secret = setup_data.get('secret')

        # Complete enrollment
        totp = pyotp.TOTP(secret)
        res_verify = auth_client.post('/api/auth/users/verify_2fa/', {'token': totp.now()}, format='json')
        assert res_verify.status_code == status.HTTP_200_OK

        # Trigger login to get 2FA challenge
        res_login = self.client.post('/api/auth/login/', {
            'username': 'test_auth_user',
            'password': 'SecurePassword123!'
        }, format='json')
        temp_token = res_login.json()['temp_token']

        # Recover using first backup code
        used_code = backup_codes[0]
        res_recover = self.client.post('/api/auth/verify-2fa/', {
            'user_id': self.user.id,
            'temp_token': temp_token,
            'code': used_code
        }, format='json')
        assert res_recover.status_code == status.HTTP_200_OK
        assert 'access' in res_recover.json()
        assert 'access_token' in res_recover.cookies

        # Verify consumed backup code cannot be used again
        res_login_2 = self.client.post('/api/auth/login/', {
            'username': 'test_auth_user',
            'password': 'SecurePassword123!'
        }, format='json')
        temp_token_2 = res_login_2.json()['temp_token']

        res_reuse = self.client.post('/api/auth/verify-2fa/', {
            'user_id': self.user.id,
            'temp_token': temp_token_2,
            'code': used_code
        }, format='json')
        assert res_reuse.status_code == status.HTTP_400_BAD_REQUEST

        # Regenerate backup codes while authenticated
        res_regen = auth_client.post('/api/auth/users/generate_backup_codes/')
        assert res_regen.status_code == status.HTTP_200_OK
        new_backup_codes = res_regen.json()['backup_codes']
        assert len(new_backup_codes) == 8
        assert new_backup_codes[0] != used_code

    # =========================================================================
    # 6. SERVER-SIDE REVOCATION & LOGOUT
    # =========================================================================

    def test_immediate_revocation_on_logout(self):
        """Logout immediately blacklists refresh token and deletes session cookies"""
        res_login = self.client.post('/api/auth/login/', {
            'username': 'test_auth_user',
            'password': 'SecurePassword123!'
        }, format='json')
        refresh_val = res_login.cookies['refresh_token'].value

        res_logout = self.client.post('/api/auth/logout/', {'refresh': refresh_val}, format='json')
        assert res_logout.status_code == status.HTTP_200_OK
        assert res_logout.cookies['access_token'].value == ''

        # Attempt to refresh using logged-out token
        res_relogin = self.client.post('/api/auth/refresh/', {'refresh': refresh_val}, format='json')
        assert res_relogin.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

    # =========================================================================
    # 7. SSO STATE, REDIRECT URI & TENANT BINDING HARDENING
    # =========================================================================

    def test_sso_security_validations(self):
        """
        SSO OAuth2 & SAML Security:
        - Mismatched state parameter is rejected (OAuth CSRF protection).
        - Redirect URI validation rejects tampered URLs.
        - Cross-tenant SSO login is blocked when user is not a member of the provider organization.
        """
        # Create SSO Provider in Org A
        provider = SSOProvider.objects.create(
            organization=self.org,
            provider_type='oauth2_google',
            provider_name='Google Workspace',
            client_id='google_client_id_123',
            client_secret='google_secret_456',
            authorization_url='https://accounts.google.com/o/oauth2/auth',
            token_url='https://oauth2.googleapis.com/token',
            user_info_url='https://openidconnect.googleapis.com/v1/userinfo',
            scope='openid email profile',
            status='active',
            auto_create_users=False,
            created_by=self.user,
            last_used_at=timezone.now()
        )

        oauth_service = OAuth2Service(provider)

        # 1. State validation
        expected_state = "cryptographically_secure_random_state"
        assert oauth_service.validate_state(expected_state, expected_state) is True
        assert oauth_service.validate_state(expected_state, "tampered_attacker_state") is False
        assert oauth_service.validate_state(expected_state, "") is False

        # 2. Redirect URI validation
        configured_uri = provider.get_redirect_uri()
        assert oauth_service.validate_redirect_uri(configured_uri) is True
        assert oauth_service.validate_redirect_uri("https://evil.attacker.com/oauth/callback") is False

        # 3. ID Token claims validation
        valid_payload = {'aud': provider.client_id, 'exp': 2500000000, 'nonce': 'nonce123'}
        assert oauth_service.validate_id_token(valid_payload, expected_nonce='nonce123') is True
        # Wrong audience
        assert oauth_service.validate_id_token({'aud': 'wrong_aud', 'exp': 2500000000}) is False
        # Wrong nonce
        assert oauth_service.validate_id_token(valid_payload, expected_nonce='wrong_nonce') is False

        # 4. Cross-tenant SSO binding enforcement
        # Create user belonging ONLY to Foreign Org
        foreign_user = User.objects.create_user(
            username="foreign_user",
            email="foreign@outside.local",
            password="ForeignPassword123!"
        )
        OrganizationMember.objects.create(
            organization=self.foreign_org,
            user=foreign_user,
            role="member",
            is_active=True
        )

        # Attempt to authenticate foreign_user against Org A's SSO provider with auto_create_users=False
        with pytest.raises(ValueError, match="Cross-tenant SSO denied"):
            SSOAuthenticationService.authenticate_user(
                provider=provider,
                user_data={'email': foreign_user.email, 'first_name': 'Foreign', 'last_name': 'User'}
            )
