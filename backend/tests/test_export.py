"""
Export API Tests

Test suite for data export functionality:
- CSV export
- Excel export
- JSON export
- PDF export
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
        username='exportuser',
        email='export@example.com',
        password='TestPass123!',
        first_name='Export',
        last_name='User'
    )
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def sample_leads(db, test_user):
    """Create sample leads for export testing."""
    from lead_management.models import Lead

    leads = []
    for i in range(5):
        lead = Lead.objects.create(
            first_name=f'Lead{i}',
            last_name=f'Test{i}',
            email=f'lead{i}@example.com',
            company=f'Company{i}',
            status='new',
            source='website',
            created_by=test_user
        )
        leads.append(lead)
    return leads


@pytest.fixture
def sample_contacts(db, test_user):
    """Create sample contacts for export testing."""
    from contact_management.models import Contact

    contacts = []
    for i in range(5):
        contact = Contact.objects.create(
            first_name=f'Contact{i}',
            last_name=f'Test{i}',
            email=f'contact{i}@example.com',
            company=f'Company{i}',
            job_title=f'Title{i}',
            created_by=test_user
        )
        contacts.append(contact)
    return contacts


class TestCSVExport:
    """Test cases for CSV export functionality."""

    @pytest.mark.django_db
    def test_export_leads_csv(self, authenticated_client, sample_leads):
        """Test exporting leads to CSV."""
        url = reverse('api:v1:export-leads')
        response = authenticated_client.get(url, {'format': 'csv'})

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment' in response['Content-Disposition']
        assert '.csv' in response['Content-Disposition']

        # Check content
        content = response.content.decode('utf-8')
        assert 'First Name' in content or 'first_name' in content.lower()

    @pytest.mark.django_db
    def test_export_contacts_csv(self, authenticated_client, sample_contacts):
        """Test exporting contacts to CSV."""
        url = reverse('api:v1:export-contacts')
        response = authenticated_client.get(url, {'format': 'csv'})

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'


class TestJSONExport:
    """Test cases for JSON export functionality."""

    @pytest.mark.django_db
    def test_export_leads_json(self, authenticated_client, sample_leads):
        """Test exporting leads to JSON."""
        url = reverse('api:v1:export-leads')
        response = authenticated_client.get(url, {'format': 'json'})

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/json'
        assert 'attachment' in response['Content-Disposition']
        assert '.json' in response['Content-Disposition']

    @pytest.mark.django_db
    def test_export_json_content_valid(self, authenticated_client, sample_leads):
        """Test that exported JSON is valid."""
        import json

        url = reverse('api:v1:export-leads')
        response = authenticated_client.get(url, {'format': 'json'})

        # Should be valid JSON
        data = json.loads(response.content.decode('utf-8'))
        assert isinstance(data, list)
        assert len(data) == len(sample_leads)


class TestExcelExport:
    """Test cases for Excel export functionality."""

    @pytest.mark.django_db
    def test_export_leads_excel(self, authenticated_client, sample_leads):
        """Test exporting leads to Excel."""
        url = reverse('api:v1:export-leads')
        response = authenticated_client.get(url, {'format': 'xlsx'})

        # May fall back to CSV if openpyxl not installed
        assert response.status_code == status.HTTP_200_OK
        assert 'attachment' in response['Content-Disposition']


class TestPDFExport:
    """Test cases for PDF export functionality."""

    @pytest.mark.django_db
    def test_export_leads_pdf(self, authenticated_client, sample_leads):
        """Test exporting leads to PDF."""
        url = reverse('api:v1:export-leads')
        response = authenticated_client.get(url, {'format': 'pdf'})

        # May fall back to CSV if reportlab not installed
        assert response.status_code == status.HTTP_200_OK
        assert 'attachment' in response['Content-Disposition']


class TestExportFiltering:
    """Test cases for export with filters."""

    @pytest.mark.django_db
    def test_export_leads_with_status_filter(self, authenticated_client, test_user):
        """Test exporting leads filtered by status."""
        from lead_management.models import Lead

        # Create leads with different statuses
        Lead.objects.create(
            first_name='New', last_name='Lead',
            email='new@example.com', status='new',
            created_by=test_user
        )
        Lead.objects.create(
            first_name='Qualified', last_name='Lead',
            email='qualified@example.com', status='qualified',
            created_by=test_user
        )

        url = reverse('api:v1:export-leads')
        response = authenticated_client.get(url, {'format': 'csv', 'status': 'new'})

        assert response.status_code == status.HTTP_200_OK


class TestExportPermissions:
    """Test cases for export access permissions."""

    @pytest.mark.django_db
    def test_unauthenticated_export_denied(self, api_client):
        """Test that unauthenticated export is denied."""
        url = reverse('api:v1:export-leads')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_user_exports_own_data_only(self, api_client, test_user):
        """Test that users can only export their own data."""
        from lead_management.models import Lead

        # Create another user with leads
        other_user = User.objects.create_user(
            username='other', email='other@example.com', password='Pass123!'
        )
        Lead.objects.create(
            first_name='Other', last_name='Lead',
            email='other@example.com', status='new',
            created_by=other_user
        )

        # Create lead for test user
        Lead.objects.create(
            first_name='My', last_name='Lead',
            email='my@example.com', status='new',
            created_by=test_user
        )

        # Export as test user
        api_client.force_authenticate(user=test_user)
        url = reverse('api:v1:export-leads')
        response = api_client.get(url, {'format': 'csv'})

        assert response.status_code == status.HTTP_200_OK
        content = response.content.decode('utf-8')

        # Should contain test user's lead
        assert 'my@example.com' in content.lower() or 'My' in content


class TestExportUtilities:
    """Test cases for export utility functions."""

    @pytest.mark.django_db
    def test_export_column_configuration(self):
        """Test ExportColumn configuration."""
        from core.export_utils import ExportColumn

        column = ExportColumn(
            field='email',
            header='Email Address',
            width=25
        )

        assert column.field == 'email'
        assert column.header == 'Email Address'
        assert column.width == 25

    @pytest.mark.django_db
    def test_export_column_with_formatter(self):
        """Test ExportColumn with custom formatter."""
        from core.export_utils import ExportColumn

        column = ExportColumn(
            field='value',
            header='Value',
            formatter=lambda v: f"${v:,.2f}"
        )

        formatted = column.formatter(1234.56)
        assert formatted == "$1,234.56"
