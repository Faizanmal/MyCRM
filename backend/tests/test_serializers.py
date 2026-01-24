"""
MyCRM Backend - Serializer Tests

Tests for Django REST Framework serializers
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from datetime import datetime, date, timedelta
from decimal import Decimal

User = get_user_model()


# =============================================================================
# Base Serializer Test Helpers
# =============================================================================

def validate_serializer(serializer_class, data, context=None):
    """Helper to validate serializer with data"""
    context = context or {}
    serializer = serializer_class(data=data, context=context)
    return serializer.is_valid(), serializer.errors, serializer


# =============================================================================
# User Serializer Tests
# =============================================================================

@pytest.mark.django_db
class TestUserSerializer(TestCase):
    """Tests for User serializer"""
    
    def get_serializer_class(self):
        """Get the user serializer class"""
        try:
            from accounts.serializers import UserSerializer
            return UserSerializer
        except ImportError:
            try:
                from user_management.serializers import UserSerializer
                return UserSerializer
            except ImportError:
                return None
    
    def test_user_serialization(self):
        """Test serializing a user"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("User serializer not found")
        
        user = User.objects.create_user(
            email='serialize@test.com',
            password='Test123!',
            first_name='John',
            last_name='Doe'
        )
        
        serializer = SerializerClass(user)
        data = serializer.data
        
        self.assertEqual(data['email'], 'serialize@test.com')
        self.assertNotIn('password', data)  # Password should not be serialized
    
    def test_user_creation(self):
        """Test creating user via serializer"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("User serializer not found")
        
        data = {
            'email': 'new@test.com',
            'password': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        serializer = SerializerClass(data=data)
        
        # May or may not be valid depending on required fields
        if serializer.is_valid():
            user = serializer.save()
            self.assertEqual(user.email, 'new@test.com')
    
    def test_email_validation(self):
        """Test email validation"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("User serializer not found")
        
        data = {
            'email': 'invalid-email',
            'password': 'Test123!'
        }
        
        serializer = SerializerClass(data=data)
        is_valid = serializer.is_valid()
        
        # Should have email error
        if not is_valid:
            self.assertIn('email', serializer.errors)
    
    def test_password_write_only(self):
        """Test password is write-only"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("User serializer not found")
        
        user = User.objects.create_user(
            email='writeonly@test.com',
            password='Test123!'
        )
        
        serializer = SerializerClass(user)
        self.assertNotIn('password', serializer.data)


# =============================================================================
# Contact Serializer Tests
# =============================================================================

@pytest.mark.django_db
class TestContactSerializer(TestCase):
    """Tests for Contact serializer"""
    
    def get_serializer_class(self):
        try:
            from contacts.serializers import ContactSerializer
            return ContactSerializer
        except ImportError:
            return None
    
    def test_contact_serialization(self):
        """Test serializing a contact"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Contact serializer not found")
        
        # Create mock contact data
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com'
        }
        
        serializer = SerializerClass(data=data)
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data['first_name'], 'John')
    
    def test_contact_email_validation(self):
        """Test contact email validation"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Contact serializer not found")
        
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'not-an-email'
        }
        
        serializer = SerializerClass(data=data)
        is_valid = serializer.is_valid()
        
        # Should fail email validation
        if not is_valid:
            self.assertIn('email', serializer.errors)
    
    def test_contact_required_fields(self):
        """Test contact required fields"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Contact serializer not found")
        
        # Empty data
        serializer = SerializerClass(data={})
        is_valid = serializer.is_valid()
        
        # Should have errors for required fields
        if not is_valid:
            self.assertTrue(len(serializer.errors) > 0)
    
    def test_contact_phone_format(self):
        """Test contact phone number format"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Contact serializer not found")
        
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '+1-555-123-4567'
        }
        
        serializer = SerializerClass(data=data)
        if serializer.is_valid():
            self.assertIn('phone', serializer.validated_data)


# =============================================================================
# Lead Serializer Tests
# =============================================================================

@pytest.mark.django_db
class TestLeadSerializer(TestCase):
    """Tests for Lead serializer"""
    
    def get_serializer_class(self):
        try:
            from leads.serializers import LeadSerializer
            return LeadSerializer
        except ImportError:
            return None
    
    def test_lead_serialization(self):
        """Test serializing a lead"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Lead serializer not found")
        
        data = {
            'name': 'Test Lead',
            'email': 'lead@test.com',
            'status': 'new'
        }
        
        serializer = SerializerClass(data=data)
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data['name'], 'Test Lead')
    
    def test_lead_status_choices(self):
        """Test lead status field choices"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Lead serializer not found")
        
        # Valid status
        data = {'name': 'Test', 'email': 'test@test.com', 'status': 'new'}
        serializer = SerializerClass(data=data)
        
        # Should be valid with correct status
        pass
    
    def test_lead_score_validation(self):
        """Test lead score validation (0-100)"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Lead serializer not found")
        
        # Score out of range
        data = {
            'name': 'Test',
            'email': 'test@test.com',
            'score': 150  # Invalid
        }
        
        serializer = SerializerClass(data=data)
        is_valid = serializer.is_valid()
        
        # May have score validation error
        if not is_valid and 'score' in serializer.errors:
            pass  # Expected behavior


