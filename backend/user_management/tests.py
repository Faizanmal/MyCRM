from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import UserProfile, Permission, AuditLog

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'sales_rep'
        }
    
    def test_create_user(self):
        """Test creating a new user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'sales_rep')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_str_method(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')
    
    def test_user_role_choices(self):
        """Test user role validation"""
        user = User.objects.create_user(**self.user_data)
        user.role = 'admin'
        user.save()
        self.assertEqual(user.role, 'admin')
    
    def test_user_default_role(self):
        """Test default role is sales_rep"""
        user = User.objects.create_user(
            username='defaultuser',
            email='default@example.com',
            password='pass123'
        )
        self.assertEqual(user.role, 'sales_rep')


class UserProfileTest(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_user_profile(self):
        """Test creating user profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            timezone='America/New_York'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.timezone, 'America/New_York')
    
    def test_user_profile_defaults(self):
        """Test default values in profile"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.timezone, 'UTC')
        self.assertEqual(profile.language, 'en')
        self.assertIsInstance(profile.notification_preferences, dict)


class PermissionTest(TestCase):
    """Test cases for Permission model"""
    
    def test_create_permission(self):
        """Test creating a permission"""
        permission = Permission.objects.create(
            name='View Contacts',
            codename='view_contacts',
            description='Can view contacts',
            module='contacts'
        )
        self.assertEqual(permission.name, 'View Contacts')
        self.assertEqual(permission.module, 'contacts')
    
    def test_permission_unique_codename(self):
        """Test that codename must be unique"""
        Permission.objects.create(
            name='View Contacts',
            codename='view_contacts',
            module='contacts'
        )
        with self.assertRaises(Exception):
            Permission.objects.create(
                name='View All Contacts',
                codename='view_contacts',
                module='contacts'
            )


class AuditLogTest(TestCase):
    """Test cases for AuditLog model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_audit_log(self):
        """Test creating an audit log entry"""
        log = AuditLog.objects.create(
            user=self.user,
            action='create',
            model_name='Contact',
            object_id='123',
            ip_address='127.0.0.1',
            details={'field': 'value'}
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'create')
        self.assertEqual(log.model_name, 'Contact')


class UserSecurityTest(TestCase):
    """Test cases for user security features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='secureuser',
            email='secure@example.com',
            password='securepass123'
        )
    
    def test_password_hashing(self):
        """Test that passwords are hashed"""
        self.assertNotEqual(self.user.password, 'securepass123')
        self.assertTrue(self.user.check_password('securepass123'))
    
    def test_two_factor_authentication(self):
        """Test 2FA fields"""
        self.user.two_factor_enabled = True
        self.user.two_factor_secret = 'test_secret'
        self.user.save()
        self.assertTrue(self.user.two_factor_enabled)
        self.assertEqual(self.user.two_factor_secret, 'test_secret')
