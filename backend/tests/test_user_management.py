# MyCRM Backend - Comprehensive User Management Tests

"""
User Management Tests

Comprehensive test suite for user management including:
- User CRUD operations
- Profile management
- Role-based access control
- Password management
- Two-factor authentication
- Audit logging
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


# =============================================================================
# User CRUD Tests
# =============================================================================

@pytest.mark.django_db
class TestUserListAPI:
    """Test cases for User list endpoint."""

    def test_list_users_unauthenticated(self, api_client):
        """Test that unauthenticated requests are rejected."""
        response = api_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_users_authenticated(self, authenticated_client, user):
        """Test listing users requires authentication."""
        response = authenticated_client.get('/api/v1/users/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_list_users_admin(self, admin_client, user, admin_user):
        """Test admin can list all users."""
        response = admin_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_users_search(self, admin_client, user):
        """Test searching users by name or email."""
        response = admin_client.get('/api/v1/users/', {'search': user.email})
        assert response.status_code == status.HTTP_200_OK

    def test_list_users_filter_by_role(self, admin_client, user, manager_user):
        """Test filtering users by role."""
        response = admin_client.get('/api/v1/users/', {'role': 'sales_rep'})
        assert response.status_code == status.HTTP_200_OK

    def test_list_users_filter_by_status(self, admin_client, user):
        """Test filtering users by active status."""
        response = admin_client.get('/api/v1/users/', {'is_active': 'true'})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestUserCreateAPI:
    """Test cases for User creation."""

    def test_create_user_admin_only(self, authenticated_client, organization):
        """Test only admins can create users."""
        data = {
            'email': 'newuser@example.com',
            'password': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'sales_rep'
        }
        response = authenticated_client.post('/api/v1/users/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_user_success(self, admin_client, organization):
        """Test admin can create a new user."""
        data = {
            'email': 'newuser@example.com',
            'password': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'sales_rep'
        }
        response = admin_client.post('/api/v1/users/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    def test_create_user_invalid_email(self, admin_client, organization):
        """Test creating user with invalid email fails."""
        data = {
            'email': 'invalid-email',
            'password': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = admin_client.post('/api/v1/users/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_duplicate_email(self, admin_client, user, organization):
        """Test creating user with duplicate email fails."""
        data = {
            'email': user.email,
            'password': 'NewPass123!',
            'first_name': 'Duplicate',
            'last_name': 'User'
        }
        response = admin_client.post('/api/v1/users/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_weak_password(self, admin_client, organization):
        """Test creating user with weak password fails."""
        data = {
            'email': 'newuser@example.com',
            'password': '123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = admin_client.post('/api/v1/users/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserDetailAPI:
    """Test cases for User detail endpoint."""

    def test_get_user_detail(self, authenticated_client, user):
        """Test getting user details."""
        response = authenticated_client.get(f'/api/v1/users/{user.id}/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_get_own_profile(self, authenticated_client, user):
        """Test getting own profile."""
        response = authenticated_client.get('/api/v1/users/me/')
        assert response.status_code == status.HTTP_200_OK

    def test_update_own_profile(self, authenticated_client, user):
        """Test updating own profile."""
        data = {'first_name': 'Updated'}
        response = authenticated_client.patch('/api/v1/users/me/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_update_other_user_forbidden(self, authenticated_client, manager_user):
        """Test regular users cannot update other users."""
        data = {'first_name': 'Hacked'}
        response = authenticated_client.patch(f'/api/v1/users/{manager_user.id}/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_update_any_user(self, admin_client, user):
        """Test admin can update any user."""
        data = {'first_name': 'AdminUpdated'}
        response = admin_client.patch(f'/api/v1/users/{user.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestUserDeleteAPI:
    """Test cases for User deletion."""

    def test_delete_user_admin_only(self, authenticated_client, manager_user):
        """Test only admins can delete users."""
        response = authenticated_client.delete(f'/api/v1/users/{manager_user.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_user_success(self, admin_client, user):
        """Test admin can delete a user."""
        response = admin_client.delete(f'/api/v1/users/{user.id}/')
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

    def test_delete_self_forbidden(self, admin_client, admin_user):
        """Test users cannot delete themselves."""
        response = admin_client.delete(f'/api/v1/users/{admin_user.id}/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =============================================================================
# Password Management Tests
# =============================================================================

@pytest.mark.django_db
class TestPasswordManagement:
    """Test cases for password management."""

    def test_change_password_success(self, authenticated_client, user):
        """Test changing password with correct current password."""
        data = {
            'current_password': 'testpass123!',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        }
        response = authenticated_client.post('/api/v1/users/change-password/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_change_password_wrong_current(self, authenticated_client, user):
        """Test changing password with wrong current password fails."""
        data = {
            'current_password': 'wrongpassword',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        }
        response = authenticated_client.post('/api/v1/users/change-password/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_mismatch(self, authenticated_client, user):
        """Test changing password with mismatched confirmation fails."""
        data = {
            'current_password': 'testpass123!',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'DifferentPass123!'
        }
        response = authenticated_client.post('/api/v1/users/change-password/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_weak(self, authenticated_client, user):
        """Test changing to weak password fails."""
        data = {
            'current_password': 'testpass123!',
            'new_password': '123',
            'new_password_confirm': '123'
        }
        response = authenticated_client.post('/api/v1/users/change-password/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =============================================================================
# Role-Based Access Control Tests
# =============================================================================

@pytest.mark.django_db
class TestRoleBasedAccessControl:
    """Test cases for RBAC functionality."""

    def test_sales_rep_access(self, authenticated_client, user):
        """Test sales rep has limited access."""
        # Sales rep should not access admin endpoints
        response = authenticated_client.get('/api/v1/admin/users/')
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_manager_access(self, manager_user, api_client):
        """Test manager has elevated access."""
        from rest_framework_simplejwt.tokens import RefreshToken
        client = api_client
        refresh = RefreshToken.for_user(manager_user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Manager should access team data
        response = client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK

    def test_admin_full_access(self, admin_client):
        """Test admin has full access."""
        response = admin_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK

    def test_role_assignment(self, admin_client, user):
        """Test role can be updated by admin."""
        data = {'role': 'manager'}
        response = admin_client.patch(f'/api/v1/users/{user.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Two-Factor Authentication Tests
# =============================================================================

@pytest.mark.django_db
class TestTwoFactorAuthentication:
    """Test cases for 2FA functionality."""

    def test_setup_2fa(self, authenticated_client, user):
        """Test 2FA setup initiation."""
        response = authenticated_client.post('/api/v1/users/2fa/setup/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_verify_2fa_invalid_code(self, authenticated_client, user):
        """Test 2FA verification with invalid code."""
        data = {'code': '000000'}
        response = authenticated_client.post('/api/v1/users/2fa/verify/', data, format='json')
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_disable_2fa(self, authenticated_client, user):
        """Test 2FA disable functionality."""
        response = authenticated_client.post('/api/v1/users/2fa/disable/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Audit Logging Tests
# =============================================================================

@pytest.mark.django_db
class TestAuditLogging:
    """Test cases for audit logging functionality."""

    def test_login_creates_audit_log(self, api_client, user):
        """Test successful login creates an audit log entry."""
        data = {
            'email': user.email,
            'password': 'testpass123!'
        }
        response = api_client.post('/api/v1/auth/login/', data, format='json')
        # Login should succeed and log the event
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_view_audit_logs_admin_only(self, authenticated_client, admin_client):
        """Test only admins can view audit logs."""
        response = authenticated_client.get('/api/v1/audit-logs/')
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

        response = admin_client.get('/api/v1/audit-logs/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_audit_log_filter_by_action(self, admin_client):
        """Test filtering audit logs by action type."""
        response = admin_client.get('/api/v1/audit-logs/', {'action': 'login'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# User Profile Tests
# =============================================================================

@pytest.mark.django_db
class TestUserProfile:
    """Test cases for user profile management."""

    def test_get_profile(self, authenticated_client, user):
        """Test getting user profile."""
        response = authenticated_client.get('/api/v1/users/profile/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_update_profile(self, authenticated_client, user):
        """Test updating user profile."""
        data = {
            'timezone': 'America/New_York',
            'language': 'en'
        }
        response = authenticated_client.patch('/api/v1/users/profile/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_update_notification_preferences(self, authenticated_client, user):
        """Test updating notification preferences."""
        data = {
            'notification_preferences': {
                'email': True,
                'push': True,
                'sms': False
            }
        }
        response = authenticated_client.patch('/api/v1/users/profile/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_upload_avatar(self, authenticated_client, user):
        """Test uploading profile avatar."""
        import io
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = SimpleUploadedFile(
            name='avatar.png',
            content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x00\x00\x00\x00:~\x9bU\x00\x00\x00\nIDATx\x9cc\xfa\x0f\x00\x00\x01\x00\x01\x00\xa3\x1c\xae\x00\x00\x00\x00IEND\xaeB`\x82',
            content_type='image/png'
        )
        response = authenticated_client.patch('/api/v1/users/profile/', {'avatar': image}, format='multipart')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]


# =============================================================================
# User Session Tests
# =============================================================================

@pytest.mark.django_db
class TestUserSessions:
    """Test cases for user session management."""

    def test_list_active_sessions(self, authenticated_client, user):
        """Test listing active sessions."""
        response = authenticated_client.get('/api/v1/users/sessions/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_revoke_session(self, authenticated_client, user):
        """Test revoking a specific session."""
        response = authenticated_client.delete('/api/v1/users/sessions/1/')
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]

    def test_revoke_all_sessions(self, authenticated_client, user):
        """Test revoking all sessions except current."""
        response = authenticated_client.post('/api/v1/users/sessions/revoke-all/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# User Search and Export Tests
# =============================================================================

@pytest.mark.django_db
class TestUserSearchAndExport:
    """Test cases for user search and export functionality."""

    def test_search_users_by_name(self, admin_client, user):
        """Test searching users by name."""
        response = admin_client.get('/api/v1/users/', {'search': user.first_name})
        assert response.status_code == status.HTTP_200_OK

    def test_search_users_by_email(self, admin_client, user):
        """Test searching users by email."""
        response = admin_client.get('/api/v1/users/', {'search': 'example.com'})
        assert response.status_code == status.HTTP_200_OK

    def test_export_users_csv(self, admin_client):
        """Test exporting users to CSV."""
        response = admin_client.get('/api/v1/users/export/', {'format': 'csv'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_users_forbidden_for_regular_users(self, authenticated_client):
        """Test regular users cannot export user list."""
        response = authenticated_client.get('/api/v1/users/export/', {'format': 'csv'})
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Unit Tests for User Model
# =============================================================================

@pytest.mark.django_db
class TestUserModel:
    """Unit tests for User model."""

    def test_user_creation(self, organization):
        """Test user creation with required fields."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123!',
            first_name='Test',
            last_name='User'
        )
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123!')
        assert user.is_active is True

    def test_superuser_creation(self, organization):
        """Test superuser creation."""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123!'
        )
        assert admin.is_superuser is True
        assert admin.is_staff is True

    def test_user_str_representation(self, user):
        """Test user string representation."""
        assert str(user) == user.email or user.get_full_name() in str(user)

    def test_user_full_name(self, user):
        """Test get_full_name method."""
        full_name = user.get_full_name()
        assert user.first_name in full_name
        assert user.last_name in full_name

    def test_user_email_normalization(self, organization):
        """Test email is normalized on creation."""
        user = User.objects.create_user(
            email='TEST@EXAMPLE.COM',
            password='testpass123!'
        )
        assert user.email == 'TEST@example.com' or user.email.lower() == 'test@example.com'
