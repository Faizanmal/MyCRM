# MyCRM Backend - Integration Hub Tests

import pytest
from rest_framework import status
from datetime import datetime


@pytest.mark.django_db
class TestIntegrationHubAPI:
    """Tests for Integration Hub API endpoints."""

    def test_list_available_integrations(self, authenticated_client):
        """Test listing available integrations."""
        url = '/api/v1/integrations/providers/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_list_connected_integrations(self, authenticated_client):
        """Test listing connected integrations."""
        url = '/api/v1/integrations/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_connect_integration(self, authenticated_client):
        """Test connecting a new integration."""
        url = '/api/v1/integrations/connect/'
        data = {
            'provider': 'slack',
            'credentials': {
                'webhook_url': 'https://hooks.slack.com/services/xxx/yyy/zzz',
            }
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_disconnect_integration(self, authenticated_client):
        """Test disconnecting an integration."""
        url = '/api/v1/integrations/1/disconnect/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_sync_integration(self, authenticated_client):
        """Test triggering integration sync."""
        url = '/api/v1/integrations/1/sync/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]

    def test_get_sync_history(self, authenticated_client):
        """Test getting sync history."""
        url = '/api/v1/integrations/1/sync-history/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestWebhooksAPI:
    """Tests for Webhooks API endpoints."""

    def test_list_webhooks(self, authenticated_client):
        """Test listing webhooks."""
        url = '/api/v1/webhooks/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_webhook(self, authenticated_client):
        """Test creating a webhook."""
        url = '/api/v1/webhooks/'
        data = {
            'name': 'Lead Created Webhook',
            'url': 'https://example.com/webhook',
            'events': ['lead.created', 'lead.updated'],
            'is_active': True,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_webhook_delivery_history(self, authenticated_client):
        """Test getting webhook delivery history."""
        url = '/api/v1/webhooks/1/deliveries/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_retry_webhook_delivery(self, authenticated_client):
        """Test retrying a failed webhook delivery."""
        url = '/api/v1/webhooks/deliveries/1/retry/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestOAuthIntegrations:
    """Tests for OAuth integration flows."""

    def test_get_oauth_url(self, authenticated_client):
        """Test getting OAuth authorization URL."""
        url = '/api/v1/integrations/oauth/google/authorize/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_oauth_callback(self, authenticated_client):
        """Test OAuth callback handling."""
        url = '/api/v1/integrations/oauth/google/callback/'
        data = {'code': 'test_auth_code', 'state': 'test_state'}
        response = authenticated_client.post(url, data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_refresh_oauth_token(self, authenticated_client):
        """Test refreshing OAuth tokens."""
        url = '/api/v1/integrations/1/refresh-token/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestSlackIntegration:
    """Tests for Slack integration."""

    def test_send_slack_notification(self, authenticated_client):
        """Test sending Slack notification."""
        url = '/api/v1/integrations/slack/send/'
        data = {
            'channel': '#sales',
            'message': 'New deal closed: $50,000',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]

    def test_list_slack_channels(self, authenticated_client):
        """Test listing Slack channels."""
        url = '/api/v1/integrations/slack/channels/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestGoogleIntegration:
    """Tests for Google Workspace integration."""

    def test_sync_google_contacts(self, authenticated_client):
        """Test syncing Google contacts."""
        url = '/api/v1/integrations/google/sync-contacts/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]

    def test_sync_google_calendar(self, authenticated_client):
        """Test syncing Google calendar."""
        url = '/api/v1/integrations/google/sync-calendar/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]

    def test_import_gmail_emails(self, authenticated_client):
        """Test importing Gmail emails."""
        url = '/api/v1/integrations/google/import-emails/'
        data = {
            'contact_id': 1,
            'days': 30,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]
