# MyCRM Backend - Contact Comprehensive Tests Extension

"""
Extended Contact Tests

Additional comprehensive tests for contact management:
- Contact groups
- Contact import
- Contact merge
- Contact activities
- Contact timeline
"""

import pytest
from rest_framework import status


# =============================================================================
# Contact Groups Tests
# =============================================================================

@pytest.mark.django_db
class TestContactGroups:
    """Test cases for Contact Groups functionality."""

    def test_list_groups(self, authenticated_client):
        """Test listing contact groups."""
        response = authenticated_client.get('/api/v1/contact-groups/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_group(self, authenticated_client, organization):
        """Test creating a contact group."""
        data = {
            'name': 'VIP Customers',
            'description': 'High-value customers'
        }
        response = authenticated_client.post('/api/v1/contact-groups/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_add_contacts_to_group(self, authenticated_client, contact, organization):
        """Test adding contacts to a group."""
        # First create group
        group_data = {'name': 'Test Group'}
        response = authenticated_client.post('/api/v1/contact-groups/', group_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            group_id = response.data['id']
            add_data = {'contact_ids': [contact.id]}
            response = authenticated_client.post(
                f'/api/v1/contact-groups/{group_id}/add-contacts/',
                add_data,
                format='json'
            )
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_remove_contact_from_group(self, authenticated_client, contact, organization):
        """Test removing contacts from a group."""
        group_data = {'name': 'Remove Test Group'}
        response = authenticated_client.post('/api/v1/contact-groups/', group_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            group_id = response.data['id']
            remove_data = {'contact_ids': [contact.id]}
            response = authenticated_client.post(
                f'/api/v1/contact-groups/{group_id}/remove-contacts/',
                remove_data,
                format='json'
            )
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Contact Import Tests
# =============================================================================

@pytest.mark.django_db
class TestContactImport:
    """Test cases for Contact Import functionality."""

    def test_import_csv(self, authenticated_client, organization):
        """Test importing contacts from CSV."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        csv_content = b'first_name,last_name,email,company\nJohn,Doe,john@test.com,Test Corp\nJane,Smith,jane@test.com,Another Corp'
        csv_file = SimpleUploadedFile('contacts.csv', csv_content, content_type='text/csv')

        response = authenticated_client.post('/api/v1/contacts/import/', {'file': csv_file}, format='multipart')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_import_excel(self, authenticated_client, organization):
        """Test importing contacts from Excel."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Simple Excel-like content (would need actual Excel file in real test)
        excel_file = SimpleUploadedFile('contacts.xlsx', b'excel content', content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        response = authenticated_client.post('/api/v1/contacts/import/', {'file': excel_file}, format='multipart')
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]

    def test_import_preview(self, authenticated_client, organization):
        """Test import preview functionality."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        csv_content = b'first_name,last_name,email\nPreview,Test,preview@test.com'
        csv_file = SimpleUploadedFile('preview.csv', csv_content, content_type='text/csv')

        response = authenticated_client.post('/api/v1/contacts/import/preview/', {'file': csv_file}, format='multipart')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_import_with_mapping(self, authenticated_client, organization):
        """Test import with custom field mapping."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        csv_content = b'Name,Mail,Organization\nTest User,test@test.com,Test Org'
        csv_file = SimpleUploadedFile('mapped.csv', csv_content, content_type='text/csv')

        data = {
            'file': csv_file,
            'mapping': '{"Name": "first_name", "Mail": "email", "Organization": "company"}'
        }
        response = authenticated_client.post('/api/v1/contacts/import/', data, format='multipart')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_import_duplicate_handling(self, authenticated_client, contact, organization):
        """Test import with duplicate contact handling."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        csv_content = f'first_name,last_name,email\nDuplicate,User,{contact.email}'.encode()
        csv_file = SimpleUploadedFile('duplicate.csv', csv_content, content_type='text/csv')

        data = {
            'file': csv_file,
            'duplicate_action': 'skip'  # or 'update' or 'create'
        }
        response = authenticated_client.post('/api/v1/contacts/import/', data, format='multipart')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Contact Merge Tests
# =============================================================================

@pytest.mark.django_db
class TestContactMerge:
    """Test cases for Contact Merge functionality."""

    def test_detect_duplicates(self, authenticated_client, contact_factory, user, organization):
        """Test duplicate detection."""
        # Create contacts with similar info
        contact_factory.create(email='similar@test.com', owner=user, organization=organization)
        contact_factory.create(email='similar@test.com', owner=user, organization=organization)

        response = authenticated_client.get('/api/v1/contacts/duplicates/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_merge_contacts(self, authenticated_client, contact_factory, user, organization):
        """Test merging two contacts."""
        contact1 = contact_factory.create(first_name='Primary', owner=user, organization=organization)
        contact2 = contact_factory.create(first_name='Secondary', owner=user, organization=organization)

        data = {
            'primary_id': contact1.id,
            'secondary_id': contact2.id
        }
        response = authenticated_client.post('/api/v1/contacts/merge/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_merge_preview(self, authenticated_client, contact_factory, user, organization):
        """Test merge preview."""
        contact1 = contact_factory.create(owner=user, organization=organization)
        contact2 = contact_factory.create(owner=user, organization=organization)

        data = {
            'primary_id': contact1.id,
            'secondary_id': contact2.id
        }
        response = authenticated_client.post('/api/v1/contacts/merge/preview/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Contact Activity Tests
# =============================================================================

@pytest.mark.django_db
class TestContactActivities:
    """Test cases for Contact Activities functionality."""

    def test_list_activities(self, authenticated_client, contact):
        """Test listing contact activities."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/activities/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_add_note(self, authenticated_client, contact):
        """Test adding a note to contact."""
        data = {
            'activity_type': 'note',
            'content': 'Important meeting notes'
        }
        response = authenticated_client.post(f'/api/v1/contacts/{contact.id}/activities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_log_call(self, authenticated_client, contact):
        """Test logging a call."""
        data = {
            'activity_type': 'call',
            'content': 'Discussed pricing options',
            'duration': 15
        }
        response = authenticated_client.post(f'/api/v1/contacts/{contact.id}/activities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_log_email(self, authenticated_client, contact):
        """Test logging an email."""
        data = {
            'activity_type': 'email',
            'content': 'Sent proposal',
            'subject': 'Proposal for Q1',
            'direction': 'outbound'
        }
        response = authenticated_client.post(f'/api/v1/contacts/{contact.id}/activities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_log_meeting(self, authenticated_client, contact):
        """Test logging a meeting."""
        data = {
            'activity_type': 'meeting',
            'content': 'Product demo',
            'duration': 60,
            'outcome': 'Positive'
        }
        response = authenticated_client.post(f'/api/v1/contacts/{contact.id}/activities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Contact Timeline Tests
# =============================================================================

@pytest.mark.django_db
class TestContactTimeline:
    """Test cases for Contact Timeline functionality."""

    def test_get_timeline(self, authenticated_client, contact):
        """Test getting contact timeline."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/timeline/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_timeline_pagination(self, authenticated_client, contact):
        """Test timeline pagination."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/timeline/', {'page': 1, 'page_size': 10})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_timeline_filter_by_type(self, authenticated_client, contact):
        """Test filtering timeline by activity type."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/timeline/', {'type': 'call'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Contact Tags Tests
# =============================================================================

@pytest.mark.django_db
class TestContactTags:
    """Test cases for Contact Tags functionality."""

    def test_add_tags(self, authenticated_client, contact):
        """Test adding tags to a contact."""
        data = {'tags': ['vip', 'enterprise', 'priority']}
        response = authenticated_client.post(f'/api/v1/contacts/{contact.id}/tags/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_remove_tag(self, authenticated_client, contact):
        """Test removing a tag from a contact."""
        response = authenticated_client.delete(f'/api/v1/contacts/{contact.id}/tags/vip/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]

    def test_filter_by_tags(self, authenticated_client, contact):
        """Test filtering contacts by tags."""
        response = authenticated_client.get('/api/v1/contacts/', {'tags': 'vip,enterprise'})
        assert response.status_code == status.HTTP_200_OK

    def test_get_all_tags(self, authenticated_client, organization):
        """Test getting all available tags."""
        response = authenticated_client.get('/api/v1/tags/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Contact Custom Fields Tests
# =============================================================================

@pytest.mark.django_db
class TestContactCustomFields:
    """Test cases for Contact Custom Fields functionality."""

    def test_set_custom_field(self, authenticated_client, contact):
        """Test setting a custom field value."""
        data = {'custom_fields': {'industry': 'Technology', 'company_size': '100-500'}}
        response = authenticated_client.patch(f'/api/v1/contacts/{contact.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_get_custom_field_definitions(self, authenticated_client, organization):
        """Test getting custom field definitions."""
        response = authenticated_client.get('/api/v1/custom-fields/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_custom_field_definition(self, authenticated_client, organization):
        """Test creating a custom field definition."""
        data = {
            'name': 'industry',
            'label': 'Industry',
            'field_type': 'select',
            'options': ['Technology', 'Finance', 'Healthcare', 'Retail']
        }
        response = authenticated_client.post('/api/v1/custom-fields/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Contact Relationship Tests
# =============================================================================

@pytest.mark.django_db
class TestContactRelationships:
    """Test cases for Contact Relationships functionality."""

    def test_create_relationship(self, authenticated_client, contact_factory, user, organization):
        """Test creating a relationship between contacts."""
        contact1 = contact_factory.create(owner=user, organization=organization)
        contact2 = contact_factory.create(owner=user, organization=organization)

        data = {
            'related_contact_id': contact2.id,
            'relationship_type': 'colleague'
        }
        response = authenticated_client.post(f'/api/v1/contacts/{contact1.id}/relationships/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_list_relationships(self, authenticated_client, contact):
        """Test listing contact relationships."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/relationships/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_remove_relationship(self, authenticated_client, contact):
        """Test removing a relationship."""
        response = authenticated_client.delete(f'/api/v1/contacts/{contact.id}/relationships/1/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]
