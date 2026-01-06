"""
Settings and RBAC Tests
Comprehensive test suite for user preferences, notification settings, export jobs, and RBAC
"""

from datetime import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .rbac_middleware import (
    Permissions,
    get_user_permissions,
    invalidate_user_permissions,
    user_has_all_permissions,
    user_has_any_permission,
    user_has_permission,
)
from .settings_models import (
    ExportJob,
    NotificationPreference,
    NotificationTypeSetting,
    UserPreference,
    UserRole,
    UserRoleAssignment,
)

User = get_user_model()


# ==================== Model Tests ====================

class UserPreferenceModelTest(TestCase):
    """Tests for UserPreference model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_preferences(self):
        """Test creating user preferences"""
        prefs = UserPreference.objects.create(user=self.user)

        self.assertEqual(prefs.theme, 'system')
        self.assertEqual(prefs.accent_color, '#3b82f6')
        self.assertEqual(prefs.font_size, 14)
        self.assertFalse(prefs.compact_mode)
        self.assertTrue(prefs.animations_enabled)

    def test_get_or_create_for_user(self):
        """Test get_or_create_for_user method"""
        prefs1 = UserPreference.get_or_create_for_user(self.user)
        prefs2 = UserPreference.get_or_create_for_user(self.user)

        self.assertEqual(prefs1.id, prefs2.id)

    def test_default_keyboard_shortcuts(self):
        """Test default keyboard shortcuts"""
        prefs = UserPreference.objects.create(user=self.user)
        shortcuts = prefs.get_default_keyboard_shortcuts()

        self.assertIn('search', shortcuts)
        self.assertIn('newContact', shortcuts)
        self.assertIn('newDeal', shortcuts)

    def test_dashboard_layout_json(self):
        """Test dashboard layout JSON field"""
        prefs = UserPreference.objects.create(
            user=self.user,
            dashboard_layout={'widgets': ['a', 'b', 'c']}
        )

        prefs.refresh_from_db()
        self.assertEqual(prefs.dashboard_layout['widgets'], ['a', 'b', 'c'])


class NotificationPreferenceModelTest(TestCase):
    """Tests for NotificationPreference model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_notification_preferences(self):
        """Test creating notification preferences"""
        prefs = NotificationPreference.objects.create(user=self.user)

        self.assertTrue(prefs.email_enabled)
        self.assertTrue(prefs.push_enabled)
        self.assertTrue(prefs.in_app_enabled)
        self.assertFalse(prefs.sms_enabled)
        self.assertFalse(prefs.quiet_hours_enabled)

    def test_quiet_hours_time_fields(self):
        """Test quiet hours time fields"""
        prefs = NotificationPreference.objects.create(
            user=self.user,
            quiet_hours_enabled=True,
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(8, 0),
            quiet_hours_days=['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        )

        prefs.refresh_from_db()
        self.assertEqual(prefs.quiet_hours_start.hour, 22)
        self.assertEqual(len(prefs.quiet_hours_days), 5)


class NotificationTypeSettingModelTest(TestCase):
    """Tests for NotificationTypeSetting model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.prefs = NotificationPreference.objects.create(user=self.user)

    def test_create_type_setting(self):
        """Test creating notification type setting"""
        setting = NotificationTypeSetting.objects.create(
            notification_preference=self.prefs,
            notification_type='deal_won',
            priority='high'
        )

        self.assertEqual(setting.notification_type, 'deal_won')
        self.assertEqual(setting.priority, 'high')
        self.assertEqual(setting.frequency, 'instant')

    def test_unique_constraint(self):
        """Test unique constraint on notification_preference + notification_type"""
        NotificationTypeSetting.objects.create(
            notification_preference=self.prefs,
            notification_type='deal_won'
        )

        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            NotificationTypeSetting.objects.create(
                notification_preference=self.prefs,
                notification_type='deal_won'
            )


class ExportJobModelTest(TestCase):
    """Tests for ExportJob model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_export_job(self):
        """Test creating export job"""
        job = ExportJob.objects.create(
            user=self.user,
            format='csv',
            entities=['contacts', 'deals'],
            date_range='month'
        )

        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.progress, 0)
        self.assertIsNone(job.file_path)

    def test_mark_processing(self):
        """Test marking job as processing"""
        job = ExportJob.objects.create(user=self.user, entities=['contacts'])
        job.mark_processing()

        self.assertEqual(job.status, 'processing')
        self.assertIsNotNone(job.started_at)

    def test_mark_completed(self):
        """Test marking job as completed"""
        job = ExportJob.objects.create(user=self.user, entities=['contacts'])
        job.mark_completed('/path/to/file.csv', 1024)

        self.assertEqual(job.status, 'completed')
        self.assertEqual(job.progress, 100)
        self.assertEqual(job.file_size, 1024)
        self.assertIsNotNone(job.completed_at)
        self.assertIsNotNone(job.expires_at)

    def test_mark_failed(self):
        """Test marking job as failed"""
        job = ExportJob.objects.create(user=self.user, entities=['contacts'])
        job.mark_failed('Some error occurred')

        self.assertEqual(job.status, 'failed')
        self.assertEqual(job.error_message, 'Some error occurred')


class UserRoleModelTest(TestCase):
    """Tests for UserRole model"""

    def test_create_role(self):
        """Test creating a role"""
        role = UserRole.objects.create(
            name='custom_role',
            display_name='Custom Role',
            level=2,
            permissions=['view_contacts', 'create_contacts']
        )

        self.assertEqual(role.name, 'custom_role')
        self.assertEqual(len(role.permissions), 2)

    def test_create_default_roles(self):
        """Test creating default system roles"""
        UserRole.create_default_roles()

        self.assertTrue(UserRole.objects.filter(name='admin').exists())
        self.assertTrue(UserRole.objects.filter(name='manager').exists())
        self.assertTrue(UserRole.objects.filter(name='sales_rep').exists())
        self.assertTrue(UserRole.objects.filter(name='viewer').exists())
        self.assertTrue(UserRole.objects.filter(name='guest').exists())

    def test_admin_role_permissions(self):
        """Test admin role has all core permissions"""
        UserRole.create_default_roles()
        admin_role = UserRole.objects.get(name='admin')

        self.assertIn('access_admin', admin_role.permissions)
        self.assertIn('view_admin_dashboard', admin_role.permissions)
        self.assertIn('manage_team', admin_role.permissions)


class UserRoleAssignmentModelTest(TestCase):
    """Tests for UserRoleAssignment model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        UserRole.create_default_roles()
        self.role = UserRole.objects.get(name='sales_rep')

    def test_assign_role(self):
        """Test assigning a role to user"""
        assignment = UserRoleAssignment.objects.create(
            user=self.user,
            role=self.role,
            assigned_by=self.admin
        )

        self.assertEqual(assignment.user, self.user)
        self.assertEqual(assignment.role, self.role)
        self.assertIsNotNone(assignment.assigned_at)


# ==================== RBAC Tests ====================

class RBACMiddlewareTest(TestCase):
    """Tests for RBAC middleware functions"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserRole.create_default_roles()
        cache.clear()

    def test_get_user_permissions_unauthenticated(self):
        """Test permissions for unauthenticated user"""
        permissions = get_user_permissions(None)
        self.assertEqual(permissions, set())

    def test_get_user_permissions_superuser(self):
        """Test superuser has all permissions"""
        superuser = User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='superpass123'
        )
        permissions = get_user_permissions(superuser)

        self.assertIn(Permissions.ACCESS_ADMIN, permissions)
        self.assertIn(Permissions.VIEW_DASHBOARD, permissions)

    def test_user_has_permission(self):
        """Test user_has_permission function"""
        role = UserRole.objects.get(name='sales_rep')
        UserRoleAssignment.objects.create(user=self.user, role=role)

        self.assertTrue(user_has_permission(self.user, 'view_contacts'))
        self.assertFalse(user_has_permission(self.user, 'access_admin'))

    def test_user_has_any_permission(self):
        """Test user_has_any_permission function"""
        role = UserRole.objects.get(name='viewer')
        UserRoleAssignment.objects.create(user=self.user, role=role)

        self.assertTrue(user_has_any_permission(self.user, ['view_contacts', 'create_contacts']))
        self.assertFalse(user_has_any_permission(self.user, ['delete_contacts', 'manage_team']))

    def test_user_has_all_permissions(self):
        """Test user_has_all_permissions function"""
        role = UserRole.objects.get(name='sales_rep')
        UserRoleAssignment.objects.create(user=self.user, role=role)

        self.assertTrue(user_has_all_permissions(self.user, ['view_contacts', 'view_deals']))
        self.assertFalse(user_has_all_permissions(self.user, ['view_contacts', 'delete_contacts']))

    def test_cache_invalidation(self):
        """Test permission cache invalidation"""
        role = UserRole.objects.get(name='viewer')
        UserRoleAssignment.objects.create(user=self.user, role=role)

        # Get permissions (adds to cache)
        get_user_permissions(self.user)

        # Invalidate cache
        invalidate_user_permissions(self.user.id)

        # Add new role
        manager_role = UserRole.objects.get(name='manager')
        UserRoleAssignment.objects.create(user=self.user, role=manager_role)

        # Get permissions again (should include new role)
        permissions2 = get_user_permissions(self.user)

        self.assertIn('manage_team', permissions2)


