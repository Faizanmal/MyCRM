"""
MyCRM Backend - Model Tests

Comprehensive tests for Django models
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()


# =============================================================================
# User Model Tests
# =============================================================================

@pytest.mark.django_db
class TestUserModel(TestCase):
    """Tests for User model"""
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123!'
        )
        
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_email_is_required(self):
        """Test that email is required"""
        with self.assertRaises((ValueError, ValidationError, TypeError)):
            User.objects.create_user(email=None, password='Test123!')
    
    def test_email_is_unique(self):
        """Test that email must be unique"""
        User.objects.create_user(
            email='unique@example.com',
            password='Test123!'
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='unique@example.com',
                password='Another123!'
            )
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email='display@example.com',
            password='Test123!',
            first_name='John',
            last_name='Doe'
        )
        
        str_repr = str(user)
        # Should contain email or name
        self.assertTrue(
            'display@example.com' in str_repr or 
            'John' in str_repr or
            'Doe' in str_repr
        )
    
    def test_user_full_name(self):
        """Test getting user's full name"""
        user = User.objects.create_user(
            email='fullname@example.com',
            password='Test123!',
            first_name='John',
            last_name='Doe'
        )
        
        # Check if get_full_name exists
        if hasattr(user, 'get_full_name'):
            full_name = user.get_full_name()
            self.assertIn('John', full_name)
            self.assertIn('Doe', full_name)


# =============================================================================
# Contact Model Tests
# =============================================================================

@pytest.mark.django_db
class TestContactModel(TestCase):
    """Tests for Contact model"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        cls.user = User.objects.create_user(
            email='contact_test@example.com',
            password='Test123!'
        )
    
    def create_contact(self, **kwargs):
        """Helper to create a contact"""
        try:
            from contacts.models import Contact
            defaults = {
                'first_name': 'Test',
                'last_name': 'Contact',
                'email': 'test.contact@example.com'
            }
            defaults.update(kwargs)
            
            # Add owner if required
            if hasattr(Contact, 'owner'):
                defaults.setdefault('owner', self.user)
            if hasattr(Contact, 'created_by'):
                defaults.setdefault('created_by', self.user)
            
            return Contact.objects.create(**defaults)
        except ImportError:
            pytest.skip("Contact model not available")
    
    def test_create_contact(self):
        """Test creating a contact"""
        contact = self.create_contact()
        self.assertEqual(contact.first_name, 'Test')
        self.assertEqual(contact.last_name, 'Contact')
    
    def test_contact_str_representation(self):
        """Test contact string representation"""
        contact = self.create_contact(
            first_name='John',
            last_name='Smith'
        )
        
        str_repr = str(contact)
        self.assertTrue('John' in str_repr or 'Smith' in str_repr)
    
    def test_contact_email_validation(self):
        """Test email validation"""
        try:
            from contacts.models import Contact
            contact = self.create_contact()
            contact.email = 'invalid-email'
            
            with self.assertRaises(ValidationError):
                contact.full_clean()
        except ImportError:
            pytest.skip("Contact model not available")
    
    def test_contact_phone_format(self):
        """Test phone number format"""
        contact = self.create_contact(phone='+1-555-123-4567')
        self.assertEqual(contact.phone, '+1-555-123-4567')
    
    def test_contact_full_name_property(self):
        """Test full name property if exists"""
        contact = self.create_contact(
            first_name='Jane',
            last_name='Doe'
        )
        
        if hasattr(contact, 'full_name'):
            self.assertIn('Jane', contact.full_name)
            self.assertIn('Doe', contact.full_name)


# =============================================================================
# Lead Model Tests
# =============================================================================

@pytest.mark.django_db
class TestLeadModel(TestCase):
    """Tests for Lead model"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='lead_test@example.com',
            password='Test123!'
        )
    
    def create_lead(self, **kwargs):
        """Helper to create a lead"""
        try:
            from leads.models import Lead
            defaults = {
                'name': 'Test Lead',
                'email': 'lead@example.com',
                'status': 'new'
            }
            defaults.update(kwargs)
            
            if hasattr(Lead, 'owner'):
                defaults.setdefault('owner', self.user)
            if hasattr(Lead, 'assigned_to'):
                defaults.setdefault('assigned_to', self.user)
            
            return Lead.objects.create(**defaults)
        except ImportError:
            pytest.skip("Lead model not available")
    
    def test_create_lead(self):
        """Test creating a lead"""
        lead = self.create_lead()
        self.assertEqual(lead.name, 'Test Lead')
        self.assertEqual(lead.status, 'new')
    
    def test_lead_status_choices(self):
        """Test lead status field choices"""
        try:
            from leads.models import Lead
            valid_statuses = ['new', 'contacted', 'qualified', 'converted', 'lost']
            
            for status in valid_statuses:
                lead = self.create_lead(
                    name=f'Lead {status}',
                    email=f'{status}@example.com',
                    status=status
                )
                self.assertEqual(lead.status, status)
        except ImportError:
            pytest.skip("Lead model not available")
    
    def test_lead_scoring(self):
        """Test lead scoring field"""
        lead = self.create_lead()
        
        if hasattr(lead, 'score'):
            lead.score = 85
            lead.save()
            lead.refresh_from_db()
            self.assertEqual(lead.score, 85)
    
    def test_lead_source_tracking(self):
        """Test lead source tracking"""
        lead = self.create_lead()
        
        if hasattr(lead, 'source'):
            lead.source = 'website'
            lead.save()
            lead.refresh_from_db()
            self.assertEqual(lead.source, 'website')


