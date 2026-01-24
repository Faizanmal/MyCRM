"""
MyCRM Backend - Test Utilities

Shared utilities for pytest tests
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import Mock, patch
from datetime import datetime, date, timedelta
from decimal import Decimal
import json
import uuid

User = get_user_model()


# =============================================================================
# Factory Mixins
# =============================================================================

class UserFactoryMixin:
    """Mixin for creating test users"""
    
    def create_user(self, email=None, password='TestPass123!', **kwargs):
        """Create a regular user"""
        email = email or f'user_{uuid.uuid4().hex[:8]}@test.com'
        return User.objects.create_user(
            email=email,
            password=password,
            **kwargs
        )
    
    def create_admin_user(self, email=None, password='AdminPass123!', **kwargs):
        """Create an admin user"""
        email = email or f'admin_{uuid.uuid4().hex[:8]}@test.com'
        return User.objects.create_superuser(
            email=email,
            password=password,
            **kwargs
        )
    
    def create_staff_user(self, email=None, password='StaffPass123!', **kwargs):
        """Create a staff user"""
        email = email or f'staff_{uuid.uuid4().hex[:8]}@test.com'
        user = User.objects.create_user(
            email=email,
            password=password,
            **kwargs
        )
        user.is_staff = True
        user.save()
        return user


class OrganizationFactoryMixin:
    """Mixin for creating test organizations"""
    
    def create_organization(self, name=None, slug=None, **kwargs):
        """Create an organization"""
        try:
            from multi_tenant.models import Organization
            
            name = name or f'Org {uuid.uuid4().hex[:8]}'
            slug = slug or f'org-{uuid.uuid4().hex[:8]}'
            
            return Organization.objects.create(
                name=name,
                slug=slug,
                **kwargs
            )
        except ImportError:
            return None


class CRMFactoryMixin:
    """Mixin for creating CRM entities"""
    
    def create_contact(self, owner=None, **kwargs):
        """Create a contact"""
        try:
            from contacts.models import Contact
            
            defaults = {
                'first_name': 'Test',
                'last_name': f'Contact_{uuid.uuid4().hex[:6]}',
                'email': f'contact_{uuid.uuid4().hex[:8]}@test.com'
            }
            defaults.update(kwargs)
            
            if owner and hasattr(Contact, 'owner'):
                defaults['owner'] = owner
            
            return Contact.objects.create(**defaults)
        except ImportError:
            return None
    
    def create_lead(self, owner=None, **kwargs):
        """Create a lead"""
        try:
            from leads.models import Lead
            
            defaults = {
                'name': f'Lead {uuid.uuid4().hex[:6]}',
                'email': f'lead_{uuid.uuid4().hex[:8]}@test.com',
                'status': 'new'
            }
            defaults.update(kwargs)
            
            if owner and hasattr(Lead, 'owner'):
                defaults['owner'] = owner
            
            return Lead.objects.create(**defaults)
        except ImportError:
            return None
    
    def create_opportunity(self, owner=None, **kwargs):
        """Create an opportunity"""
        try:
            from opportunities.models import Opportunity
            
            defaults = {
                'name': f'Opportunity {uuid.uuid4().hex[:6]}',
                'value': Decimal('50000.00'),
                'stage': 'prospecting'
            }
            defaults.update(kwargs)
            
            if owner and hasattr(Opportunity, 'owner'):
                defaults['owner'] = owner
            
            return Opportunity.objects.create(**defaults)
        except ImportError:
            return None
    
    def create_task(self, owner=None, **kwargs):
        """Create a task"""
        try:
            from tasks.models import Task
            
            defaults = {
                'title': f'Task {uuid.uuid4().hex[:6]}',
                'status': 'pending'
            }
            defaults.update(kwargs)
            
            if owner and hasattr(Task, 'owner'):
                defaults['owner'] = owner
            
            return Task.objects.create(**defaults)
        except ImportError:
            return None


# =============================================================================
# Test Case Base Classes
# =============================================================================

@pytest.mark.django_db
class BaseTestCase(TestCase, UserFactoryMixin, OrganizationFactoryMixin, CRMFactoryMixin):
    """Base test case with all mixins"""
    pass


@pytest.mark.django_db
class APITestCase(BaseTestCase):
    """Base API test case"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = self.create_user()
        self.admin_user = self.create_admin_user()
    
    def authenticate(self, user=None):
        """Authenticate API client"""
        user = user or self.user
        self.client.force_authenticate(user=user)
    
    def authenticate_admin(self):
        """Authenticate as admin"""
        self.client.force_authenticate(user=self.admin_user)
    
    def logout(self):
        """Logout from API client"""
        self.client.force_authenticate(user=None)


# =============================================================================
# Assertion Helpers
# =============================================================================

