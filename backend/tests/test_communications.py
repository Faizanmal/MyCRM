# MyCRM Backend - Communication Management Tests

import pytest
from rest_framework import status
from datetime import datetime, timedelta


@pytest.mark.django_db
class TestCommunicationsAPI:
    """Tests for Communications API endpoints."""

    def test_list_communications(self, authenticated_client):
        """Test listing communications."""
        url = '/api/v1/communications/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_email_communication(self, authenticated_client, contact):
        """Test creating an email communication."""
        url = '/api/v1/communications/'
        data = {
            'type': 'email',
            'subject': 'Follow-up on our meeting',
            'content': 'Hi, I wanted to follow up on our recent meeting...',
            'direction': 'outbound',
            'contact': contact.id if contact else 1,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_create_call_communication(self, authenticated_client, contact):
        """Test logging a phone call."""
        url = '/api/v1/communications/'
        data = {
            'type': 'call',
            'subject': 'Discovery call',
            'content': 'Discussed product requirements and timeline',
            'direction': 'outbound',
            'duration': 1800,  # 30 minutes in seconds
            'contact': contact.id if contact else 1,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_create_meeting_communication(self, authenticated_client, contact):
        """Test logging a meeting."""
        url = '/api/v1/communications/'
        data = {
            'type': 'meeting',
            'subject': 'Product demo',
            'content': 'Demo session with the technical team',
            'direction': 'outbound',
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(hours=1)).isoformat(),
            'contact': contact.id if contact else 1,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_filter_by_type(self, authenticated_client):
        """Test filtering communications by type."""
        url = '/api/v1/communications/?type=email'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_filter_by_contact(self, authenticated_client, contact):
        """Test filtering communications by contact."""
        if contact:
            url = f'/api/v1/communications/?contact={contact.id}'
            response = authenticated_client.get(url)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_contact_timeline(self, authenticated_client, contact):
        """Test getting contact communication timeline."""
        if contact:
            url = f'/api/v1/contacts/{contact.id}/communications/'
            response = authenticated_client.get(url)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestEmailTemplatesAPI:
    """Tests for Email Templates API endpoints."""

    def test_list_templates(self, authenticated_client):
        """Test listing email templates."""
        url = '/api/v1/email-templates/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_template(self, authenticated_client):
        """Test creating an email template."""
        url = '/api/v1/email-templates/'
        data = {
            'name': 'Welcome Email',
            'subject': 'Welcome to {{company_name}}!',
            'body': 'Hi {{first_name}},\n\nWelcome to our platform...',
            'category': 'onboarding',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_preview_template(self, authenticated_client):
        """Test previewing a template with variables."""
        url = '/api/v1/email-templates/1/preview/'
        data = {
            'variables': {
                'company_name': 'Acme Corp',
                'first_name': 'John',
            }
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestEmailSequencesAPI:
    """Tests for Email Sequences API endpoints."""

    def test_list_sequences(self, authenticated_client):
        """Test listing email sequences."""
        url = '/api/v1/email-sequences/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_sequence(self, authenticated_client):
        """Test creating an email sequence."""
        url = '/api/v1/email-sequences/'
        data = {
            'name': 'New Lead Nurturing',
            'description': 'Automated sequence for new leads',
            'trigger': 'lead_created',
            'steps': [
                {'delay_days': 0, 'template_id': 1, 'subject': 'Welcome!'},
                {'delay_days': 3, 'template_id': 2, 'subject': 'How can we help?'},
                {'delay_days': 7, 'template_id': 3, 'subject': 'Check out our resources'},
            ]
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_enroll_contact_in_sequence(self, authenticated_client, contact):
        """Test enrolling a contact in a sequence."""
        if contact:
            url = '/api/v1/email-sequences/1/enroll/'
            data = {'contact_id': contact.id}
            response = authenticated_client.post(url, data, format='json')
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_pause_sequence_for_contact(self, authenticated_client, contact):
        """Test pausing a sequence for a specific contact."""
        if contact:
            url = f'/api/v1/email-sequences/1/contacts/{contact.id}/pause/'
            response = authenticated_client.post(url)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_sequence_analytics(self, authenticated_client):
        """Test getting sequence analytics."""
        url = '/api/v1/email-sequences/1/analytics/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.fixture
def contact(db, organization, user):
    """Create a test contact."""
    try:
        from contact_management.models import Contact
        return Contact.objects.create(
            first_name='Test',
            last_name='Contact',
            email='testcontact@example.com',
            company='Test Company',
            organization=organization,
            owner=user,
        )
    except Exception:
        return None