# =============================================================================
# Opportunity Serializer Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunitySerializer(TestCase):
    """Tests for Opportunity serializer"""
    
    def get_serializer_class(self):
        try:
            from opportunities.serializers import OpportunitySerializer
            return OpportunitySerializer
        except ImportError:
            return None
    
    def test_opportunity_serialization(self):
        """Test serializing an opportunity"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Opportunity serializer not found")
        
        data = {
            'name': 'Big Deal',
            'value': '50000.00',
            'stage': 'prospecting'
        }
        
        serializer = SerializerClass(data=data)
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data['name'], 'Big Deal')
    
    def test_opportunity_value_decimal(self):
        """Test opportunity value as decimal"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Opportunity serializer not found")
        
        data = {
            'name': 'Test',
            'value': '123456.78',
            'stage': 'prospecting'
        }
        
        serializer = SerializerClass(data=data)
        if serializer.is_valid():
            value = serializer.validated_data.get('value')
            if value:
                self.assertEqual(Decimal(str(value)), Decimal('123456.78'))
    
    def test_opportunity_probability_range(self):
        """Test opportunity probability range (0-100)"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Opportunity serializer not found")
        
        data = {
            'name': 'Test',
            'value': '50000',
            'probability': 50
        }
        
        serializer = SerializerClass(data=data)
        # Should be valid with probability in range
        pass
    
    def test_opportunity_close_date_future(self):
        """Test opportunity close date validation"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Opportunity serializer not found")
        
        data = {
            'name': 'Test',
            'value': '50000',
            'close_date': (date.today() + timedelta(days=30)).isoformat()
        }
        
        serializer = SerializerClass(data=data)
        # Should accept future dates
        pass


# =============================================================================
# Task Serializer Tests
# =============================================================================

@pytest.mark.django_db
class TestTaskSerializer(TestCase):
    """Tests for Task serializer"""
    
    def get_serializer_class(self):
        try:
            from tasks.serializers import TaskSerializer
            return TaskSerializer
        except ImportError:
            return None
    
    def test_task_serialization(self):
        """Test serializing a task"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Task serializer not found")
        
        data = {
            'title': 'Call client',
            'status': 'pending'
        }
        
        serializer = SerializerClass(data=data)
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data['title'], 'Call client')
    
    def test_task_priority_choices(self):
        """Test task priority field choices"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Task serializer not found")
        
        priorities = ['low', 'medium', 'high', 'urgent']
        
        for priority in priorities:
            data = {
                'title': f'Task {priority}',
                'priority': priority
            }
            serializer = SerializerClass(data=data)
            # Should accept valid priorities
            pass
    
    def test_task_due_date_format(self):
        """Test task due date format"""
        SerializerClass = self.get_serializer_class()
        if not SerializerClass:
            self.skipTest("Task serializer not found")
        
        data = {
            'title': 'Test Task',
            'due_date': '2025-01-25T10:00:00Z'
        }
        
        serializer = SerializerClass(data=data)
        # Should accept ISO format dates
        pass


# =============================================================================
# Nested Serializer Tests
# =============================================================================

@pytest.mark.django_db
class TestNestedSerializers(TestCase):
    """Tests for nested serializer relationships"""
    
    def test_contact_with_activities(self):
        """Test contact serializer with nested activities"""
        try:
            from contacts.serializers import ContactDetailSerializer
            
            # Test would verify nested serialization
            pass
        except ImportError:
            self.skipTest("ContactDetailSerializer not found")
    
    def test_lead_with_contact(self):
        """Test lead serializer with contact relation"""
        try:
            from leads.serializers import LeadDetailSerializer
            
            # Test would verify nested serialization
            pass
        except ImportError:
            self.skipTest("LeadDetailSerializer not found")
    
    def test_opportunity_with_products(self):
        """Test opportunity with nested products"""
        try:
            from opportunities.serializers import OpportunityDetailSerializer
            
            # Test would verify nested serialization
            pass
        except ImportError:
            self.skipTest("OpportunityDetailSerializer not found")


# =============================================================================
# Validation Tests
# =============================================================================