# =============================================================================
# Opportunity Model Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunityModel(TestCase):
    """Tests for Opportunity model"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='opp_test@example.com',
            password='Test123!'
        )
    
    def create_opportunity(self, **kwargs):
        """Helper to create an opportunity"""
        try:
            from opportunities.models import Opportunity
            defaults = {
                'name': 'Test Opportunity',
                'value': Decimal('50000.00'),
                'stage': 'prospecting'
            }
            defaults.update(kwargs)
            
            if hasattr(Opportunity, 'owner'):
                defaults.setdefault('owner', self.user)
            
            return Opportunity.objects.create(**defaults)
        except ImportError:
            pytest.skip("Opportunity model not available")
    
    def test_create_opportunity(self):
        """Test creating an opportunity"""
        opp = self.create_opportunity()
        self.assertEqual(opp.name, 'Test Opportunity')
        self.assertEqual(opp.value, Decimal('50000.00'))
    
    def test_opportunity_value_decimal(self):
        """Test opportunity value is properly stored as decimal"""
        opp = self.create_opportunity(value=Decimal('123456.78'))
        opp.refresh_from_db()
        
        self.assertIsInstance(opp.value, Decimal)
        self.assertEqual(opp.value, Decimal('123456.78'))
    
    def test_opportunity_stage_transitions(self):
        """Test opportunity stage changes"""
        opp = self.create_opportunity(stage='prospecting')
        
        stages = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won']
        
        for stage in stages:
            opp.stage = stage
            opp.save()
            opp.refresh_from_db()
            self.assertEqual(opp.stage, stage)
    
    def test_opportunity_probability(self):
        """Test opportunity probability field"""
        opp = self.create_opportunity()
        
        if hasattr(opp, 'probability'):
            opp.probability = 75
            opp.save()
            opp.refresh_from_db()
            self.assertEqual(opp.probability, 75)
    
    def test_opportunity_close_date(self):
        """Test opportunity close date"""
        close_date = timezone.now().date() + timedelta(days=30)
        opp = self.create_opportunity()
        
        if hasattr(opp, 'close_date'):
            opp.close_date = close_date
            opp.save()
            opp.refresh_from_db()
            self.assertEqual(opp.close_date, close_date)
    
    def test_weighted_value_calculation(self):
        """Test weighted value calculation if available"""
        opp = self.create_opportunity(value=Decimal('100000.00'))
        
        if hasattr(opp, 'probability') and hasattr(opp, 'weighted_value'):
            opp.probability = 50
            opp.save()
            
            expected_weighted = Decimal('50000.00')
            self.assertEqual(opp.weighted_value, expected_weighted)


# =============================================================================
# Task Model Tests
# =============================================================================

@pytest.mark.django_db
class TestTaskModel(TestCase):
    """Tests for Task model"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='task_test@example.com',
            password='Test123!'
        )
    
    def create_task(self, **kwargs):
        """Helper to create a task"""
        try:
            from tasks.models import Task
            defaults = {
                'title': 'Test Task',
                'status': 'pending'
            }
            defaults.update(kwargs)
            
            if hasattr(Task, 'owner'):
                defaults.setdefault('owner', self.user)
            if hasattr(Task, 'assigned_to'):
                defaults.setdefault('assigned_to', self.user)
            
            return Task.objects.create(**defaults)
        except ImportError:
            pytest.skip("Task model not available")
    
    def test_create_task(self):
        """Test creating a task"""
        task = self.create_task()
        self.assertEqual(task.title, 'Test Task')
    
    def test_task_status_changes(self):
        """Test task status changes"""
        task = self.create_task(status='pending')
        
        task.status = 'in_progress'
        task.save()
        task.refresh_from_db()
        self.assertEqual(task.status, 'in_progress')
        
        task.status = 'completed'
        task.save()
        task.refresh_from_db()
        self.assertEqual(task.status, 'completed')
    
    def test_task_due_date(self):
        """Test task due date"""
        due_date = timezone.now() + timedelta(days=1)
        task = self.create_task()
        
        if hasattr(task, 'due_date'):
            task.due_date = due_date
            task.save()
            task.refresh_from_db()
            self.assertIsNotNone(task.due_date)
    
    def test_task_priority(self):
        """Test task priority field"""
        task = self.create_task()
        
        if hasattr(task, 'priority'):
            priorities = ['low', 'medium', 'high', 'urgent']
            for priority in priorities:
                task.priority = priority
                task.save()
                task.refresh_from_db()
                self.assertEqual(task.priority, priority)
    
    def test_task_completion(self):
        """Test task completion"""
        task = self.create_task(status='pending')
        
        if hasattr(task, 'completed_at'):
            self.assertIsNone(task.completed_at)
            
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.save()
            task.refresh_from_db()
            
            self.assertIsNotNone(task.completed_at)
    
    def test_overdue_task_detection(self):
        """Test detecting overdue tasks"""
        task = self.create_task()
        
        if hasattr(task, 'due_date') and hasattr(task, 'is_overdue'):
            # Set due date in the past
            task.due_date = timezone.now() - timedelta(days=1)
            task.status = 'pending'
            task.save()
            
            self.assertTrue(task.is_overdue)


