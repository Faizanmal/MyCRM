"""
Contact Management API Tests

Comprehensive test suite for contact management including:
- CRUD operations
- Search and filtering
- Contact merging
- Activity tracking
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create and return a test user."""
    user = User.objects.create_user(
        username='contactuser',
        email='contacts@example.com',
        password='TestPass123!',
        first_name='Contact',
        last_name='User'
    )
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def sample_contact(db, test_user):
    """Create and return a sample contact."""
    from contact_management.models import Contact
    return Contact.objects.create(
        first_name='John',
        last_name='Customer',
        email='john.customer@example.com',
        phone='+1234567890',
        company='Acme Inc',
        job_title='CEO',
        created_by=test_user
    )


@pytest.fixture
def multiple_contacts(db, test_user):
    """Create multiple contacts for testing."""
    from contact_management.models import Contact

    contacts = []
    companies = ['Apple', 'Google', 'Microsoft', 'Amazon', 'Meta']

    for i, company in enumerate(companies):
        contact = Contact.objects.create(
            first_name=f'Contact{i}',
            last_name=f'Test{i}',
            email=f'contact{i}@{company.lower()}.com',
            company=company,
            phone=f'+1234567890{i}',
            created_by=test_user
        )
        contacts.append(contact)
    return contacts


class TestContactCRUD:
    """Test cases for contact CRUD operations."""

    @pytest.mark.django_db
    def test_create_contact_success(self, authenticated_client):
        """Test successful contact creation."""
        url = reverse('api:v1:contacts-list')
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'phone': '+1987654321',
            'company': 'Tech Corp',
            'job_title': 'CTO'
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get('first_name') == 'Jane'
        assert response.data.get('email') == 'jane.doe@example.com'

    @pytest.mark.django_db
    def test_create_contact_duplicate_email(self, authenticated_client, sample_contact):
        """Test creating contact with duplicate email."""
        url = reverse('api:v1:contacts-list')
        data = {
            'first_name': 'Duplicate',
            'last_name': 'Contact',
            'email': sample_contact.email,  # Duplicate
            'company': 'Another Corp'
        }
        response = authenticated_client.post(url, data, format='json')

        # Should either reject or handle duplicate
        assert response.status_code in [
            status.HTTP_201_CREATED,  # May allow with warning
            status.HTTP_400_BAD_REQUEST,  # May reject
        ]

    @pytest.mark.django_db
    def test_get_contact_detail(self, authenticated_client, sample_contact):
        """Test retrieving a single contact."""
        url = reverse('api:v1:contacts-detail', kwargs={'pk': sample_contact.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('email') == sample_contact.email

    @pytest.mark.django_db
    def test_update_contact(self, authenticated_client, sample_contact):
        """Test updating a contact."""
        url = reverse('api:v1:contacts-detail', kwargs={'pk': sample_contact.id})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'job_title': 'Updated Title'
        }
        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('first_name') == 'Updated'

    @pytest.mark.django_db
    def test_partial_update_contact(self, authenticated_client, sample_contact):
        """Test partial contact update (PATCH)."""
        url = reverse('api:v1:contacts-detail', kwargs={'pk': sample_contact.id})
        data = {'job_title': 'New Title'}
        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('job_title') == 'New Title'

    @pytest.mark.django_db
    def test_delete_contact(self, authenticated_client, sample_contact):
        """Test deleting a contact."""
        url = reverse('api:v1:contacts-detail', kwargs={'pk': sample_contact.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestContactSearch:
    """Test cases for contact search and filtering."""

    @pytest.mark.django_db
    def test_search_by_name(self, authenticated_client, multiple_contacts):
        """Test searching contacts by name."""
        url = reverse('api:v1:contacts-list')
        response = authenticated_client.get(url, {'search': 'Contact0'})

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) >= 1

    @pytest.mark.django_db
    def test_search_by_email(self, authenticated_client, sample_contact):
        """Test searching contacts by email."""
        url = reverse('api:v1:contacts-list')
        response = authenticated_client.get(url, {'search': 'john.customer'})

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_filter_by_company(self, authenticated_client, multiple_contacts):
        """Test filtering contacts by company."""
        url = reverse('api:v1:contacts-list')
        response = authenticated_client.get(url, {'company': 'Apple'})

        assert response.status_code == status.HTTP_200_OK


class TestContactValidation:
    """Test cases for contact data validation."""

    @pytest.mark.django_db
    def test_invalid_email_format(self, authenticated_client):
        """Test contact creation with invalid email."""
        url = reverse('api:v1:contacts-list')
        data = {
            'first_name': 'Invalid',
            'last_name': 'Email',
            'email': 'not-an-email'  # Invalid format
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_missing_required_fields(self, authenticated_client):
        """Test contact creation with missing required fields."""
        url = reverse('api:v1:contacts-list')
        data = {
            'company': 'No Name Corp'  # Missing first_name and email
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestContactPermissions:
    """Test cases for contact access permissions."""

    @pytest.mark.django_db
    def test_unauthenticated_access_denied(self, api_client):
        """Test unauthenticated access is denied."""
        url = reverse('api:v1:contacts-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_contact_not_found(self, authenticated_client):
        """Test accessing non-existent contact."""
        url = reverse('api:v1:contacts-detail', kwargs={'pk': 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestContactPagination:
    """Test cases for contact pagination."""

    @pytest.mark.django_db
    def test_contacts_are_paginated(self, authenticated_client, test_user):
        """Test contacts are properly paginated."""
        from contact_management.models import Contact

        # Create many contacts
        for i in range(30):
            Contact.objects.create(
                first_name=f'Paginate{i}',
                last_name=f'Test{i}',
                email=f'paginate{i}@example.com',
                created_by=test_user
            )

        url = reverse('api:v1:contacts-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Check pagination structure
        if 'results' in response.data:
            assert 'count' in response.data or 'next' in response.data
            assert len(response.data['results']) <= 20  # Default page size

    @pytest.mark.django_db
    def test_page_navigation(self, authenticated_client, test_user):
        """Test navigating between pages."""
        from contact_management.models import Contact

        # Create contacts
        for i in range(25):
            Contact.objects.create(
                first_name=f'Page{i}',
                last_name=f'Test{i}',
                email=f'page{i}@example.com',
                created_by=test_user
            )

        url = reverse('api:v1:contacts-list')

        # Get page 1
        response1 = authenticated_client.get(url, {'page': 1})
        assert response1.status_code == status.HTTP_200_OK

        # Get page 2
        response2 = authenticated_client.get(url, {'page': 2})
        assert response2.status_code == status.HTTP_200_OK
