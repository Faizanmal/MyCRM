"""
Unit tests for Session Authentication & Token Security Hardening
"""
import pyotp
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from multi_tenant.models import Organization, OrganizationMember
from multi_tenant.middleware import reset_tenant_context
from user_management.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
class TestSessionAuthHardening:
    """Verifies HttpOnly cookies, token rotation, replay defense, 2FA gating, and logout"""

    def setup_method(self):
        reset_tenant_context()
        self.org = Organization.objects.create(slug="auth-test-org", name="Auth Test Org", status="active")
        self.user = User.objects.create_user(username="test_auth_user", email="auth@test.local", password="SecurePassword123!")
        OrganizationMember.objects.create(organization=self.org, user=self.user, role="admin", is_active=True)
        self.client = APIClient()

    def teardown_method(self):
        reset_tenant_context()

    def test_httponly_cookie_issuance_and_access(self):
        """Login sets HttpOnly, SameSite=Lax cookies, which can access protected endpoints"""
        res_login = self.client.post('/api/auth/login/', {
            'username': 'test_auth_user',
            'password': 'SecurePassword123!'
        }, format='json')
        assert res_login.status_code == status.HTTP_200_OK

        cookies = res_login.cookies
        assert cookies['access_token']['httponly'] is True
        assert cookies['refresh_token']['httponly'] is True
        assert cookies['access_token']['samesite'] == 'Lax'

        # Authenticate via cookie alone (no Authorization header)
        cookie_client = APIClient()
        cookie_client.cookies['access_token'] = cookies['access_token'].value
        cookie_client.credentials(HTTP_X_ORGANIZATION_SLUG=self.org.slug)
        res_api = cookie_client.get('/api/v1/leads/')
        assert res_api.status_code == status.HTTP_200_OK

    def test_refresh_token_rotation_and_replay_defense(self):
        """Rotates refresh token upon refresh and rejects replay attempts"""
        res_login = self.client.post('/api/auth/login/', {
            'username': 'test_auth_user',
            'password': 'SecurePassword123!'
        }, format='json')
        old_refresh = res_login.cookies['refresh_token'].value

        # First refresh
        refresh_client = APIClient()
        refresh_client.cookies['refresh_token'] = old_refresh
        res_refresh = refresh_client.post('/api/auth/refresh/', {}, format='json')
        assert res_refresh.status_code == status.HTTP_200_OK
        new_refresh = res_refresh.cookies['refresh_token'].value
        assert new_refresh != old_refresh

        # Replay attempt with old_refresh
        replay_client = APIClient()
        replay_client.cookies['refresh_token'] = old_refresh
        res_replay = replay_client.post('/api/auth/refresh/', {}, format='json')
        assert res_replay.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

    def test_two_factor_auth_gating(self):
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

        # Valid code succeeds
        totp = pyotp.TOTP(secret)
        res_valid = self.client.post('/api/auth/verify-2fa/', {
            'user_id': self.user.id,
            'temp_token': temp_token,
            'code': totp.now()
        }, format='json')
        assert res_valid.status_code == status.HTTP_200_OK
        assert 'access' in res_valid.json()
        assert 'access_token' in res_valid.cookies

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
