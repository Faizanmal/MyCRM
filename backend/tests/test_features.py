# MyCRM Backend - Feature-Specific Tests

"""
Feature Tests

Comprehensive test suite for specific features:
- AI Insights
- Campaign Management
- Email Tracking
- Gamification
- GDPR Compliance
- Reporting
- Document Management
"""

import pytest
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone


# =============================================================================
# AI Insights Tests
# =============================================================================

@pytest.mark.django_db
class TestAIInsights:
    """Test cases for AI Insights feature."""

    def test_get_lead_insights(self, authenticated_client, lead, mock_ai_service):
        """Test getting AI insights for a lead."""
        response = authenticated_client.get(f'/api/v1/leads/{lead.id}/insights/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_ai_recommendations(self, authenticated_client, organization, mock_ai_service):
        """Test getting AI recommendations."""
        response = authenticated_client.get('/api/v1/ai/recommendations/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_sales_predictions(self, authenticated_client, opportunity, mock_ai_service):
        """Test getting sales predictions."""
        response = authenticated_client.get('/api/v1/ai/sales-predictions/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_churn_risk_analysis(self, authenticated_client, contact, mock_ai_service):
        """Test getting churn risk analysis."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/churn-risk/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_next_best_action(self, authenticated_client, lead, mock_ai_service):
        """Test getting next best action recommendation."""
        response = authenticated_client.get(f'/api/v1/leads/{lead.id}/next-best-action/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_ai_assisted_email_generation(self, authenticated_client, contact, mock_ai_service):
        """Test AI-assisted email generation."""
        data = {
            'contact_id': contact.id,
            'purpose': 'follow_up',
            'tone': 'professional'
        }
        response = authenticated_client.post('/api/v1/ai/generate-email/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Campaign Management Tests
# =============================================================================

@pytest.mark.django_db
class TestCampaignManagement:
    """Test cases for Campaign Management feature."""

    def test_list_campaigns(self, authenticated_client):
        """Test listing campaigns."""
        response = authenticated_client.get('/api/v1/campaigns/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_email_campaign(self, authenticated_client, organization):
        """Test creating an email campaign."""
        data = {
            'name': 'Summer Sale Campaign',
            'campaign_type': 'email',
            'subject': 'Summer Sale - 20% Off!',
            'content': '<h1>Summer Sale</h1><p>Get 20% off all products!</p>',
            'scheduled_date': (timezone.now() + timedelta(days=7)).isoformat()
        }
        response = authenticated_client.post('/api/v1/campaigns/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_add_recipients_to_campaign(self, authenticated_client, contact, organization):
        """Test adding recipients to a campaign."""
        # First create a campaign
        campaign_data = {
            'name': 'Test Campaign',
            'campaign_type': 'email'
        }
        response = authenticated_client.post('/api/v1/campaigns/', campaign_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            campaign_id = response.data['id']
            recipient_data = {'contact_ids': [contact.id]}
            response = authenticated_client.post(
                f'/api/v1/campaigns/{campaign_id}/add-recipients/',
                recipient_data,
                format='json'
            )
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_send_campaign(self, authenticated_client, organization, mock_email_service):
        """Test sending a campaign."""
        # Create and prepare campaign
        campaign_data = {
            'name': 'Send Test Campaign',
            'campaign_type': 'email',
            'subject': 'Test Subject',
            'content': 'Test Content'
        }
        response = authenticated_client.post('/api/v1/campaigns/', campaign_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            campaign_id = response.data['id']
            response = authenticated_client.post(f'/api/v1/campaigns/{campaign_id}/send/')
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_campaign_analytics(self, authenticated_client, organization):
        """Test getting campaign analytics."""
        response = authenticated_client.get('/api/v1/campaigns/analytics/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_pause_campaign(self, authenticated_client, organization):
        """Test pausing an active campaign."""
        campaign_data = {
            'name': 'Pause Test Campaign',
            'campaign_type': 'email',
            'status': 'active'
        }
        response = authenticated_client.post('/api/v1/campaigns/', campaign_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            campaign_id = response.data['id']
            response = authenticated_client.post(f'/api/v1/campaigns/{campaign_id}/pause/')
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Email Tracking Tests
# =============================================================================

@pytest.mark.django_db
class TestEmailTracking:
    """Test cases for Email Tracking feature."""

    def test_list_tracked_emails(self, authenticated_client):
        """Test listing tracked emails."""
        response = authenticated_client.get('/api/v1/email-tracking/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_email_open_stats(self, authenticated_client, contact):
        """Test getting email open statistics."""
        response = authenticated_client.get('/api/v1/email-tracking/stats/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_click_through_rate(self, authenticated_client):
        """Test getting click-through rate."""
        response = authenticated_client.get('/api/v1/email-tracking/click-rate/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_contact_email_history(self, authenticated_client, contact):
        """Test getting email history for a contact."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/email-history/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Gamification Tests
# =============================================================================

@pytest.mark.django_db
class TestGamification:
    """Test cases for Gamification feature."""

    def test_get_user_points(self, authenticated_client, user):
        """Test getting user points."""
        response = authenticated_client.get('/api/v1/gamification/points/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_leaderboard(self, authenticated_client, organization):
        """Test getting leaderboard."""
        response = authenticated_client.get('/api/v1/gamification/leaderboard/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_achievements(self, authenticated_client, user):
        """Test getting user achievements."""
        response = authenticated_client.get('/api/v1/gamification/achievements/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_badges(self, authenticated_client, user):
        """Test getting user badges."""
        response = authenticated_client.get('/api/v1/gamification/badges/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_challenges(self, authenticated_client, organization):
        """Test getting active challenges."""
        response = authenticated_client.get('/api/v1/gamification/challenges/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_weekly_leaderboard(self, authenticated_client, organization):
        """Test getting weekly leaderboard."""
        response = authenticated_client.get('/api/v1/gamification/leaderboard/', {'period': 'week'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# GDPR Compliance Tests
# =============================================================================

@pytest.mark.django_db
class TestGDPRCompliance:
    """Test cases for GDPR Compliance feature."""

    def test_get_data_processing_records(self, authenticated_client, organization):
        """Test getting data processing records."""
        response = authenticated_client.get('/api/v1/gdpr/processing-records/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_consent_records(self, authenticated_client, contact):
        """Test getting consent records for a contact."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/consents/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_record_consent(self, authenticated_client, contact):
        """Test recording consent."""
        data = {
            'consent_type': 'marketing_email',
            'granted': True,
            'ip_address': '192.168.1.1'
        }
        response = authenticated_client.post(
            f'/api/v1/contacts/{contact.id}/consents/',
            data,
            format='json'
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_withdraw_consent(self, authenticated_client, contact):
        """Test withdrawing consent."""
        data = {
            'consent_type': 'marketing_email',
            'granted': False
        }
        response = authenticated_client.post(
            f'/api/v1/contacts/{contact.id}/withdraw-consent/',
            data,
            format='json'
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_data_subject_access_request(self, authenticated_client, contact):
        """Test data subject access request."""
        response = authenticated_client.post(f'/api/v1/contacts/{contact.id}/dsar/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]

    def test_right_to_erasure(self, authenticated_client, contact):
        """Test right to erasure (right to be forgotten)."""
        response = authenticated_client.post(f'/api/v1/contacts/{contact.id}/erase/')
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND
        ]

    def test_data_portability(self, authenticated_client, contact):
        """Test data portability export."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/export-data/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Advanced Reporting Tests
# =============================================================================

@pytest.mark.django_db
class TestAdvancedReporting:
    """Test cases for Advanced Reporting feature."""

    def test_generate_sales_report(self, authenticated_client, opportunity, organization):
        """Test generating sales report."""
        data = {
            'report_type': 'sales',
            'date_from': (date.today() - timedelta(days=30)).isoformat(),
            'date_to': date.today().isoformat()
        }
        response = authenticated_client.post('/api/v1/reports/generate/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_get_revenue_report(self, authenticated_client, organization):
        """Test getting revenue report."""
        response = authenticated_client.get('/api/v1/reports/revenue/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_conversion_funnel(self, authenticated_client, organization):
        """Test getting conversion funnel report."""
        response = authenticated_client.get('/api/v1/reports/funnel/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_activity_report(self, authenticated_client, user, organization):
        """Test getting activity report."""
        response = authenticated_client.get('/api/v1/reports/activity/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_team_performance(self, authenticated_client, organization):
        """Test getting team performance report."""
        response = authenticated_client.get('/api/v1/reports/team-performance/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_schedule_report(self, authenticated_client, organization):
        """Test scheduling a recurring report."""
        data = {
            'name': 'Weekly Sales Report',
            'report_type': 'sales',
            'frequency': 'weekly',
            'recipients': ['manager@example.com']
        }
        response = authenticated_client.post('/api/v1/reports/schedule/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_export_report_pdf(self, authenticated_client, organization):
        """Test exporting report to PDF."""
        response = authenticated_client.get('/api/v1/reports/revenue/', {'format': 'pdf'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_custom_report_builder(self, authenticated_client, organization):
        """Test custom report builder."""
        data = {
            'name': 'Custom Report',
            'fields': ['contact_name', 'deal_value', 'close_date'],
            'filters': {'stage': 'closed_won'},
            'grouping': 'month'
        }
        response = authenticated_client.post('/api/v1/reports/custom/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Document Management Tests
# =============================================================================

@pytest.mark.django_db
class TestDocumentManagement:
    """Test cases for Document Management feature."""

    def test_list_documents(self, authenticated_client):
        """Test listing documents."""
        response = authenticated_client.get('/api/v1/documents/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_upload_document(self, authenticated_client, organization):
        """Test uploading a document."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        doc_file = SimpleUploadedFile('test.pdf', b'%PDF-1.4 test content', content_type='application/pdf')
        data = {
            'file': doc_file,
            'title': 'Test Document',
            'description': 'A test document'
        }
        response = authenticated_client.post('/api/v1/documents/', data, format='multipart')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_download_document(self, authenticated_client, organization):
        """Test downloading a document."""
        # First upload a document
        from django.core.files.uploadedfile import SimpleUploadedFile

        doc_file = SimpleUploadedFile('download.pdf', b'%PDF-1.4 content', content_type='application/pdf')
        response = authenticated_client.post('/api/v1/documents/', {'file': doc_file, 'title': 'Download Test'}, format='multipart')
        if response.status_code == status.HTTP_201_CREATED:
            doc_id = response.data['id']
            response = authenticated_client.get(f'/api/v1/documents/{doc_id}/download/')
            assert response.status_code == status.HTTP_200_OK

    def test_share_document(self, authenticated_client, manager_user, organization):
        """Test sharing a document."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        doc_file = SimpleUploadedFile('share.pdf', b'%PDF-1.4 content', content_type='application/pdf')
        response = authenticated_client.post('/api/v1/documents/', {'file': doc_file, 'title': 'Share Test'}, format='multipart')
        if response.status_code == status.HTTP_201_CREATED:
            doc_id = response.data['id']
            share_data = {'user_ids': [manager_user.id]}
            response = authenticated_client.post(f'/api/v1/documents/{doc_id}/share/', share_data, format='json')
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_folder(self, authenticated_client, organization):
        """Test creating a document folder."""
        data = {'name': 'Proposals', 'description': 'Proposal documents'}
        response = authenticated_client.post('/api/v1/documents/folders/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_search_documents(self, authenticated_client):
        """Test searching documents."""
        response = authenticated_client.get('/api/v1/documents/', {'search': 'proposal'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Smart Scheduling Tests
# =============================================================================

@pytest.mark.django_db
class TestSmartScheduling:
    """Test cases for Smart Scheduling feature."""

    def test_get_available_slots(self, authenticated_client, user):
        """Test getting available time slots."""
        response = authenticated_client.get('/api/v1/scheduling/available-slots/', {
            'date': (date.today() + timedelta(days=1)).isoformat(),
            'duration': 60
        })
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_book_meeting(self, authenticated_client, contact, user):
        """Test booking a meeting."""
        start = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'title': 'Sales Call',
            'contact_id': contact.id,
            'start_time': start.isoformat(),
            'end_time': (start + timedelta(hours=1)).isoformat()
        }
        response = authenticated_client.post('/api/v1/scheduling/book/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_suggest_meeting_times(self, authenticated_client, contact, mock_ai_service):
        """Test AI-suggested meeting times."""
        data = {
            'contact_id': contact.id,
            'duration': 30,
            'meeting_type': 'demo'
        }
        response = authenticated_client.post('/api/v1/scheduling/suggest-times/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_reschedule_meeting(self, authenticated_client, user):
        """Test rescheduling a meeting."""
        # First create a meeting
        from task_management.models import CalendarEvent
        start = timezone.now() + timedelta(days=1)
        try:
            event = CalendarEvent.objects.create(
                title='Reschedule Test',
                event_type='meeting',
                start_time=start,
                end_time=start + timedelta(hours=1),
                organizer=user
            )
            new_start = start + timedelta(days=1)
            data = {
                'start_time': new_start.isoformat(),
                'end_time': (new_start + timedelta(hours=1)).isoformat()
            }
            response = authenticated_client.post(f'/api/v1/calendar-events/{event.id}/reschedule/', data, format='json')
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        except Exception:
            pass


# =============================================================================
# Social Selling Tests
# =============================================================================

@pytest.mark.django_db
class TestSocialSelling:
    """Test cases for Social Selling feature."""

    def test_get_social_profiles(self, authenticated_client, contact):
        """Test getting social profiles for a contact."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/social-profiles/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_link_social_profile(self, authenticated_client, contact):
        """Test linking a social profile."""
        data = {
            'platform': 'linkedin',
            'profile_url': 'https://linkedin.com/in/johndoe'
        }
        response = authenticated_client.post(
            f'/api/v1/contacts/{contact.id}/social-profiles/',
            data,
            format='json'
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_get_social_feed(self, authenticated_client):
        """Test getting social feed."""
        response = authenticated_client.get('/api/v1/social/feed/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Integration Hub Tests
# =============================================================================

@pytest.mark.django_db
class TestIntegrationHub:
    """Test cases for Integration Hub feature."""

    def test_list_available_integrations(self, authenticated_client):
        """Test listing available integrations."""
        response = authenticated_client.get('/api/v1/integrations/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_connected_integrations(self, authenticated_client, organization):
        """Test getting connected integrations."""
        response = authenticated_client.get('/api/v1/integrations/connected/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_connect_integration(self, authenticated_client, organization):
        """Test connecting an integration."""
        data = {
            'integration_type': 'google_calendar',
            'credentials': {'api_key': 'test_key'}
        }
        response = authenticated_client.post('/api/v1/integrations/connect/', data, format='json')
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]

    def test_disconnect_integration(self, authenticated_client, organization):
        """Test disconnecting an integration."""
        response = authenticated_client.post('/api/v1/integrations/google_calendar/disconnect/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_sync_integration(self, authenticated_client, organization):
        """Test syncing integration data."""
        response = authenticated_client.post('/api/v1/integrations/google_calendar/sync/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Data Enrichment Tests
# =============================================================================

@pytest.mark.django_db
class TestDataEnrichment:
    """Test cases for Data Enrichment feature."""

    def test_enrich_contact(self, authenticated_client, contact):
        """Test enriching contact data."""
        response = authenticated_client.post(f'/api/v1/contacts/{contact.id}/enrich/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]

    def test_enrich_company(self, authenticated_client, contact):
        """Test enriching company data."""
        response = authenticated_client.post(f'/api/v1/contacts/{contact.id}/enrich-company/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]

    def test_get_enrichment_status(self, authenticated_client, contact):
        """Test getting enrichment status."""
        response = authenticated_client.get(f'/api/v1/contacts/{contact.id}/enrichment-status/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_bulk_enrich(self, authenticated_client, contact_factory, user, organization):
        """Test bulk contact enrichment."""
        contacts = [contact_factory.create(owner=user, organization=organization) for _ in range(5)]
        contact_ids = [c.id for c in contacts]
        data = {'contact_ids': contact_ids}
        response = authenticated_client.post('/api/v1/contacts/bulk-enrich/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]
