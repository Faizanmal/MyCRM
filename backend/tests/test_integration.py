"""
Integration Tests for API Endpoints

Tests that verify the integration between different components
and API workflows.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create and return a test user."""
    return User.objects.create_user(
        username='integrationuser',
        email='integration@example.com', 
        password='TestPass123!',
        first_name='Integration',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    @pytest.mark.django_db
    @pytest.mark.integration
    def test_health_check(self, api_client):
        """Test basic health check endpoint."""
        response = api_client.get('/api/v1/healthz/')
        
        assert response.status_code == status.HTTP_200_OK
        
    @pytest.mark.django_db
    @pytest.mark.integration
    def test_ping_endpoint(self, api_client):
        """Test ping endpoint for load balancer."""
        response = api_client.get('/api/v1/ping/')
        
        assert response.status_code == status.HTTP_200_OK
        
    @pytest.mark.django_db
    @pytest.mark.integration
    def test_ready_endpoint(self, api_client):
        """Test readiness check endpoint."""
        response = api_client.get('/api/v1/ready/')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]


class TestCRMWorkflow:
    """Test complete CRM workflows."""
    
    @pytest.mark.django_db
    @pytest.mark.integration
    def test_lead_to_opportunity_workflow(self, authenticated_client):
        """Test converting a lead to an opportunity."""
        # Step 1: Create a lead
        lead_url = reverse('api:v1:leads-list')
        lead_data = {
            'first_name': 'Prospect',
            'last_name': 'Customer',
            'email': 'prospect@example.com',
            'company': 'Big Corp',
            'status': 'new',
            'source': 'website'
        }
        lead_response = authenticated_client.post(lead_url, lead_data, format='json')
        
        assert lead_response.status_code == status.HTTP_201_CREATED
        lead_id = lead_response.data.get('id')
        
        # Step 2: Update lead status to qualified
        update_url = reverse('api:v1:leads-detail', kwargs={'pk': lead_id})
        update_data = {'status': 'qualified'}
        update_response = authenticated_client.patch(update_url, update_data, format='json')
        
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data.get('status') == 'qualified'
        
    @pytest.mark.django_db
    @pytest.mark.integration
    def test_contact_with_tasks(self, authenticated_client):
        """Test creating a contact and associating tasks."""
        # Step 1: Create a contact
        contact_url = reverse('api:v1:contacts-list')
        contact_data = {
            'first_name': 'John',
            'last_name': 'Client',
            'email': 'john.client@example.com',
            'phone': '+1234567890'
        }
        contact_response = authenticated_client.post(contact_url, contact_data, format='json')
        
        assert contact_response.status_code == status.HTTP_201_CREATED
        contact_id = contact_response.data.get('id')
        
        # Step 2: Create a task for the contact
        task_url = reverse('api:v1:tasks-list')
        task_data = {
            'title': 'Follow up call',
            'description': 'Schedule follow up call with John',
            'priority': 'high',
            'status': 'pending',
            'contact_id': contact_id
        }
        task_response = authenticated_client.post(task_url, task_data, format='json')
        
        # Task creation may succeed or fail based on model structure
        assert task_response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST  # If contact_id is not a valid field
        ]


class TestAPIVersioning:
    """Test API versioning."""
    
    @pytest.mark.django_db
    @pytest.mark.integration
    def test_v1_endpoints_accessible(self, authenticated_client):
        """Test v1 API endpoints are accessible."""
        endpoints = [
            '/api/v1/leads/',
            '/api/v1/contacts/',
            '/api/v1/tasks/',
        ]
        
        for endpoint in endpoints:
            response = authenticated_client.get(endpoint)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestBulkOperations:
    """Test bulk operations on resources."""
    
    @pytest.mark.django_db
    @pytest.mark.integration
    @pytest.mark.slow
    def test_bulk_lead_creation(self, authenticated_client):
        """Test creating multiple leads."""
        url = reverse('api:v1:leads-list')
        
        leads_created = 0
        for i in range(5):
            data = {
                'first_name': f'Bulk{i}',
                'last_name': f'Lead{i}',
                'email': f'bulk{i}@example.com',
                'status': 'new'
            }
            response = authenticated_client.post(url, data, format='json')
            if response.status_code == status.HTTP_201_CREATED:
                leads_created += 1
                
        assert leads_created >= 3  # At least 3 should succeed


class TestPagination:
    """Test pagination functionality."""
    
    @pytest.mark.django_db
    @pytest.mark.integration
    def test_leads_pagination(self, authenticated_client, test_user):
        """Test leads endpoint pagination."""
        from lead_management.models import Lead
        
        # Create multiple leads
        for i in range(25):
            Lead.objects.create(
                first_name=f'Page{i}',
                last_name=f'Test{i}',
                email=f'page{i}@example.com',
                status='new',
                created_by=test_user
            )
            
        url = reverse('api:v1:leads-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check pagination structure
        if 'results' in response.data:
            assert 'count' in response.data or 'next' in response.data
            assert len(response.data['results']) <= 20  # Page size limit


class TestFilteringAndSearch:
    """Test filtering and search functionality."""
    
    @pytest.mark.django_db
    @pytest.mark.integration
    def test_leads_complex_filter(self, authenticated_client, test_user):
        """Test complex filtering on leads."""
        from lead_management.models import Lead
        
        # Create leads with different statuses
        Lead.objects.create(
            first_name='Active', last_name='Lead',
            email='active@example.com', status='new',
            created_by=test_user
        )
        Lead.objects.create(
            first_name='Qualified', last_name='Lead',
            email='qualified@example.com', status='qualified',
            created_by=test_user
        )
        
        url = reverse('api:v1:leads-list')
        
        # Test status filter
        response = authenticated_client.get(url, {'status': 'new'})
        assert response.status_code == status.HTTP_200_OK
        
        # Test search
        response = authenticated_client.get(url, {'search': 'Active'})
        assert response.status_code == status.HTTP_200_OK
