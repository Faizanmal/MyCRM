# MyCRM Backend - Enhanced Test Suite Configuration

import pytest
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import factory
from faker import Faker

fake = Faker()


# =============================================================================
# Test Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest settings."""
    settings.DEBUG = False
    settings.TESTING = True
    settings.PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    

# =============================================================================
# Fixtures - Authentication
# =============================================================================

@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def authenticated_client(user):
    """Return an authenticated API client."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def admin_client(admin_user):
    """Return an authenticated admin API client."""
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


# =============================================================================
# Fixtures - Users
# =============================================================================

@pytest.fixture
def user(db, organization):
    """Create a regular user."""
    from user_management.models import User
    return User.objects.create_user(
        email='testuser@example.com',
        password='testpass123!',
        first_name='Test',
        last_name='User',
        role='sales_rep',
        organization=organization
    )


@pytest.fixture
def admin_user(db, organization):
    """Create an admin user."""
    from user_management.models import User
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123!',
        first_name='Admin',
        last_name='User',
        organization=organization
    )


@pytest.fixture
def manager_user(db, organization):
    """Create a manager user."""
    from user_management.models import User
    return User.objects.create_user(
        email='manager@example.com',
        password='managerpass123!',
        first_name='Manager',
        last_name='User',
        role='manager',
        organization=organization
    )


# =============================================================================
# Fixtures - Organizations
# =============================================================================

@pytest.fixture
def organization(db):
    """Create an organization."""
    from multi_tenant.models import Organization
    return Organization.objects.create(
        name='Test Organization',
        slug='test-org',
        plan='professional'
    )


@pytest.fixture
def other_organization(db):
    """Create another organization for isolation tests."""
    from multi_tenant.models import Organization
    return Organization.objects.create(
        name='Other Organization',
        slug='other-org',
        plan='starter'
    )


# =============================================================================
# Fixtures - CRM Entities
# =============================================================================

@pytest.fixture
def contact(db, user, organization):
    """Create a contact."""
    from contact_management.models import Contact
    return Contact.objects.create(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        phone='+1-555-123-4567',
        company='Acme Corp',
        job_title='CEO',
        owner=user,
        organization=organization
    )


@pytest.fixture
def contact_factory(db, organization):
    """Return a factory for creating contacts."""
    class ContactFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = 'contact_management.Contact'
        
        first_name = factory.Faker('first_name')
        last_name = factory.Faker('last_name')
        email = factory.Sequence(lambda n: f'contact{n}@example.com')
        phone = factory.Faker('phone_number')
        company = factory.Faker('company')
        job_title = factory.Faker('job')
        organization = factory.LazyAttribute(lambda _: organization)
    
    return ContactFactory


@pytest.fixture
def lead(db, user, organization):
    """Create a lead."""
    from lead_management.models import Lead
    return Lead.objects.create(
        name='Test Lead',
        company='Lead Corp',
        email='lead@example.com',
        phone='+1-555-987-6543',
        source='website',
        status='new',
        estimated_value=50000,
        owner=user,
        organization=organization
    )


@pytest.fixture
def lead_factory(db, organization):
    """Return a factory for creating leads."""
    class LeadFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = 'lead_management.Lead'
        
        name = factory.Sequence(lambda n: f'Lead {n}')
        company = factory.Faker('company')
        email = factory.Sequence(lambda n: f'lead{n}@example.com')
        source = factory.Iterator(['website', 'referral', 'cold_call', 'event'])
        status = factory.Iterator(['new', 'contacted', 'qualified'])
        estimated_value = factory.Faker('random_int', min=10000, max=100000)
        organization = factory.LazyAttribute(lambda _: organization)
    
    return LeadFactory


@pytest.fixture
def opportunity(db, user, contact, organization):
    """Create an opportunity."""
    from opportunity_management.models import Opportunity, OpportunityStage
    
    # Create default stages if needed
    stage, _ = OpportunityStage.objects.get_or_create(
        name='Prospecting',
        defaults={'probability': 10, 'order': 1, 'organization': organization}
    )
    
    return Opportunity.objects.create(
        name='Test Deal',
        contact=contact,
        stage=stage,
        value=75000,
        probability=0.5,
        expected_close_date='2025-03-31',
        owner=user,
        organization=organization
    )


@pytest.fixture
def task(db, user, organization):
    """Create a task."""
    from task_management.models import Task
    return Task.objects.create(
        title='Test Task',
        description='Test task description',
        task_type='call',
        priority='high',
        status='pending',
        due_date='2024-12-31T17:00:00Z',
        assigned_to=user,
        created_by=user,
        organization=organization
    )


# =============================================================================
# Fixtures - Pipelines & Stages
# =============================================================================

@pytest.fixture
def pipeline(db, organization):
    """Create a sales pipeline."""
    from opportunity_management.models import OpportunityStage
    
    stages = [
        ('Prospecting', 10, 1),
        ('Qualification', 25, 2),
        ('Proposal', 50, 3),
        ('Negotiation', 75, 4),
        ('Closed Won', 100, 5),
        ('Closed Lost', 0, 6),
    ]
    
    created_stages = []
    for name, prob, order in stages:
        stage = OpportunityStage.objects.create(
            name=name,
            probability=prob,
            order=order,
            organization=organization
        )
        created_stages.append(stage)
    
    return created_stages


# =============================================================================
# Test Utilities
# =============================================================================

class TestDataBuilder:
    """Utility class for building test data."""
    
    @staticmethod
    def create_contacts_batch(organization, owner, count=10):
        """Create a batch of contacts."""
        from contact_management.models import Contact
        contacts = []
        for i in range(count):
            contact = Contact.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=f'contact{i}_{fake.random_int()}@example.com',
                company=fake.company(),
                owner=owner,
                organization=organization
            )
            contacts.append(contact)
        return contacts
    
    @staticmethod
    def create_leads_batch(organization, owner, count=10):
        """Create a batch of leads."""
        from lead_management.models import Lead
        leads = []
        sources = ['website', 'referral', 'cold_call', 'event', 'other']
        statuses = ['new', 'contacted', 'qualified']
        
        for i in range(count):
            lead = Lead.objects.create(
                name=f'{fake.company()} Lead',
                company=fake.company(),
                email=f'lead{i}_{fake.random_int()}@example.com',
                source=fake.random_element(sources),
                status=fake.random_element(statuses),
                estimated_value=fake.random_int(min=10000, max=100000),
                owner=owner,
                organization=organization
            )
            leads.append(lead)
        return leads


@pytest.fixture
def test_data_builder():
    """Return a test data builder instance."""
    return TestDataBuilder()


# =============================================================================
# Assertion Helpers
# =============================================================================

class APIAssertions:
    """Assertion helpers for API tests."""
    
    @staticmethod
    def assert_success(response, status_code=200):
        """Assert successful response."""
        assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.content}"
    
    @staticmethod
    def assert_created(response):
        """Assert resource created."""
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.content}"
    
    @staticmethod
    def assert_bad_request(response):
        """Assert bad request."""
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.content}"
    
    @staticmethod
    def assert_unauthorized(response):
        """Assert unauthorized."""
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.content}"
    
    @staticmethod
    def assert_forbidden(response):
        """Assert forbidden."""
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.content}"
    
    @staticmethod
    def assert_not_found(response):
        """Assert not found."""
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.content}"
    
    @staticmethod
    def assert_pagination(response, expected_count=None):
        """Assert pagination structure."""
        data = response.json()
        assert 'count' in data, "Missing 'count' in pagination"
        assert 'results' in data, "Missing 'results' in pagination"
        if expected_count is not None:
            assert data['count'] == expected_count, f"Expected count {expected_count}, got {data['count']}"


@pytest.fixture
def assertions():
    """Return API assertions helper."""
    return APIAssertions()


# =============================================================================
# Mock Services
# =============================================================================

@pytest.fixture
def mock_email_service(mocker):
    """Mock email service."""
    return mocker.patch('django.core.mail.send_mail')


@pytest.fixture
def mock_ai_service(mocker):
    """Mock AI service."""
    mock = mocker.patch('ai_insights.services.scoring.LeadScoringEngine.score_lead')
    mock.return_value = {
        'score': 85,
        'breakdown': {'engagement': 30, 'fit': 30, 'intent': 25},
        'recommendation': 'High priority lead'
    }
    return mock


@pytest.fixture
def mock_celery_task(mocker):
    """Mock Celery task to run synchronously."""
    mocker.patch('celery.app.task.Task.delay', side_effect=lambda *args, **kwargs: None)


# =============================================================================
# Database Utilities
# =============================================================================

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass


@pytest.fixture
def django_db_reset_sequences(db, django_db_blocker):
    """Reset database sequences after test."""
    yield
    with django_db_blocker.unblock():
        from django.core.management import call_command
        call_command('sqlsequencereset', 'contact_management', 'lead_management', verbosity=0)