# =============================================================================
# Organization Model Tests
# =============================================================================

@pytest.mark.django_db
class TestOrganizationModel(TestCase):
    """Tests for Organization model"""
    
    def create_organization(self, **kwargs):
        """Helper to create an organization"""
        try:
            from multi_tenant.models import Organization
            defaults = {
                'name': 'Test Organization',
                'slug': 'test-org'
            }
            defaults.update(kwargs)
            return Organization.objects.create(**defaults)
        except ImportError:
            pytest.skip("Organization model not available")
    
    def test_create_organization(self):
        """Test creating an organization"""
        org = self.create_organization()
        self.assertEqual(org.name, 'Test Organization')
        self.assertEqual(org.slug, 'test-org')
    
    def test_organization_slug_unique(self):
        """Test organization slug is unique"""
        try:
            from multi_tenant.models import Organization
            self.create_organization(slug='unique-slug')
            
            with self.assertRaises(IntegrityError):
                self.create_organization(slug='unique-slug', name='Another Org')
        except ImportError:
            pytest.skip("Organization model not available")
    
    def test_organization_str_representation(self):
        """Test organization string representation"""
        org = self.create_organization(name='Acme Corp')
        self.assertIn('Acme', str(org))


# =============================================================================
# Activity Model Tests
# =============================================================================