# ==================== API Tests ====================

class UserPreferenceAPITest(APITestCase):
    """Tests for UserPreference API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_preferences(self):
        """Test getting user preferences"""
        response = self.client.get('/api/v1/settings/preferences/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'system')

    def test_update_preferences(self):
        """Test updating user preferences"""
        response = self.client.patch('/api/v1/settings/preferences/me/', {
            'theme': 'dark',
            'compact_mode': True
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'dark')
        self.assertTrue(response.data['compact_mode'])

    def test_reset_preferences(self):
        """Test resetting preferences to defaults"""
        # First update
        self.client.patch('/api/v1/settings/preferences/me/', {'theme': 'dark'})

        # Then reset
        response = self.client.post('/api/v1/settings/preferences/reset/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'system')


class NotificationPreferenceAPITest(APITestCase):
    """Tests for NotificationPreference API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_notification_preferences(self):
        """Test getting notification preferences"""
        response = self.client.get('/api/v1/settings/notifications/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['email_enabled'])

    def test_update_channel(self):
        """Test updating notification channel"""
        response = self.client.patch('/api/v1/settings/notifications/channel/', {
            'channel': 'push',
            'enabled': False
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['enabled'])

    def test_update_quiet_hours(self):
        """Test updating quiet hours"""
        response = self.client.patch('/api/v1/settings/notifications/quiet-hours/', {
            'enabled': True,
            'start_time': '22:00',
            'end_time': '07:00',
            'days': ['Mon', 'Tue', 'Wed']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['enabled'])


class ExportJobAPITest(APITestCase):
    """Tests for ExportJob API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_export_job(self):
        """Test creating an export job"""
        response = self.client.post('/api/v1/settings/export/', {
            'format': 'csv',
            'entities': ['contacts', 'deals'],
            'date_range': 'month'
        })

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('id', response.data)

    def test_create_export_no_entities(self):
        """Test creating export without entities fails"""
        response = self.client.post('/api/v1/settings/export/', {
            'format': 'csv',
            'entities': []
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_export_history(self):
        """Test getting export history"""
        # Create some jobs
        ExportJob.objects.create(user=self.user, entities=['contacts'])
        ExportJob.objects.create(user=self.user, entities=['deals'])

        response = self.client.get('/api/v1/settings/export/history/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['exports']), 2)


class UserRoleAPITest(APITestCase):
    """Tests for UserRole API"""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()

    def test_list_roles(self):
        """Test listing roles"""
        self.client.force_authenticate(user=self.user)
        UserRole.create_default_roles()

        response = self.client.get('/api/v1/settings/roles/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 5)

    def test_initialize_roles_admin_only(self):
        """Test initializing roles requires admin"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/v1/settings/roles/initialize/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_initialize_roles_as_admin(self):
        """Test initializing roles as admin"""
        self.client.force_authenticate(user=self.admin)

        response = self.client.post('/api/v1/settings/roles/initialize/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('roles', response.data)


class PermissionsAPITest(APITestCase):
    """Tests for permissions API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserRole.create_default_roles()
        role = UserRole.objects.get(name='sales_rep')
        UserRoleAssignment.objects.create(user=self.user, role=role)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        cache.clear()

    def test_get_my_permissions(self):
        """Test getting current user's permissions"""
        response = self.client.get('/api/v1/settings/permissions/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('permissions', response.data)
        self.assertIn('view_contacts', response.data['permissions'])

    def test_check_permission_granted(self):
        """Test checking a granted permission"""
        response = self.client.post('/api/v1/settings/permissions/check/', {
            'permission': 'view_contacts'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_permission'])

    def test_check_permission_denied(self):
        """Test checking a denied permission"""
        response = self.client.post('/api/v1/settings/permissions/check/', {
            'permission': 'access_admin'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_permission'])


class AnalyticsDashboardAPITest(APITestCase):
    """Tests for Analytics Dashboard API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_analytics_dashboard(self):
        """Test getting analytics dashboard data"""
        response = self.client.get('/api/v1/settings/analytics/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overview', response.data)
        self.assertIn('revenue_by_month', response.data)
        self.assertIn('team_performance', response.data)

    def test_analytics_with_time_range(self):
        """Test analytics with different time ranges"""
        for time_range in ['week', 'month', 'quarter', 'year']:
            response = self.client.get(f'/api/v1/settings/analytics/dashboard/?range={time_range}')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('overview', response.data)
