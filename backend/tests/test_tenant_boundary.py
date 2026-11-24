"""
Unit tests for Multi-Tenant Boundary Isolation and Hardening
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from multi_tenant.models import Organization, OrganizationMember
from multi_tenant.middleware import get_current_organization, reset_tenant_context
from lead_management.models import Lead
from contact_management.models import Contact

User = get_user_model()


@pytest.mark.django_db
class TestTenantBoundary:
    """Rigorous tests verifying complete tenant isolation across layers"""

    def setup_method(self):
        reset_tenant_context()
        self.org_a = Organization.objects.create(slug="tenant-a", name="Tenant A", status="active")
        self.org_b = Organization.objects.create(slug="tenant-b", name="Tenant B", status="active")

        self.user_a = User.objects.create_user(username="usera", email="a@example.com", password="password")
        self.user_b = User.objects.create_user(username="userb", email="b@example.com", password="password")

        OrganizationMember.objects.create(organization=self.org_a, user=self.user_a, role="member", is_active=True)
        OrganizationMember.objects.create(organization=self.org_b, user=self.user_b, role="member", is_active=True)

        self.token_a = str(RefreshToken.for_user(self.user_a).access_token)
        self.token_b = str(RefreshToken.for_user(self.user_b).access_token)

        self.client_a = APIClient()
        self.client_a.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}', HTTP_X_ORGANIZATION_SLUG='tenant-a')

        self.client_b = APIClient()
        self.client_b.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_b}', HTTP_X_ORGANIZATION_SLUG='tenant-b')

    def teardown_method(self):
        reset_tenant_context()

    def test_cross_tenant_header_rejection(self):
        """User from Org A cannot access API with X-Organization-Slug for Org B"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_a}', HTTP_X_ORGANIZATION_SLUG='tenant-b')
        response = client.get('/api/v1/leads/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json().get('code') == 'tenant_forbidden'

    def test_direct_object_access_cross_tenant_hidden(self):
        """Querying an object belonging to Org B by ID from Org A yields 404 (does not exist in tenant)"""
        lead_b = Lead.objects.create(
            first_name="Target",
            last_name="LeadB",
            company_name="Corp B",
            organization=self.org_b,
            owner=self.user_b,
            estimated_value=1500.00
        )

        response = self.client_a.get(f'/api/v1/leads/{lead_b.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_bulk_update_cross_tenant_rejection(self):
        """Bulk update containing any cross-tenant ID fails and leaves foreign records untouched"""
        lead_a = Lead.objects.create(
            first_name="Lead",
            last_name="A",
            company_name="Alpha",
            organization=self.org_a,
            owner=self.user_a,
            estimated_value=1000.00
        )
        lead_b = Lead.objects.create(
            first_name="Lead",
            last_name="B",
            company_name="Beta",
            organization=self.org_b,
            owner=self.user_b,
            estimated_value=2000.00
        )

        response = self.client_a.post('/api/v1/leads/bulk_update/', {
            'ids': [lead_a.id, lead_b.id],
            'action': 'update',
            'data': {'company_name': 'Tampered'}
        }, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        lead_b.refresh_from_db()
        assert lead_b.company_name == "Beta"

    def test_export_data_does_not_leak_other_tenants(self):
        """CSV export only includes records of the caller's organization"""
        Lead.objects.create(first_name="AliceA", last_name="A", company_name="CorpA", organization=self.org_a, owner=self.user_a, estimated_value=500.00)
        Lead.objects.create(first_name="BobB", last_name="B", company_name="CorpB", organization=self.org_b, owner=self.user_b, estimated_value=600.00)

        response = self.client_a.get('/api/v1/export/leads/')
        assert response.status_code == status.HTTP_200_OK
        content = response.content.decode('utf-8')
        assert "AliceA" in content
        assert "BobB" not in content
