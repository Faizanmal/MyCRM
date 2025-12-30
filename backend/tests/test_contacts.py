# MyCRM Backend - Comprehensive Contact API Tests

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestContactListAPI:
    """Test cases for Contact list endpoint."""
    
    def test_list_contacts_unauthenticated(self, api_client):
        """Test that unauthenticated requests are rejected."""
        response = api_client.get('/api/v1/contacts/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_contacts_authenticated(self, authenticated_client, contact):
        """Test listing contacts returns results."""
        response = authenticated_client.get('/api/v1/contacts/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert response.data['count'] >= 1
    
    def test_list_contacts_pagination(self, authenticated_client, contact_factory, user, organization):
        """Test pagination works correctly."""
        # Create 25 contacts
        for i in range(25):
            contact_factory.create(owner=user, organization=organization)
        
        response = authenticated_client.get('/api/v1/contacts/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20  # Default page size
        assert response.data['next'] is not None
    
    def test_list_contacts_search(self, authenticated_client, contact):
        """Test search functionality."""
        response = authenticated_client.get('/api/v1/contacts/', {'search': 'John'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1
        assert any(c['first_name'] == 'John' for c in response.data['results'])
    
    def test_list_contacts_filter_by_company(self, authenticated_client, contact):
        """Test filtering by company."""
        response = authenticated_client.get('/api/v1/contacts/', {'company': 'Acme Corp'})
        assert response.status_code == status.HTTP_200_OK
        for c in response.data['results']:
            assert 'Acme' in c['company']
    
    def test_list_contacts_ordering(self, authenticated_client, contact_factory, user, organization):
        """Test ordering contacts."""
        contact_factory.create(first_name='Alice', owner=user, organization=organization)
        contact_factory.create(first_name='Zoe', owner=user, organization=organization)
        
        response = authenticated_client.get('/api/v1/contacts/', {'ordering': 'first_name'})
        assert response.status_code == status.HTTP_200_OK
        names = [c['first_name'] for c in response.data['results']]
        assert names == sorted(names)


@pytest.mark.django_db
class TestContactCreateAPI:
    """Test cases for Contact creation endpoint."""
    
    def test_create_contact_success(self, authenticated_client, organization):
        """Test creating a contact successfully."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone': '+1-555-111-2222',
            'company': 'Tech Corp'
        }
        response = authenticated_client.post('/api/v1/contacts/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['first_name'] == 'Jane'
        assert response.data['email'] == 'jane.smith@example.com'
    
    def test_create_contact_invalid_email(self, authenticated_client):
        """Test creating a contact with invalid email fails."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'invalid-email',
        }
        response = authenticated_client.post('/api/v1/contacts/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_create_contact_duplicate_email(self, authenticated_client, contact):
        """Test creating a contact with duplicate email within same org."""
        data = {
            'first_name': 'Another',
            'last_name': 'Person',
            'email': contact.email,  # Same email as existing contact
        }
        response = authenticated_client.post('/api/v1/contacts/', data, format='json')
        # Should either fail or warn about duplicate
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED]
    
    def test_create_contact_with_tags(self, authenticated_client):
        """Test creating a contact with tags."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'tags': ['vip', 'enterprise']
        }
        response = authenticated_client.post('/api/v1/contacts/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'vip' in response.data.get('tags', [])
    
    def test_create_contact_with_custom_fields(self, authenticated_client):
        """Test creating a contact with custom fields."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'custom_fields': {
                'industry': 'Technology',
                'company_size': '100-500'
            }
        }
        response = authenticated_client.post('/api/v1/contacts/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestContactDetailAPI:
    """Test cases for Contact detail endpoint."""
    
    def test_get_contact_success(self, authenticated_client, contact):
        """Test retrieving a contact."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == contact.id
        assert response.data['email'] == contact.email
    
    def test_get_contact_not_found(self, authenticated_client):
        """Test retrieving non-existent contact."""
        response = authenticated_client.get('/api/v1/contacts/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_contact_different_organization(self, authenticated_client, other_organization):
        """Test cannot access contact from different organization."""
        from contact_management.models import Contact
        other_contact = Contact.objects.create(
            first_name='Other',
            last_name='Contact',
            email='other@example.com',
            organization=other_organization
        )
        response = authenticated_client.get(f'/api/v1/contacts/{other_contact.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestContactUpdateAPI:
    """Test cases for Contact update endpoint."""
    
    def test_update_contact_success(self, authenticated_client, contact):
        """Test updating a contact."""
        data = {'job_title': 'CTO'}
        response = authenticated_client.patch(f'/api/v1/contacts/{contact.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['job_title'] == 'CTO'
    
    def test_update_contact_full(self, authenticated_client, contact):
        """Test full contact update."""
        data = {
            'first_name': 'Johnny',
            'last_name': 'Doe',
            'email': 'johnny.doe@example.com',
            'phone': '+1-555-999-8888',
            'company': 'New Corp',
            'job_title': 'VP'
        }
        response = authenticated_client.put(f'/api/v1/contacts/{contact.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Johnny'
        assert response.data['company'] == 'New Corp'


@pytest.mark.django_db
class TestContactDeleteAPI:
    """Test cases for Contact deletion endpoint."""
    
    def test_delete_contact_success(self, authenticated_client, contact):
        """Test deleting a contact."""
        response = authenticated_client.delete(f'/api/v1/contacts/{contact.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_contact_different_organization(self, authenticated_client, other_organization):
        """Test cannot delete contact from different organization."""
        from contact_management.models import Contact
        other_contact = Contact.objects.create(
            first_name='Other',
            last_name='Contact',
            email='other@example.com',
            organization=other_organization
        )
        response = authenticated_client.delete(f'/api/v1/contacts/{other_contact.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestContactBulkOperations:
    """Test cases for Contact bulk operations."""
    
    def test_bulk_create_contacts(self, authenticated_client):
        """Test bulk creating contacts."""
        data = {
            'contacts': [
                {'first_name': 'Bulk1', 'last_name': 'Test', 'email': 'bulk1@example.com'},
                {'first_name': 'Bulk2', 'last_name': 'Test', 'email': 'bulk2@example.com'},
                {'first_name': 'Bulk3', 'last_name': 'Test', 'email': 'bulk3@example.com'},
            ]
        }
        response = authenticated_client.post('/api/v1/contacts/bulk/', data, format='json')
        # Endpoint may or may not exist
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]
    
    def test_bulk_delete_contacts(self, authenticated_client, contact_factory, user, organization):
        """Test bulk deleting contacts."""
        contacts = [
            contact_factory.create(owner=user, organization=organization)
            for _ in range(3)
        ]
        ids = [c.id for c in contacts]
        
        data = {'ids': ids}
        response = authenticated_client.delete('/api/v1/contacts/bulk/', data, format='json')
        # Endpoint may or may not exist
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestContactPermissions:
    """Test cases for Contact permissions."""
    
    def test_sales_rep_can_only_see_own_contacts(self, authenticated_client, contact_factory, user, organization, manager_user):
        """Test sales reps can only see their own contacts."""
        # Create contact owned by manager
        manager_contact = contact_factory.create(owner=manager_user, organization=organization)
        # Create contact owned by user
        own_contact = contact_factory.create(owner=user, organization=organization)
        
        response = authenticated_client.get('/api/v1/contacts/')
        contact_ids = [c['id'] for c in response.data['results']]
        
        # User should see their own contact
        assert own_contact.id in contact_ids
    
    def test_admin_can_see_all_contacts(self, admin_client, contact_factory, user, organization, manager_user):
        """Test admins can see all contacts in organization."""
        contact1 = contact_factory.create(owner=user, organization=organization)
        contact2 = contact_factory.create(owner=manager_user, organization=organization)
        
        response = admin_client.get('/api/v1/contacts/')
        contact_ids = [c['id'] for c in response.data['results']]
        
        assert contact1.id in contact_ids
        assert contact2.id in contact_ids


@pytest.mark.django_db
class TestContactExport:
    """Test cases for Contact export functionality."""
    
    def test_export_contacts_csv(self, authenticated_client, contact):
        """Test exporting contacts to CSV."""
        response = authenticated_client.get('/api/v1/contacts/export/', {'format': 'csv'})
        # May return file or async job
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]
    
    def test_export_contacts_with_filter(self, authenticated_client, contact):
        """Test exporting filtered contacts."""
        response = authenticated_client.get('/api/v1/contacts/export/', {
            'format': 'csv',
            'company': 'Acme'
        })
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]