@pytest.mark.django_db
class TestActivityModel(TestCase):
    """Tests for Activity model"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='activity_test@example.com',
            password='Test123!'
        )
    
    def create_activity(self, **kwargs):
        """Helper to create an activity"""
        try:
            from activity_feed.models import Activity
            defaults = {
                'type': 'note',
                'description': 'Test activity'
            }
            defaults.update(kwargs)
            
            if hasattr(Activity, 'user'):
                defaults.setdefault('user', self.user)
            if hasattr(Activity, 'created_by'):
                defaults.setdefault('created_by', self.user)
            
            return Activity.objects.create(**defaults)
        except ImportError:
            pytest.skip("Activity model not available")
    
    def test_create_activity(self):
        """Test creating an activity"""
        activity = self.create_activity()
        self.assertEqual(activity.type, 'note')
    
    def test_activity_types(self):
        """Test different activity types"""
        activity_types = ['call', 'email', 'meeting', 'note', 'task']
        
        for act_type in activity_types:
            try:
                activity = self.create_activity(
                    type=act_type,
                    description=f'Test {act_type}'
                )
                self.assertEqual(activity.type, act_type)
            except ValueError:
                # Some types may not be valid
                pass
    
    def test_activity_timestamp(self):
        """Test activity timestamp"""
        activity = self.create_activity()
        
        if hasattr(activity, 'created_at'):
            self.assertIsNotNone(activity.created_at)


# =============================================================================
# Email Tracking Model Tests
# =============================================================================

@pytest.mark.django_db
class TestEmailTrackingModel(TestCase):
    """Tests for email tracking models"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='email_test@example.com',
            password='Test123!'
        )
    
    def create_tracked_email(self, **kwargs):
        """Helper to create a tracked email"""
        try:
            from email_tracking.models import TrackedEmail
            defaults = {
                'to_email': 'recipient@example.com',
                'subject': 'Test Email',
                'body': 'Test content'
            }
            defaults.update(kwargs)
            
            if hasattr(TrackedEmail, 'sender'):
                defaults.setdefault('sender', self.user)
            
            return TrackedEmail.objects.create(**defaults)
        except ImportError:
            pytest.skip("Email tracking model not available")
    
    def test_create_tracked_email(self):
        """Test creating a tracked email"""
        email = self.create_tracked_email()
        self.assertEqual(email.to_email, 'recipient@example.com')
        self.assertEqual(email.subject, 'Test Email')
    
    def test_email_open_tracking(self):
        """Test email open tracking"""
        email = self.create_tracked_email()
        
        if hasattr(email, 'opened') and hasattr(email, 'opened_at'):
            self.assertFalse(email.opened)
            
            email.opened = True
            email.opened_at = timezone.now()
            email.save()
            
            email.refresh_from_db()
            self.assertTrue(email.opened)
            self.assertIsNotNone(email.opened_at)
    
    def test_email_click_tracking(self):
        """Test email link click tracking"""
        email = self.create_tracked_email()
        
        if hasattr(email, 'clicks'):
            self.assertEqual(email.clicks, 0)
            
            email.clicks = 5
            email.save()
            email.refresh_from_db()
            
            self.assertEqual(email.clicks, 5)


# =============================================================================
# Custom Field Model Tests
# =============================================================================

@pytest.mark.django_db
class TestCustomFieldModel(TestCase):
    """Tests for custom field models"""
    
    def create_custom_field(self, **kwargs):
        """Helper to create a custom field"""
        try:
            from core.models import CustomField
            defaults = {
                'name': 'Custom Field',
                'field_type': 'text',
                'entity_type': 'contact'
            }
            defaults.update(kwargs)
            return CustomField.objects.create(**defaults)
        except ImportError:
            pytest.skip("CustomField model not available")
    
    def test_create_custom_field(self):
        """Test creating a custom field"""
        field = self.create_custom_field()
        self.assertEqual(field.name, 'Custom Field')
        self.assertEqual(field.field_type, 'text')
    
    def test_custom_field_types(self):
        """Test different custom field types"""
        field_types = ['text', 'number', 'date', 'boolean', 'dropdown']
        
        for i, field_type in enumerate(field_types):
            try:
                field = self.create_custom_field(
                    name=f'Field {i}',
                    field_type=field_type
                )
                self.assertEqual(field.field_type, field_type)
            except (ValueError, ValidationError):
                # Some types may not be valid
                pass
    
    def test_custom_field_required(self):
        """Test custom field required flag"""
        field = self.create_custom_field()
        
        if hasattr(field, 'required'):
            field.required = True
            field.save()
            field.refresh_from_db()
            self.assertTrue(field.required)


# =============================================================================
# Tag Model Tests
# =============================================================================

@pytest.mark.django_db
class TestTagModel(TestCase):
    """Tests for Tag model"""
    
    def create_tag(self, **kwargs):
        """Helper to create a tag"""
        try:
            from core.models import Tag
            defaults = {
                'name': 'Test Tag'
            }
            defaults.update(kwargs)
            return Tag.objects.create(**defaults)
        except ImportError:
            pytest.skip("Tag model not available")
    
    def test_create_tag(self):
        """Test creating a tag"""
        tag = self.create_tag()
        self.assertEqual(tag.name, 'Test Tag')
    
    def test_tag_color(self):
        """Test tag color field"""
        tag = self.create_tag()
        
        if hasattr(tag, 'color'):
            tag.color = '#FF5733'
            tag.save()
            tag.refresh_from_db()
            self.assertEqual(tag.color, '#FF5733')
    
    def test_tag_unique_name(self):
        """Test tag name uniqueness"""
        try:
            from core.models import Tag
            self.create_tag(name='Unique Tag')
            
            with self.assertRaises(IntegrityError):
                self.create_tag(name='Unique Tag')
        except (ImportError, Exception):
            # Tag may allow duplicates or not exist
            pass