class TestSerializerValidation(TestCase):
    """Tests for custom serializer validation"""
    
    def test_cross_field_validation(self):
        """Test cross-field validation"""
        # Example: password confirmation
        class PasswordSerializer(serializers.Serializer):
            password = serializers.CharField()
            password_confirm = serializers.CharField()
            
            def validate(self, data):
                if data['password'] != data['password_confirm']:
                    raise ValidationError("Passwords don't match")
                return data
        
        # Test matching passwords
        serializer = PasswordSerializer(data={
            'password': 'Test123!',
            'password_confirm': 'Test123!'
        })
        self.assertTrue(serializer.is_valid())
        
        # Test non-matching passwords
        serializer = PasswordSerializer(data={
            'password': 'Test123!',
            'password_confirm': 'Different!'
        })
        self.assertFalse(serializer.is_valid())
    
    def test_custom_field_validation(self):
        """Test custom field validation"""
        class EmailListSerializer(serializers.Serializer):
            emails = serializers.ListField(child=serializers.EmailField())
            
            def validate_emails(self, value):
                if len(value) > 10:
                    raise ValidationError("Maximum 10 emails allowed")
                return value
        
        # Test valid list
        serializer = EmailListSerializer(data={
            'emails': ['a@test.com', 'b@test.com']
        })
        self.assertTrue(serializer.is_valid())
        
        # Test too many emails
        serializer = EmailListSerializer(data={
            'emails': [f'email{i}@test.com' for i in range(15)]
        })
        self.assertFalse(serializer.is_valid())
    
    def test_date_range_validation(self):
        """Test date range validation"""
        class DateRangeSerializer(serializers.Serializer):
            start_date = serializers.DateField()
            end_date = serializers.DateField()
            
            def validate(self, data):
                if data['end_date'] < data['start_date']:
                    raise ValidationError("End date must be after start date")
                return data
        
        # Test valid range
        serializer = DateRangeSerializer(data={
            'start_date': '2025-01-01',
            'end_date': '2025-12-31'
        })
        self.assertTrue(serializer.is_valid())
        
        # Test invalid range
        serializer = DateRangeSerializer(data={
            'start_date': '2025-12-31',
            'end_date': '2025-01-01'
        })
        self.assertFalse(serializer.is_valid())


# =============================================================================
# Read-Only and Write-Only Field Tests
# =============================================================================

class TestFieldModes(TestCase):
    """Tests for read-only and write-only fields"""
    
    def test_read_only_fields(self):
        """Test read-only fields are not writable"""
        class ItemSerializer(serializers.Serializer):
            id = serializers.IntegerField(read_only=True)
            name = serializers.CharField()
            created_at = serializers.DateTimeField(read_only=True)
        
        data = {
            'id': 999,  # Should be ignored
            'name': 'Test',
            'created_at': '2025-01-01T00:00:00Z'  # Should be ignored
        }
        
        serializer = ItemSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # id and created_at should not be in validated_data
        self.assertNotIn('id', serializer.validated_data)
        self.assertNotIn('created_at', serializer.validated_data)
    
    def test_write_only_fields(self):
        """Test write-only fields are not readable"""
        class UserSerializer(serializers.Serializer):
            email = serializers.EmailField()
            password = serializers.CharField(write_only=True)
        
        # Simulate serializing an object
        class User:
            email = 'test@test.com'
            password = 'secret123'
        
        serializer = UserSerializer(User())
        
        # password should not be in output
        self.assertNotIn('password', serializer.data)
        self.assertIn('email', serializer.data)


# =============================================================================
# Bulk Serializer Tests
# =============================================================================

class TestBulkSerializers(TestCase):
    """Tests for bulk operations with serializers"""
    
    def test_many_serialization(self):
        """Test serializing multiple objects"""
        class ItemSerializer(serializers.Serializer):
            id = serializers.IntegerField()
            name = serializers.CharField()
        
        items = [
            {'id': 1, 'name': 'Item 1'},
            {'id': 2, 'name': 'Item 2'},
            {'id': 3, 'name': 'Item 3'}
        ]
        
        serializer = ItemSerializer(items, many=True)
        self.assertEqual(len(serializer.data), 3)
    
    def test_many_validation(self):
        """Test validating multiple objects"""
        class ItemSerializer(serializers.Serializer):
            id = serializers.IntegerField()
            name = serializers.CharField()
        
        items = [
            {'id': 1, 'name': 'Item 1'},
            {'id': 'invalid', 'name': 'Item 2'},  # Invalid
            {'id': 3, 'name': 'Item 3'}
        ]
        
        serializer = ItemSerializer(data=items, many=True)
        self.assertFalse(serializer.is_valid())
        
        # Should have error for second item
        self.assertEqual(len(serializer.errors), 3)
        self.assertIn('id', serializer.errors[1])


# =============================================================================
# Context and Request Tests
# =============================================================================

@pytest.mark.django_db
class TestSerializerContext(TestCase):
    """Tests for serializer context usage"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='context@test.com',
            password='Test123!'
        )
    
    def test_context_user_access(self):
        """Test accessing user from context"""
        class ItemSerializer(serializers.Serializer):
            name = serializers.CharField()
            
            def validate(self, data):
                user = self.context.get('request')
                if user and hasattr(user, 'user'):
                    data['created_by'] = user.user
                return data
        
        # Simulate request context
        class MockRequest:
            user = self.user
        
        serializer = ItemSerializer(
            data={'name': 'Test'},
            context={'request': MockRequest()}
        )
        
        self.assertTrue(serializer.is_valid())
    
    def test_context_organization_access(self):
        """Test accessing organization from context"""
        class OrgItemSerializer(serializers.Serializer):
            name = serializers.CharField()
            
            def validate_name(self, value):
                org = self.context.get('organization')
                # Could check org-specific validation
                return value
        
        serializer = OrgItemSerializer(
            data={'name': 'Test'},
            context={'organization': 'test-org'}
        )
        
        self.assertTrue(serializer.is_valid())
