from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Contact, ContactGroup

User = get_user_model()


class ContactModelTest(TestCase):
    """Test cases for Contact model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='testpass123'
        )
        self.contact_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'company_name': 'Test Company',
            'job_title': 'CEO',
            'contact_type': 'customer',
            'assigned_to': self.user,
            'created_by': self.user
        }

    def test_create_contact(self):
        """Test creating a new contact"""
        contact = Contact.objects.create(**self.contact_data)
        self.assertEqual(contact.first_name, 'John')
        self.assertEqual(contact.last_name, 'Doe')
        self.assertEqual(contact.email, 'john.doe@example.com')
        self.assertEqual(contact.contact_type, 'customer')

    def test_contact_full_name_property(self):
        """Test full_name property"""
        contact = Contact.objects.create(**self.contact_data)
        self.assertEqual(contact.full_name, 'John Doe')

    def test_contact_str_method(self):
        """Test contact string representation"""
        contact = Contact.objects.create(**self.contact_data)
        expected = 'John Doe (john.doe@example.com)'
        self.assertEqual(str(contact), expected)

    def test_contact_default_values(self):
        """Test default values"""
        contact = Contact.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            created_by=self.user
        )
        self.assertEqual(contact.contact_type, 'prospect')
        self.assertEqual(contact.status, 'active')
        self.assertIsInstance(contact.tags, list)
        self.assertIsInstance(contact.custom_fields, dict)


class ContactGroupTest(TestCase):
    """Test cases for ContactGroup model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='testpass123'
        )
        self.contact1 = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            created_by=self.user
        )

    def test_create_contact_group(self):
        """Test creating a contact group"""
        group = ContactGroup.objects.create(
            name='VIP Customers',
            description='High value customers',
            created_by=self.user
        )
        self.assertEqual(group.name, 'VIP Customers')
        self.assertEqual(group.created_by, self.user)
