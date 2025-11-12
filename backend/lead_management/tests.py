from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Lead, LeadActivity
from decimal import Decimal

User = get_user_model()


class LeadModelTest(TestCase):
    """Test cases for Lead model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='testpass123'
        )
        self.lead_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'company_name': 'Test Company',
            'job_title': 'CEO',
            'lead_source': 'website',
            'status': 'new',
            'priority': 'high',
            'owner': self.user
        }
    
    def test_create_lead(self):
        """Test creating a new lead"""
        lead = Lead.objects.create(**self.lead_data)
        self.assertEqual(lead.first_name, 'John')
        self.assertEqual(lead.email, 'john@example.com')
        self.assertEqual(lead.status, 'new')
        self.assertEqual(lead.priority, 'high')
    
    def test_lead_full_name_property(self):
        """Test full_name property"""
        lead = Lead.objects.create(**self.lead_data)
        self.assertEqual(lead.full_name, 'John Doe')
    
    def test_lead_default_values(self):
        """Test default values"""
        lead = Lead.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            owner=self.user
        )
        self.assertEqual(lead.status, 'new')
        self.assertEqual(lead.priority, 'medium')
        self.assertEqual(lead.lead_source, 'website')
        self.assertEqual(lead.lead_score, 0)
        self.assertEqual(lead.probability, 0)
    
    def test_lead_scoring(self):
        """Test lead scoring functionality"""
        lead = Lead.objects.create(**self.lead_data)
        lead.lead_score = 85
        lead.save()
        self.assertEqual(lead.lead_score, 85)
    
    def test_lead_estimated_value(self):
        """Test estimated value"""
        lead_data = self.lead_data.copy()
        lead_data['estimated_value'] = Decimal('50000.00')
        lead = Lead.objects.create(**lead_data)
        self.assertEqual(lead.estimated_value, Decimal('50000.00'))
    
    def test_lead_assignment(self):
        """Test lead assignment"""
        sales_rep = User.objects.create_user(
            username='salesrep',
            email='sales@example.com',
            password='pass123'
        )
        lead_data = self.lead_data.copy()
        lead_data['assigned_to'] = sales_rep
        lead = Lead.objects.create(**lead_data)
        self.assertEqual(lead.assigned_to, sales_rep)
        self.assertEqual(lead.owner, self.user)


class LeadActivityTest(TestCase):
    """Test cases for LeadActivity model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='testpass123'
        )
        self.lead = Lead.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            owner=self.user
        )
    
    def test_create_lead_activity(self):
        """Test creating a lead activity"""
        activity = LeadActivity.objects.create(
            lead=self.lead,
            activity_type='call',
            subject='Follow-up call'
        )
        self.assertEqual(activity.lead, self.lead)
        self.assertEqual(activity.activity_type, 'call')
        self.assertEqual(activity.subject, 'Follow-up call')
    
    def test_lead_multiple_activities(self):
        """Test multiple activities for a lead"""
        LeadActivity.objects.create(
            lead=self.lead,
            activity_type='call',
            subject='First call'
        )
        LeadActivity.objects.create(
            lead=self.lead,
            activity_type='email',
            subject='Follow-up email'
        )
        self.assertEqual(self.lead.activities.count(), 2)


class LeadStatusTest(TestCase):
    """Test cases for lead status transitions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='testpass123'
        )
        self.lead = Lead.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            owner=self.user,
            status='new'
        )
    
    def test_status_transition_to_contacted(self):
        """Test changing status to contacted"""
        self.lead.status = 'contacted'
        self.lead.last_contact_date = timezone.now()
        self.lead.save()
        self.assertEqual(self.lead.status, 'contacted')
        self.assertIsNotNone(self.lead.last_contact_date)
    
    def test_status_transition_to_qualified(self):
        """Test changing status to qualified"""
        self.lead.status = 'qualified'
        self.lead.lead_score = 75
        self.lead.save()
        self.assertEqual(self.lead.status, 'qualified')
    
    def test_status_transition_to_converted(self):
        """Test changing status to converted"""
        self.lead.status = 'converted'
        self.lead.converted_at = timezone.now()
        self.lead.save()
        self.assertEqual(self.lead.status, 'converted')
        self.assertIsNotNone(self.lead.converted_at)


class LeadQueryTest(TestCase):
    """Test cases for lead queries"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='testpass123'
        )
        # Create multiple leads
        for i in range(10):
            Lead.objects.create(
                first_name=f'Lead{i}',
                last_name=f'Test{i}',
                email=f'lead{i}@example.com',
                status='new' if i % 2 == 0 else 'contacted',
                priority='high' if i < 5 else 'medium',
                lead_score=i * 10,
                owner=self.user
            )
    
    def test_filter_by_status(self):
        """Test filtering leads by status"""
        new_leads = Lead.objects.filter(status='new')
        contacted_leads = Lead.objects.filter(status='contacted')
        self.assertEqual(new_leads.count(), 5)
        self.assertEqual(contacted_leads.count(), 5)
    
    def test_filter_by_priority(self):
        """Test filtering leads by priority"""
        high_priority = Lead.objects.filter(priority='high')
        self.assertEqual(high_priority.count(), 5)
    
    def test_filter_by_score_range(self):
        """Test filtering leads by score range"""
        high_score_leads = Lead.objects.filter(lead_score__gte=50)
        self.assertEqual(high_score_leads.count(), 5)
    
    def test_order_by_score(self):
        """Test ordering leads by score"""
        leads = Lead.objects.all().order_by('-lead_score')
        self.assertEqual(leads.first().lead_score, 90)
        self.assertEqual(leads.last().lead_score, 0)
