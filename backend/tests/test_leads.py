"""
Lead Management API Tests

Comprehensive test suite for lead management endpoints including:
- CRUD operations
- Lead scoring
- Filtering and search
- Bulk operations
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from lead_management.models import Lead

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


@pytest.fixture
def sample_lead(db, test_user):
    """Create and return a sample lead."""
    return Lead.objects.create(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        company='Acme Corp',
        phone='+1234567890',
        status='new',
        source='website',
        created_by=test_user
    )


@pytest.fixture
def multiple_leads(db, test_user):
    """Create multiple leads for testing."""
    leads = []
    statuses = ['new', 'contacted', 'qualified', 'proposal', 'won', 'lost']
    sources = ['website', 'referral', 'cold_call', 'social_media']
    
    for i in range(10):
        lead = Lead.objects.create(
            first_name=f'Lead{i}',
            last_name=f'Test{i}',
            email=f'lead{i}@example.com',
            company=f'Company {i}',
            status=statuses[i % len(statuses)],
            source=sources[i % len(sources)],
            created_by=test_user
        )
        leads.append(lead)
    return leads


class TestLeadCRUD:
    """Test cases for lead CRUD operations."""
    
    @pytest.mark.django_db
    def test_create_lead_success(self, authenticated_client, test_user):
        """Test successful lead creation."""
        url = reverse('api:v1:leads-list')
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'company': 'Tech Corp',
            'phone': '+1987654321',
            'status': 'new',
            'source': 'website'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get('first_name') == 'Jane'
        assert response.data.get('last_name') == 'Smith'
        
    @pytest.mark.django_db
    def test_create_lead_invalid_email(self, authenticated_client):
        """Test lead creation with invalid email fails."""
        url = reverse('api:v1:leads-list')
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'invalid-email',  # Invalid email
            'company': 'Tech Corp'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    @pytest.mark.django_db
    def test_get_lead_detail(self, authenticated_client, sample_lead):
        """Test retrieving a single lead."""
        url = reverse('api:v1:leads-detail', kwargs={'pk': sample_lead.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('first_name') == sample_lead.first_name
        
    @pytest.mark.django_db
    def test_update_lead_success(self, authenticated_client, sample_lead):
        """Test successful lead update."""
        url = reverse('api:v1:leads-detail', kwargs={'pk': sample_lead.id})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'status': 'contacted'
        }
        response = authenticated_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('first_name') == 'Updated'
        assert response.data.get('status') == 'contacted'
        
    @pytest.mark.django_db
    def test_partial_update_lead(self, authenticated_client, sample_lead):
        """Test partial lead update (PATCH)."""
        url = reverse('api:v1:leads-detail', kwargs={'pk': sample_lead.id})
        data = {'status': 'qualified'}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('status') == 'qualified'
        
    @pytest.mark.django_db
    def test_delete_lead_success(self, authenticated_client, sample_lead):
        """Test successful lead deletion."""
        url = reverse('api:v1:leads-detail', kwargs={'pk': sample_lead.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Lead.objects.filter(id=sample_lead.id).exists()


class TestLeadListing:
    """Test cases for lead listing and filtering."""
    
    @pytest.mark.django_db
    def test_list_leads(self, authenticated_client, multiple_leads):
        """Test listing all leads."""
        url = reverse('api:v1:leads-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Check for paginated response
        if 'results' in response.data:
            assert len(response.data['results']) > 0
        else:
            assert len(response.data) > 0
            
    @pytest.mark.django_db
    def test_filter_leads_by_status(self, authenticated_client, multiple_leads):
        """Test filtering leads by status."""
        url = reverse('api:v1:leads-list')
        response = authenticated_client.get(url, {'status': 'new'})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        for lead in results:
            assert lead.get('status') == 'new'
            
    @pytest.mark.django_db
    def test_search_leads(self, authenticated_client, sample_lead):
        """Test searching leads."""
        url = reverse('api:v1:leads-list')
        response = authenticated_client.get(url, {'search': 'John'})
        
        assert response.status_code == status.HTTP_200_OK


class TestLeadPermissions:
    """Test cases for lead access permissions."""
    
    @pytest.mark.django_db
    def test_unauthenticated_access_denied(self, api_client):
        """Test unauthenticated access is denied."""
        url = reverse('api:v1:leads-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    @pytest.mark.django_db
    def test_lead_not_found(self, authenticated_client):
        """Test accessing non-existent lead returns 404."""
        url = reverse('api:v1:leads-detail', kwargs={'pk': 99999})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestLeadScoring:
    """Test cases for lead scoring functionality."""
    
    @pytest.mark.django_db
    @pytest.mark.slow
    def test_lead_score_calculation(self, authenticated_client, sample_lead):
        """Test that lead score is calculated."""
        url = reverse('api:v1:leads-detail', kwargs={'pk': sample_lead.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Lead score should be present (may be None or a number)
        assert 'lead_score' in response.data or 'score' in response.data
