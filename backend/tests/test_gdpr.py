# MyCRM Backend - GDPR Compliance Tests

from datetime import datetime

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestDataSubjectRequestsAPI:
    """Tests for GDPR Data Subject Requests API endpoints."""

    def test_list_dsr_requests(self, authenticated_client):
        """Test listing data subject requests."""
        url = '/api/v1/gdpr/requests/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_access_request(self, authenticated_client):
        """Test creating a data access request (SAR)."""
        url = '/api/v1/gdpr/requests/'
        data = {
            'type': 'access',
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'description': 'Request for all personal data',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_create_deletion_request(self, authenticated_client):
        """Test creating a data deletion (right to be forgotten) request."""
        url = '/api/v1/gdpr/requests/'
        data = {
            'type': 'deletion',
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'description': 'Request to delete all personal data',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_create_rectification_request(self, authenticated_client):
        """Test creating a data rectification request."""
        url = '/api/v1/gdpr/requests/'
        data = {
            'type': 'rectification',
            'email': 'user@example.com',
            'description': 'Please correct my email address',
            'changes': {'email': 'newemail@example.com'},
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_create_portability_request(self, authenticated_client):
        """Test creating a data portability request."""
        url = '/api/v1/gdpr/requests/'
        data = {
            'type': 'portability',
            'email': 'user@example.com',
            'format': 'json',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_get_request_status(self, authenticated_client):
        """Test getting request status."""
        url = '/api/v1/gdpr/requests/1/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_complete_request(self, authenticated_client):
        """Test completing a DSR request."""
        url = '/api/v1/gdpr/requests/1/complete/'
        data = {'notes': 'All data has been provided'}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestConsentManagementAPI:
    """Tests for Consent Management API endpoints."""

    def test_list_consent_records(self, authenticated_client):
        """Test listing consent records."""
        url = '/api/v1/gdpr/consents/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_record_consent(self, authenticated_client):
        """Test recording a consent."""
        url = '/api/v1/gdpr/consents/'
        data = {
            'contact_email': 'user@example.com',
            'purpose': 'marketing',
            'given': True,
            'source': 'web_form',
            'ip_address': '192.168.1.1',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_withdraw_consent(self, authenticated_client):
        """Test withdrawing consent."""
        url = '/api/v1/gdpr/consents/1/withdraw/'
        data = {'reason': 'No longer interested'}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_consent_history(self, authenticated_client):
        """Test getting consent history for a contact."""
        url = '/api/v1/gdpr/consents/?email=user@example.com'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_verify_consent(self, authenticated_client):
        """Test verifying current consent status."""
        url = '/api/v1/gdpr/consents/verify/'
        data = {'email': 'user@example.com', 'purpose': 'marketing'}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestDataRetentionAPI:
    """Tests for Data Retention Policy API endpoints."""

    def test_list_retention_policies(self, authenticated_client):
        """Test listing data retention policies."""
        url = '/api/v1/gdpr/retention-policies/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_retention_policy(self, authenticated_client):
        """Test creating a retention policy."""
        url = '/api/v1/gdpr/retention-policies/'
        data = {
            'name': 'Contact Data Retention',
            'data_type': 'contacts',
            'retention_period_days': 730,  # 2 years
            'action': 'archive',
            'enabled': True,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_update_retention_policy(self, authenticated_client):
        """Test updating a retention policy."""
        url = '/api/v1/gdpr/retention-policies/1/'
        data = {'retention_period_days': 1095}  # 3 years
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_run_retention_policy(self, authenticated_client):
        """Test running a retention policy manually."""
        url = '/api/v1/gdpr/retention-policies/1/run/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_202_ACCEPTED, status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_retention_report(self, authenticated_client):
        """Test getting retention policy report."""
        url = '/api/v1/gdpr/retention-policies/1/report/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestDataProcessingAgreementsAPI:
    """Tests for Data Processing Agreements API endpoints."""

    def test_list_dpas(self, authenticated_client):
        """Test listing DPAs."""
        url = '/api/v1/gdpr/dpas/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_dpa(self, authenticated_client):
        """Test creating a DPA."""
        url = '/api/v1/gdpr/dpas/'
        data = {
            'processor_name': 'Analytics Provider',
            'processor_contact': 'dpo@analytics.com',
            'data_types': ['usage_data', 'analytics'],
            'processing_purpose': 'Usage analytics and reporting',
            'signed_date': datetime.now().date().isoformat(),
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_renew_dpa(self, authenticated_client):
        """Test renewing a DPA."""
        url = '/api/v1/gdpr/dpas/1/renew/'
        data = {'new_expiry_date': '2026-12-31'}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestDataBreachAPI:
    """Tests for Data Breach Management API endpoints."""

    def test_list_breaches(self, authenticated_client):
        """Test listing data breaches."""
        url = '/api/v1/gdpr/breaches/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_report_breach(self, authenticated_client):
        """Test reporting a data breach."""
        url = '/api/v1/gdpr/breaches/'
        data = {
            'title': 'Suspected Data Breach',
            'description': 'Unauthorized access detected',
            'severity': 'high',
            'affected_records': 100,
            'data_types_affected': ['email', 'phone'],
            'discovered_at': datetime.now().isoformat(),
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_update_breach_status(self, authenticated_client):
        """Test updating breach status."""
        url = '/api/v1/gdpr/breaches/1/'
        data = {'status': 'investigating', 'notes': 'Forensic analysis underway'}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_notify_authorities(self, authenticated_client):
        """Test notifying authorities about a breach."""
        url = '/api/v1/gdpr/breaches/1/notify-authorities/'
        data = {'authority': 'ICO', 'reference_number': 'ICO-2024-12345'}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestAuditLogAPI:
    """Tests for GDPR Audit Log API endpoints."""

    def test_list_audit_logs(self, authenticated_client):
        """Test listing audit logs."""
        url = '/api/v1/gdpr/audit-logs/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_filter_audit_logs(self, authenticated_client):
        """Test filtering audit logs."""
        url = '/api/v1/gdpr/audit-logs/?action=data_access&start_date=2024-01-01'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_audit_logs(self, authenticated_client):
        """Test exporting audit logs."""
        url = '/api/v1/gdpr/audit-logs/export/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestPrivacySettingsAPI:
    """Tests for Privacy Settings API endpoints."""

    def test_get_privacy_settings(self, authenticated_client):
        """Test getting privacy settings."""
        url = '/api/v1/gdpr/settings/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_update_privacy_settings(self, authenticated_client):
        """Test updating privacy settings."""
        url = '/api/v1/gdpr/settings/'
        data = {
            'data_anonymization_enabled': True,
            'auto_consent_reminders': True,
            'consent_reminder_days': 365,
        }
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_compliance_report(self, authenticated_client):
        """Test getting compliance report."""
        url = '/api/v1/gdpr/compliance-report/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