class APIAssertions:
    """API-specific assertions"""
    
    @staticmethod
    def assert_status_ok(response):
        """Assert response has OK status"""
        assert response.status_code in [200, 201, 204], \
            f"Expected OK status, got {response.status_code}: {response.content}"
    
    @staticmethod
    def assert_status_created(response):
        """Assert response has Created status"""
        assert response.status_code == 201, \
            f"Expected 201, got {response.status_code}: {response.content}"
    
    @staticmethod
    def assert_status_unauthorized(response):
        """Assert response has Unauthorized status"""
        assert response.status_code == 401, \
            f"Expected 401, got {response.status_code}"
    
    @staticmethod
    def assert_status_forbidden(response):
        """Assert response has Forbidden status"""
        assert response.status_code == 403, \
            f"Expected 403, got {response.status_code}"
    
    @staticmethod
    def assert_status_not_found(response):
        """Assert response has Not Found status"""
        assert response.status_code == 404, \
            f"Expected 404, got {response.status_code}"
    
    @staticmethod
    def assert_status_bad_request(response):
        """Assert response has Bad Request status"""
        assert response.status_code == 400, \
            f"Expected 400, got {response.status_code}"
    
    @staticmethod
    def assert_validation_error(response, field):
        """Assert response has validation error for field"""
        assert response.status_code == 400
        data = response.json()
        assert field in data, f"Expected error for {field}, got: {data}"
    
    @staticmethod
    def assert_paginated_response(response):
        """Assert response is paginated"""
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data or isinstance(data, list)
        if 'results' in data:
            assert 'count' in data


# =============================================================================
# Mock Helpers
# =============================================================================

def mock_datetime(target_datetime):
    """Context manager to mock datetime"""
    mock = Mock(wraps=datetime)
    mock.now = Mock(return_value=target_datetime)
    mock.today = Mock(return_value=target_datetime.date())
    
    return patch('datetime.datetime', mock)


def mock_date(target_date):
    """Context manager to mock date"""
    mock = Mock(wraps=date)
    mock.today = Mock(return_value=target_date)
    
    return patch('datetime.date', mock)


def mock_external_api(url_pattern, response_data, status_code=200):
    """Mock external API calls"""
    import requests
    
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = response_data
    mock_response.text = json.dumps(response_data)
    mock_response.ok = status_code < 400
    
    return patch.object(
        requests,
        'get',
        return_value=mock_response
    )


# =============================================================================
# Data Generators
# =============================================================================

class DataGenerator:
    """Generate test data"""
    
    @staticmethod
    def email():
        """Generate random email"""
        return f'test_{uuid.uuid4().hex[:8]}@example.com'
    
    @staticmethod
    def phone():
        """Generate random phone"""
        import random
        return f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}'
    
    @staticmethod
    def company_name():
        """Generate random company name"""
        prefixes = ['Acme', 'Tech', 'Global', 'Digital', 'Smart', 'Pro']
        suffixes = ['Corp', 'Inc', 'LLC', 'Solutions', 'Systems', 'Group']
        import random
        return f'{random.choice(prefixes)} {random.choice(suffixes)}'
    
    @staticmethod
    def money_amount(min_val=1000, max_val=1000000):
        """Generate random money amount"""
        import random
        return Decimal(str(random.randint(min_val, max_val)))
    
    @staticmethod
    def future_date(days_ahead=30):
        """Generate future date"""
        return date.today() + timedelta(days=days_ahead)
    
    @staticmethod
    def past_date(days_ago=30):
        """Generate past date"""
        return date.today() - timedelta(days=days_ago)
    
    @staticmethod
    def percentage():
        """Generate random percentage 0-100"""
        import random
        return random.randint(0, 100)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def api_client():
    """Provide API client"""
    return APIClient()


@pytest.fixture
def user(db):
    """Provide a test user"""
    return User.objects.create_user(
        email='fixture_user@test.com',
        password='TestPass123!'
    )


@pytest.fixture
def admin_user(db):
    """Provide an admin user"""
    return User.objects.create_superuser(
        email='fixture_admin@test.com',
        password='AdminPass123!'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Provide authenticated API client"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Provide admin authenticated API client"""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def data_generator():
    """Provide data generator"""
    return DataGenerator()


# =============================================================================
# Performance Utilities
# =============================================================================

import time
from contextlib import contextmanager


@contextmanager
def timer(name='Operation'):
    """Context manager to time operations"""
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f'{name} took {(end - start) * 1000:.2f}ms')


class QueryCounter:
    """Count database queries"""
    
    def __init__(self):
        self.queries = []
    
    def __enter__(self):
        from django.db import connection
        from django.conf import settings
        
        settings.DEBUG = True
        connection.queries_log.clear()
        return self
    
    def __exit__(self, *args):
        from django.db import connection
        from django.conf import settings
        
        self.queries = list(connection.queries)
        settings.DEBUG = False
    
    @property
    def count(self):
        return len(self.queries)
    
    def assert_max_queries(self, max_count):
        assert self.count <= max_count, \
            f"Expected max {max_count} queries, got {self.count}"
