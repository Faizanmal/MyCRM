"""
Authentication API Tests

Comprehensive test suite for authentication endpoints including:
- User registration
- Login/Logout
- Token refresh
- Password management
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create and return a test user."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


class TestUserRegistration:
    """Test cases for user registration endpoint."""

    @pytest.mark.django_db
    def test_register_user_success(self, api_client):
        """Test successful user registration."""
        url = reverse('api:v1:auth-register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    @pytest.mark.django_db
    def test_register_user_weak_password(self, api_client):
        """Test registration with weak password fails."""
        url = reverse('api:v1:auth-register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',  # Weak password
            'password_confirm': '123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_register_duplicate_email(self, api_client, test_user):
        """Test registration with existing email fails."""
        url = reverse('api:v1:auth-register')
        data = {
            'username': 'anotheruser',
            'email': test_user.email,  # Duplicate email
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Another',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUserLogin:
    """Test cases for user login endpoint."""

    @pytest.mark.django_db
    def test_login_success(self, api_client, test_user):
        """Test successful login returns tokens."""
        url = reverse('api:v1:auth-login')
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data or 'token' in response.data

    @pytest.mark.django_db
    def test_login_invalid_credentials(self, api_client, test_user):
        """Test login with invalid credentials fails."""
        url = reverse('api:v1:auth-login')
        data = {
            'username': 'testuser',
            'password': 'WrongPassword!'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST]

    @pytest.mark.django_db
    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent user fails."""
        url = reverse('api:v1:auth-login')
        data = {
            'username': 'nonexistent',
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST]


class TestTokenRefresh:
    """Test cases for token refresh endpoint."""

    @pytest.mark.django_db
    def test_token_refresh_success(self, api_client, test_user):
        """Test successful token refresh."""
        # First login to get tokens
        login_url = reverse('api:v1:auth-login')
        login_data = {'username': 'testuser', 'password': 'TestPass123!'}
        login_response = api_client.post(login_url, login_data, format='json')

        if 'refresh' in login_response.data:
            refresh_url = reverse('api:v1:auth-token-refresh')
            refresh_data = {'refresh': login_response.data['refresh']}
            response = api_client.post(refresh_url, refresh_data, format='json')

            assert response.status_code == status.HTTP_200_OK
            assert 'access' in response.data


class TestProtectedEndpoints:
    """Test that protected endpoints require authentication."""

    @pytest.mark.django_db
    def test_me_endpoint_requires_auth(self, api_client):
        """Test /me endpoint requires authentication."""
        url = reverse('api:v1:auth-me')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_me_endpoint_authenticated(self, authenticated_client, test_user):
        """Test authenticated user can access /me endpoint."""
        url = reverse('api:v1:auth-me')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('username') == test_user.username or response.data.get('email') == test_user.email


class TestPasswordManagement:
    """Test cases for password management."""

    @pytest.mark.django_db
    def test_change_password_success(self, authenticated_client, test_user):
        """Test successful password change."""
        url = reverse('api:v1:auth-change-password')
        data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewSecurePass456!',
            'new_password_confirm': 'NewSecurePass456!'
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    @pytest.mark.django_db
    def test_change_password_wrong_old(self, authenticated_client):
        """Test password change with wrong old password fails."""
        url = reverse('api:v1:auth-change-password')
        data = {
            'old_password': 'WrongOldPass!',
            'new_password': 'NewSecurePass456!',
            'new_password_confirm': 'NewSecurePass456!'
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
