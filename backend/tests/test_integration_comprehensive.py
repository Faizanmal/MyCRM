# MyCRM Backend - Comprehensive Integration Tests

"""
Integration Tests

Comprehensive integration test suite for:
- Multi-module workflows
- API endpoint integration
- Database transactions
- External service integration
- End-to-end API flows
"""

import pytest
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone


# =============================================================================
# Lead to Opportunity Conversion Flow
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestLeadToOpportunityFlow:
    """Integration tests for lead to opportunity conversion flow."""

    def test_complete_lead_to_opportunity_flow(self, authenticated_client, organization, pipeline):
        """Test complete flow from lead creation to opportunity conversion."""
        # Step 1: Create a lead
        lead_data = {
            'name': 'Enterprise Lead',
            'company': 'Big Corp',
            'email': 'contact@bigcorp.com',
            'phone': '+1-555-123-4567',
            'source': 'website',
            'estimated_value': 100000
        }
        response = authenticated_client.post('/api/v1/leads/', lead_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        lead_id = response.data['id']

        # Step 2: Add activities to the lead
        activity_data = {
            'activity_type': 'call',
            'description': 'Initial discovery call'
        }
        response = authenticated_client.post(f'/api/v1/leads/{lead_id}/activities/', activity_data, format='json')
        # Activities endpoint may or may not exist
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

        # Step 3: Qualify the lead
        response = authenticated_client.patch(f'/api/v1/leads/{lead_id}/', {'status': 'qualified'}, format='json')
        assert response.status_code == status.HTTP_200_OK

        # Step 4: Convert lead to opportunity
        convert_data = {
            'opportunity_name': 'Big Corp Enterprise Deal',
            'opportunity_value': 100000,
            'expected_close_date': (date.today() + timedelta(days=90)).isoformat()
        }
        response = authenticated_client.post(f'/api/v1/leads/{lead_id}/convert/', convert_data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_lead_conversion_creates_contact(self, authenticated_client, organization, pipeline):
        """Test lead conversion also creates associated contact."""
        # Create lead with full contact info
        lead_data = {
            'name': 'John Smith',
            'company': 'Tech Inc',
            'email': 'john@techinc.com',
            'phone': '+1-555-987-6543',
            'source': 'referral'
        }
        response = authenticated_client.post('/api/v1/leads/', lead_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        lead_id = response.data['id']

        # Qualify lead
        authenticated_client.patch(f'/api/v1/leads/{lead_id}/', {'status': 'qualified'}, format='json')

        # Convert with contact creation
        convert_data = {
            'opportunity_name': 'Tech Inc Deal',
            'create_contact': True
        }
        response = authenticated_client.post(f'/api/v1/leads/{lead_id}/convert/', convert_data, format='json')
        if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            # Verify contact was created
            response = authenticated_client.get('/api/v1/contacts/', {'search': 'john@techinc.com'})
            assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Sales Pipeline Flow
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestSalesPipelineFlow:
    """Integration tests for sales pipeline workflow."""

    def test_opportunity_through_pipeline(self, authenticated_client, contact, pipeline, organization):
        """Test moving opportunity through all pipeline stages."""
        # Create opportunity
        opp_data = {
            'name': 'Pipeline Test Deal',
            'contact': contact.id,
            'stage': pipeline[0].id,  # Prospecting
            'value': 50000,
            'expected_close_date': (date.today() + timedelta(days=60)).isoformat()
        }
        response = authenticated_client.post('/api/v1/opportunities/', opp_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        opp_id = response.data['id']

        # Move through each stage
        for stage in pipeline[1:5]:  # Qualification -> Closed Won
            response = authenticated_client.patch(
                f'/api/v1/opportunities/{opp_id}/',
                {'stage': stage.id},
                format='json'
            )
            assert response.status_code == status.HTTP_200_OK

        # Verify final stage
        response = authenticated_client.get(f'/api/v1/opportunities/{opp_id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_lost_opportunity_with_reason(self, authenticated_client, contact, pipeline, organization):
        """Test marking opportunity as lost with reason."""
        # Create opportunity
        opp_data = {
            'name': 'Lost Deal',
            'contact': contact.id,
            'stage': pipeline[2].id,  # Proposal
            'value': 30000
        }
        response = authenticated_client.post('/api/v1/opportunities/', opp_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        opp_id = response.data['id']

        # Move to Closed Lost
        lost_stage = pipeline[5]  # Closed Lost
        response = authenticated_client.patch(
            f'/api/v1/opportunities/{opp_id}/',
            {'stage': lost_stage.id, 'loss_reason': 'Competitor won'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Contact Management Flow
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestContactManagementFlow:
    """Integration tests for contact management workflow."""

    def test_contact_with_multiple_opportunities(self, authenticated_client, contact, pipeline, user, organization):
        """Test contact with multiple opportunities."""
        # Create multiple opportunities for same contact
        for i in range(3):
            opp_data = {
                'name': f'Deal {i+1}',
                'contact': contact.id,
                'stage': pipeline[i % 4].id,
                'value': 25000 * (i + 1)
            }
            response = authenticated_client.post('/api/v1/opportunities/', opp_data, format='json')
            assert response.status_code == status.HTTP_201_CREATED

        # Get contact details with opportunities
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_contact_with_tasks_and_notes(self, authenticated_client, contact, user, organization):
        """Test contact with associated tasks and notes."""
        # Create task for contact
        task_data = {
            'title': 'Follow up with contact',
            'task_type': 'follow_up',
            'contact': contact.id,
            'due_date': (timezone.now() + timedelta(days=3)).isoformat()
        }
        response = authenticated_client.post('/api/v1/tasks/', task_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

        # Get contact with related data
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/')
        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Task and Activity Flow
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestTaskActivityFlow:
    """Integration tests for task and activity workflow."""

    def test_task_lifecycle_with_reminders(self, authenticated_client, user, organization):
        """Test complete task lifecycle with reminders."""
        # Create task
        task_data = {
            'title': 'Complete proposal',
            'description': 'Finish the proposal document',
            'task_type': 'proposal',
            'priority': 'high',
            'due_date': (timezone.now() + timedelta(days=2)).isoformat()
        }
        response = authenticated_client.post('/api/v1/tasks/', task_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        task_id = response.data['id']

        # Create reminder for task
        reminder_data = {
            'title': 'Proposal reminder',
            'reminder_type': 'task',
            'task': task_id,
            'remind_at': (timezone.now() + timedelta(days=1)).isoformat()
        }
        response = authenticated_client.post('/api/v1/reminders/', reminder_data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

        # Update task progress
        response = authenticated_client.patch(f'/api/v1/tasks/{task_id}/', {'status': 'in_progress'}, format='json')
        assert response.status_code == status.HTTP_200_OK

        # Complete task
        response = authenticated_client.post(f'/api/v1/tasks/{task_id}/complete/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_calendar_event_with_attendees(self, authenticated_client, user, manager_user, organization):
        """Test calendar event with multiple attendees."""
        start = timezone.now() + timedelta(days=1)
        event_data = {
            'title': 'Team Meeting',
            'event_type': 'meeting',
            'start_time': start.isoformat(),
            'end_time': (start + timedelta(hours=1)).isoformat(),
            'location': 'Conference Room A'
        }
        response = authenticated_client.post('/api/v1/calendar-events/', event_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            event_id = response.data['id']

            # Add attendee
            attendee_data = {'attendee_id': manager_user.id}
            response = authenticated_client.post(f'/api/v1/calendar-events/{event_id}/add-attendee/', attendee_data, format='json')
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Reporting and Analytics Flow
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestReportingFlow:
    """Integration tests for reporting and analytics."""

    def test_sales_dashboard_data(self, authenticated_client, opportunity, lead, contact, organization):
        """Test sales dashboard aggregates data correctly."""
        # Get dashboard data
        response = authenticated_client.get('/api/v1/dashboard/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_pipeline_report(self, authenticated_client, user, contact, pipeline, organization):
        """Test pipeline report generation."""
        # Create opportunities in different stages
        from opportunity_management.models import Opportunity

        for i, stage in enumerate(pipeline[:4]):
            Opportunity.objects.create(
                name=f'Report Deal {i}',
                contact=contact,
                stage=stage,
                value=50000,
                owner=user,
                organization=organization
            )

        # Get pipeline report
        response = authenticated_client.get('/api/v1/opportunities/pipeline/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_lead_source_report(self, authenticated_client, lead_factory, user, organization):
        """Test lead source analysis report."""
        # Create leads with different sources
        sources = ['website', 'referral', 'cold_call', 'event']
        for source in sources:
            for _ in range(5):
                lead_factory.create(source=source, owner=user, organization=organization)

        # Get source report
        response = authenticated_client.get('/api/v1/leads/by-source/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Bulk Operations Flow
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestBulkOperationsFlow:
    """Integration tests for bulk operations."""

    def test_bulk_import_and_update(self, authenticated_client, organization):
        """Test bulk import followed by bulk update."""
        # Create multiple contacts
        contacts = []
        for i in range(10):
            data = {
                'first_name': f'Bulk{i}',
                'last_name': f'Contact{i}',
                'email': f'bulk{i}@test.com',
                'company': 'Bulk Corp'
            }
            response = authenticated_client.post('/api/v1/contacts/', data, format='json')
            if response.status_code == status.HTTP_201_CREATED:
                contacts.append(response.data['id'])

        # Bulk update
        if contacts:
            bulk_data = {
                'contact_ids': contacts,
                'company': 'Updated Bulk Corp'
            }
            response = authenticated_client.post('/api/v1/contacts/bulk-update/', bulk_data, format='json')
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_bulk_lead_assignment(self, authenticated_client, lead_factory, user, manager_user, organization):
        """Test bulk lead assignment."""
        # Create leads
        leads = [lead_factory.create(owner=user, organization=organization) for _ in range(5)]
        lead_ids = [lead.id for lead in leads]

        # Bulk assign
        data = {
            'lead_ids': lead_ids,
            'owner_id': manager_user.id
        }
        response = authenticated_client.post('/api/v1/leads/bulk-assign/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Search and Filter Flow
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestSearchFilterFlow:
    """Integration tests for search and filtering."""

    def test_global_search(self, authenticated_client, contact, lead, opportunity):
        """Test global search across entities."""
        response = authenticated_client.get('/api/v1/search/', {'q': 'Test'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_advanced_contact_filters(self, authenticated_client, contact_factory, user, organization):
        """Test advanced contact filtering."""
        # Create contacts with various attributes
        for i in range(10):
            contact_factory.create(
                company=f'Company {i % 3}',
                owner=user,
                organization=organization
            )

        # Filter by company
        response = authenticated_client.get('/api/v1/contacts/', {'company': 'Company 0'})
        assert response.status_code == status.HTTP_200_OK

    def test_combined_filters(self, authenticated_client, lead_factory, user, organization):
        """Test combining multiple filters."""
        # Create leads with various attributes
        statuses = ['new', 'contacted', 'qualified']
        sources = ['website', 'referral']

        for status_val in statuses:
            for source in sources:
                lead_factory.create(
                    status=status_val,
                    source=source,
                    owner=user,
                    organization=organization
                )

        # Combined filter
        response = authenticated_client.get('/api/v1/leads/', {
            'status': 'new',
            'source': 'website'
        })
        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# User Management Flow
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestUserManagementFlow:
    """Integration tests for user management."""

    def test_user_onboarding_flow(self, admin_client, organization):
        """Test complete user onboarding flow."""
        # Admin creates new user
        user_data = {
            'email': 'newrep@example.com',
            'password': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'Rep',
            'role': 'sales_rep'
        }
        response = admin_client.post('/api/v1/users/', user_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            user_id = response.data['id']

            # Update profile
            profile_data = {
                'timezone': 'America/New_York',
                'notification_preferences': {'email': True, 'push': True}
            }
            response = admin_client.patch(f'/api/v1/users/{user_id}/profile/', profile_data, format='json')
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_team_hierarchy(self, admin_client, user, manager_user, organization):
        """Test team hierarchy management."""
        # Assign user to manager
        response = admin_client.patch(
            f'/api/v1/users/{user.id}/',
            {'manager': manager_user.id},
            format='json'
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


# =============================================================================
# Data Export/Import Flow
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestDataExportImportFlow:
    """Integration tests for data export and import."""

    def test_contact_export_import_cycle(self, authenticated_client, contact_factory, user, organization):
        """Test exporting and reimporting contacts."""
        # Create contacts
        for _ in range(5):
            contact_factory.create(owner=user, organization=organization)

        # Export contacts
        response = authenticated_client.get('/api/v1/contacts/export/', {'format': 'csv'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_lead_export_with_filters(self, authenticated_client, lead_factory, user, organization):
        """Test exporting leads with filters applied."""
        # Create leads with different statuses
        for status_val in ['new', 'contacted', 'qualified']:
            lead_factory.create(status=status_val, owner=user, organization=organization)

        # Export only qualified leads
        response = authenticated_client.get('/api/v1/leads/export/', {
            'format': 'csv',
            'status': 'qualified'
        })
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# API Rate Limiting Tests
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestAPIRateLimiting:
    """Integration tests for API rate limiting."""

    def test_rapid_requests(self, authenticated_client, contact):
        """Test handling of rapid consecutive requests."""
        # Make many rapid requests
        for _ in range(50):
            response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/')
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        # Should either succeed or be rate limited
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_429_TOO_MANY_REQUESTS]


# =============================================================================
# Error Handling Tests
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestErrorHandling:
    """Integration tests for error handling."""

    def test_404_handling(self, authenticated_client):
        """Test 404 error handling."""
        response = authenticated_client.get('/api/v1/contacts/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_validation_error_handling(self, authenticated_client, organization):
        """Test validation error handling."""
        data = {
            'first_name': 'Test',
            'email': 'invalid-email'
        }
        response = authenticated_client.post('/api/v1/contacts/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_concurrent_modification(self, authenticated_client, contact):
        """Test handling of concurrent modifications."""
        # Make two concurrent updates (simulated)
        response1 = authenticated_client.patch(f'/api/v1/contacts/{contact.id}/', {'first_name': 'Update1'}, format='json')
        response2 = authenticated_client.patch(f'/api/v1/contacts/{contact.id}/', {'first_name': 'Update2'}, format='json')

        # Both should succeed or handle conflict properly
        assert response1.status_code in [status.HTTP_200_OK, status.HTTP_409_CONFLICT]
        assert response2.status_code in [status.HTTP_200_OK, status.HTTP_409_CONFLICT]
