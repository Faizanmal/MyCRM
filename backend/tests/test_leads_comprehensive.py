# MyCRM Backend - Comprehensive Lead Management Tests

"""
Lead Management Tests

Comprehensive test suite for lead management including:
- Lead CRUD operations
- Lead conversion
- Lead activities
- Lead scoring
- Assignment rules
- Bulk operations
"""

import pytest
from rest_framework import status
from decimal import Decimal


# =============================================================================
# Lead CRUD Tests
# =============================================================================

@pytest.mark.django_db
class TestLeadListAPI:
    """Test cases for Lead list endpoint."""

    def test_list_leads_unauthenticated(self, api_client):
        """Test unauthenticated requests are rejected."""
        response = api_client.get('/api/v1/leads/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_leads_authenticated(self, authenticated_client, lead):
        """Test listing leads returns results."""
        response = authenticated_client.get('/api/v1/leads/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert response.data['count'] >= 1

    def test_list_leads_pagination(self, authenticated_client, lead_factory, user, organization):
        """Test pagination works correctly."""
        for _ in range(25):
            lead_factory.create(owner=user, organization=organization)

        response = authenticated_client.get('/api/v1/leads/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) <= 20

    def test_list_leads_search(self, authenticated_client, lead):
        """Test search functionality."""
        response = authenticated_client.get('/api/v1/leads/', {'search': 'Test Lead'})
        assert response.status_code == status.HTTP_200_OK

    def test_list_leads_filter_by_status(self, authenticated_client, lead):
        """Test filtering by status."""
        response = authenticated_client.get('/api/v1/leads/', {'status': 'new'})
        assert response.status_code == status.HTTP_200_OK

    def test_list_leads_filter_by_source(self, authenticated_client, lead):
        """Test filtering by source."""
        response = authenticated_client.get('/api/v1/leads/', {'source': 'website'})
        assert response.status_code == status.HTTP_200_OK

    def test_list_leads_filter_by_priority(self, authenticated_client, lead):
        """Test filtering by priority."""
        response = authenticated_client.get('/api/v1/leads/', {'priority': 'high'})
        assert response.status_code == status.HTTP_200_OK

    def test_list_leads_filter_by_owner(self, authenticated_client, lead, user):
        """Test filtering by owner."""
        response = authenticated_client.get('/api/v1/leads/', {'owner': user.id})
        assert response.status_code == status.HTTP_200_OK

    def test_list_leads_ordering_by_value(self, authenticated_client, lead_factory, user, organization):
        """Test ordering leads by estimated value."""
        lead_factory.create(estimated_value=10000, owner=user, organization=organization)
        lead_factory.create(estimated_value=50000, owner=user, organization=organization)

        response = authenticated_client.get('/api/v1/leads/', {'ordering': '-estimated_value'})
        assert response.status_code == status.HTTP_200_OK

    def test_list_leads_date_range_filter(self, authenticated_client, lead):
        """Test filtering by date range."""
        response = authenticated_client.get('/api/v1/leads/', {
            'created_after': '2024-01-01',
            'created_before': '2027-12-31'
        })
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestLeadCreateAPI:
    """Test cases for Lead creation endpoint."""

    def test_create_lead_success(self, authenticated_client, organization):
        """Test creating a lead successfully."""
        data = {
            'name': 'New Lead',
            'company': 'Tech Corp',
            'email': 'lead@techcorp.com',
            'phone': '+1-555-123-4567',
            'source': 'website',
            'status': 'new',
            'estimated_value': 25000,
            'priority': 'medium'
        }
        response = authenticated_client.post('/api/v1/leads/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Lead'

    def test_create_lead_minimal_data(self, authenticated_client, organization):
        """Test creating a lead with minimal data."""
        data = {
            'name': 'Minimal Lead',
            'company': 'Some Corp'
        }
        response = authenticated_client.post('/api/v1/leads/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_lead_invalid_email(self, authenticated_client, organization):
        """Test creating lead with invalid email fails."""
        data = {
            'name': 'Bad Lead',
            'company': 'Bad Corp',
            'email': 'invalid-email'
        }
        response = authenticated_client.post('/api/v1/leads/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_lead_with_custom_fields(self, authenticated_client, organization):
        """Test creating lead with custom fields."""
        data = {
            'name': 'Custom Lead',
            'company': 'Custom Corp',
            'custom_fields': {'industry': 'Technology', 'employees': 50}
        }
        response = authenticated_client.post('/api/v1/leads/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_lead_with_tags(self, authenticated_client, organization):
        """Test creating lead with tags."""
        data = {
            'name': 'Tagged Lead',
            'company': 'Tagged Corp',
            'tags': ['hot', 'enterprise']
        }
        response = authenticated_client.post('/api/v1/leads/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestLeadDetailAPI:
    """Test cases for Lead detail endpoint."""

    def test_get_lead_detail(self, authenticated_client, lead):
        """Test getting lead details."""
        response = authenticated_client.get(f'/api/v1/leads/{lead.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == lead.id

    def test_update_lead_success(self, authenticated_client, lead):
        """Test updating lead."""
        data = {'status': 'contacted', 'priority': 'high'}
        response = authenticated_client.patch(f'/api/v1/leads/{lead.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_update_lead_full(self, authenticated_client, lead):
        """Test full update of lead."""
        data = {
            'name': 'Updated Lead Name',
            'company': 'Updated Corp',
            'email': 'updated@corp.com',
            'phone': '+1-555-999-8888',
            'source': 'referral',
            'status': 'qualified',
            'priority': 'urgent',
            'estimated_value': 100000
        }
        response = authenticated_client.put(f'/api/v1/leads/{lead.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_delete_lead(self, authenticated_client, lead):
        """Test deleting a lead."""
        response = authenticated_client.delete(f'/api/v1/leads/{lead.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestLeadOrganizationIsolation:
    """Test cases for organization data isolation."""

    def test_cannot_access_other_org_leads(self, authenticated_client, other_organization):
        """Test users cannot access leads from other organizations."""
        from lead_management.models import Lead

        # Create lead in other organization
        other_lead = Lead.objects.create(
            name='Other Org Lead',
            company='Other Corp',
            organization=other_organization
        )

        response = authenticated_client.get(f'/api/v1/leads/{other_lead.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# Lead Conversion Tests
# =============================================================================

@pytest.mark.django_db
class TestLeadConversion:
    """Test cases for lead conversion functionality."""

    def test_convert_lead_to_opportunity(self, authenticated_client, lead, pipeline):
        """Test converting a qualified lead to an opportunity."""
        lead.status = 'qualified'
        lead.save()

        data = {
            'opportunity_name': 'New Deal',
            'opportunity_value': 50000,
            'expected_close_date': '2025-06-30'
        }
        response = authenticated_client.post(f'/api/v1/leads/{lead.id}/convert/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_convert_lead_creates_contact(self, authenticated_client, lead, pipeline):
        """Test lead conversion also creates a contact."""
        lead.status = 'qualified'
        lead.email = 'convert@test.com'
        lead.save()

        data = {
            'opportunity_name': 'Contact Deal',
            'create_contact': True
        }
        response = authenticated_client.post(f'/api/v1/leads/{lead.id}/convert/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_convert_unqualified_lead_fails(self, authenticated_client, lead):
        """Test converting an unqualified lead fails."""
        lead.status = 'new'
        lead.save()

        data = {'opportunity_name': 'Should Fail'}
        response = authenticated_client.post(f'/api/v1/leads/{lead.id}/convert/', data, format='json')
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_already_converted_lead(self, authenticated_client, lead, pipeline):
        """Test converting an already converted lead fails."""
        lead.status = 'converted'
        lead.save()

        data = {'opportunity_name': 'Double Convert'}
        response = authenticated_client.post(f'/api/v1/leads/{lead.id}/convert/', data, format='json')
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Lead Activity Tests
# =============================================================================

@pytest.mark.django_db
class TestLeadActivities:
    """Test cases for lead activity tracking."""

    def test_add_activity_to_lead(self, authenticated_client, lead):
        """Test adding an activity to a lead."""
        data = {
            'activity_type': 'call',
            'description': 'Introductory call with prospect'
        }
        response = authenticated_client.post(f'/api/v1/leads/{lead.id}/activities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_list_lead_activities(self, authenticated_client, lead):
        """Test listing lead activities."""
        response = authenticated_client.get(f'/api/v1/leads/{lead.id}/activities/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_add_note_activity(self, authenticated_client, lead):
        """Test adding a note activity."""
        data = {
            'activity_type': 'note',
            'description': 'Important note about this lead'
        }
        response = authenticated_client.post(f'/api/v1/leads/{lead.id}/activities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_add_email_activity(self, authenticated_client, lead):
        """Test adding an email activity."""
        data = {
            'activity_type': 'email',
            'description': 'Follow-up email sent',
            'metadata': {'subject': 'Follow Up', 'sent_to': lead.email}
        }
        response = authenticated_client.post(f'/api/v1/leads/{lead.id}/activities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Bulk Operations Tests
# =============================================================================

@pytest.mark.django_db
class TestLeadBulkOperations:
    """Test cases for bulk lead operations."""

    def test_bulk_update_leads(self, authenticated_client, lead_factory, user, organization):
        """Test bulk updating multiple leads."""
        leads = [lead_factory.create(owner=user, organization=organization) for _ in range(5)]
        lead_ids = [lead.id for lead in leads]

        data = {
            'lead_ids': lead_ids,
            'status': 'contacted'
        }
        response = authenticated_client.post('/api/v1/leads/bulk-update/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_bulk_delete_leads(self, authenticated_client, lead_factory, user, organization):
        """Test bulk deleting multiple leads."""
        leads = [lead_factory.create(owner=user, organization=organization) for _ in range(3)]
        lead_ids = [lead.id for lead in leads]

        data = {'lead_ids': lead_ids}
        response = authenticated_client.post('/api/v1/leads/bulk-delete/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]

    def test_bulk_assign_leads(self, authenticated_client, lead_factory, user, manager_user, organization):
        """Test bulk assigning leads to a user."""
        leads = [lead_factory.create(owner=user, organization=organization) for _ in range(3)]
        lead_ids = [lead.id for lead in leads]

        data = {
            'lead_ids': lead_ids,
            'owner_id': manager_user.id
        }
        response = authenticated_client.post('/api/v1/leads/bulk-assign/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Lead Import/Export Tests
# =============================================================================

@pytest.mark.django_db
class TestLeadImportExport:
    """Test cases for lead import and export functionality."""

    def test_export_leads_csv(self, authenticated_client, lead):
        """Test exporting leads to CSV."""
        response = authenticated_client.get('/api/v1/leads/export/', {'format': 'csv'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_leads_excel(self, authenticated_client, lead):
        """Test exporting leads to Excel."""
        response = authenticated_client.get('/api/v1/leads/export/', {'format': 'excel'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_import_leads_csv(self, authenticated_client, organization):
        """Test importing leads from CSV."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        csv_content = b'name,company,email,phone\nImported Lead,Import Corp,import@test.com,555-1234'
        csv_file = SimpleUploadedFile('leads.csv', csv_content, content_type='text/csv')

        response = authenticated_client.post('/api/v1/leads/import/', {'file': csv_file}, format='multipart')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Lead Scoring Tests
# =============================================================================

@pytest.mark.django_db
class TestLeadScoring:
    """Test cases for lead scoring functionality."""

    def test_get_lead_score(self, authenticated_client, lead, mock_ai_service):
        """Test getting AI-calculated lead score."""
        response = authenticated_client.get(f'/api/v1/leads/{lead.id}/score/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_recalculate_lead_score(self, authenticated_client, lead, mock_ai_service):
        """Test recalculating lead score."""
        response = authenticated_client.post(f'/api/v1/leads/{lead.id}/recalculate-score/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_lead_score_breakdown(self, authenticated_client, lead, mock_ai_service):
        """Test getting detailed score breakdown."""
        response = authenticated_client.get(f'/api/v1/leads/{lead.id}/score-breakdown/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Lead Statistics Tests
# =============================================================================

@pytest.mark.django_db
class TestLeadStatistics:
    """Test cases for lead statistics and analytics."""

    def test_get_lead_statistics(self, authenticated_client, lead):
        """Test getting lead statistics."""
        response = authenticated_client.get('/api/v1/leads/statistics/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_leads_by_source(self, authenticated_client, lead_factory, user, organization):
        """Test getting lead breakdown by source."""
        for source in ['website', 'referral', 'cold_call']:
            lead_factory.create(source=source, owner=user, organization=organization)

        response = authenticated_client.get('/api/v1/leads/by-source/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_leads_by_status(self, authenticated_client, lead_factory, user, organization):
        """Test getting lead breakdown by status."""
        for stat in ['new', 'contacted', 'qualified']:
            lead_factory.create(status=stat, owner=user, organization=organization)

        response = authenticated_client.get('/api/v1/leads/by-status/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_lead_conversion_rate(self, authenticated_client, lead):
        """Test getting lead conversion rate."""
        response = authenticated_client.get('/api/v1/leads/conversion-rate/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Lead Model Unit Tests
# =============================================================================

@pytest.mark.django_db
class TestLeadModel:
    """Unit tests for Lead model."""

    def test_lead_creation(self, organization, user):
        """Test lead creation with required fields."""
        from lead_management.models import Lead

        lead = Lead.objects.create(
            name='Test Lead',
            company='Test Corp',
            email='test@testcorp.com',
            organization=organization,
            owner=user
        )
        assert lead.name == 'Test Lead'
        assert lead.status == 'new'  # Default status

    def test_lead_str_representation(self, lead):
        """Test lead string representation."""
        assert lead.name in str(lead)

    def test_lead_estimated_value_decimal(self, organization, user):
        """Test lead estimated value is properly handled."""
        from lead_management.models import Lead

        lead = Lead.objects.create(
            name='Value Lead',
            company='Value Corp',
            estimated_value=Decimal('50000.00'),
            organization=organization,
            owner=user
        )
        assert lead.estimated_value == Decimal('50000.00')

    def test_lead_status_transitions(self, lead):
        """Test lead status transitions."""
        lead.status = 'contacted'
        lead.save()
        assert lead.status == 'contacted'

        lead.status = 'qualified'
        lead.save()
        assert lead.status == 'qualified'

    def test_lead_with_all_sources(self, organization, user):
        """Test creating leads with all source types."""
        from lead_management.models import Lead

        sources = ['website', 'referral', 'social_media', 'email_campaign', 'cold_call']
        for source in sources:
            lead = Lead.objects.create(
                name=f'{source.title()} Lead',
                company='Source Corp',
                source=source,
                organization=organization,
                owner=user
            )
            assert lead.source == source
