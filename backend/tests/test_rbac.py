"""
Unit tests for Role-Based Access Control (RBAC) Hardening
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from multi_tenant.models import Organization, OrganizationMember
from multi_tenant.middleware import reset_tenant_context
from lead_management.models import Lead

User = get_user_model()


@pytest.mark.django_db
class TestRBACPermissions:
    """Rigorous tests verifying RBAC matrix across endpoints and actions"""

    def setup_method(self):
        reset_tenant_context()
        self.org = Organization.objects.create(slug="rbac-test-org", name="RBAC Test Org", status="active")

        self.users = {}
        self.clients = {}

        for role in ['owner', 'admin', 'manager', 'member', 'viewer']:
            u = User.objects.create_user(username=f"user_{role}", email=f"{role}@test.local", password="password")
            OrganizationMember.objects.create(organization=self.org, user=u, role=role, is_active=True)
            self.users[role] = u

            token = str(RefreshToken.for_user(u).access_token)
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}', HTTP_X_ORGANIZATION_SLUG=self.org.slug)
            self.clients[role] = client

        # Create leads
        self.lead_admin = Lead.objects.create(
            first_name="AdminLead",
            last_name="Test",
            company_name="CorpAdmin",
            organization=self.org,
            owner=self.users['admin'],
            estimated_value=1000.00
        )
        self.lead_member = Lead.objects.create(
            first_name="MemberLead",
            last_name="Test",
            company_name="CorpMember",
            organization=self.org,
            owner=self.users['member'],
            assigned_to=self.users['member'],
            estimated_value=2000.00
        )

    def teardown_method(self):
        reset_tenant_context()

    def test_viewer_read_only_and_create_rejected(self):
        """Viewer has read access but cannot create resources"""
        # List permitted
        res_list = self.clients['viewer'].get('/api/v1/leads/')
        assert res_list.status_code == status.HTTP_200_OK

        # Create rejected
        res_create = self.clients['viewer'].post('/api/v1/leads/', {
            'first_name': 'Bad',
            'last_name': 'Lead',
            'company_name': 'ViewerBadCo',
            'email': 'bad@test.local'
        }, format='json')
        assert res_create.status_code == status.HTTP_403_FORBIDDEN
        assert "cannot perform action 'create'" in res_create.json().get('detail', '')

    def test_member_row_level_isolation(self):
        """Member can only view and update their own/assigned resources"""
        # Member listing only shows their lead
        res_list = self.clients['member'].get('/api/v1/leads/')
        assert res_list.status_code == status.HTTP_200_OK
        results = res_list.json().get('results', [])
        assert len(results) == 1
        assert results[0]['id'] == self.lead_member.id

        # Update own lead permitted
        res_update = self.clients['member'].patch(f'/api/v1/leads/{self.lead_member.id}/', {
            'company_name': 'RenamedCo'
        }, format='json')
        assert res_update.status_code == status.HTTP_200_OK

        # Update admin's lead rejected
        res_update_admin = self.clients['member'].patch(f'/api/v1/leads/{self.lead_admin.id}/', {
            'company_name': 'Hijacked'
        }, format='json')
        assert res_update_admin.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_manager_bulk_update_allowed_bulk_delete_rejected(self):
        """Manager can bulk update but cannot bulk delete"""
        # Bulk update allowed
        res_upd = self.clients['manager'].post('/api/v1/leads/bulk_update/', {
            'ids': [self.lead_member.id],
            'action': 'update',
            'data': {'company_name': 'ManagerUpdated'}
        }, format='json')
        assert res_upd.status_code == status.HTTP_200_OK

        # Bulk delete rejected
        res_del = self.clients['manager'].post('/api/v1/leads/bulk_update/', {
            'ids': [self.lead_member.id],
            'action': 'delete'
        }, format='json')
        assert res_del.status_code == status.HTTP_403_FORBIDDEN
        assert "cannot perform bulk delete" in res_del.json().get('detail', '')

    def test_admin_bulk_delete_allowed(self):
        """Admin can execute bulk delete"""
        res_del = self.clients['admin'].post('/api/v1/leads/bulk_update/', {
            'ids': [self.lead_member.id],
            'action': 'delete'
        }, format='json')
        assert res_del.status_code == status.HTTP_200_OK
        assert not Lead.objects.filter(id=self.lead_member.id).exists()

    def test_export_role_scoping(self):
        """Export is forbidden for viewer/member and allowed for manager/admin/owner"""
        assert self.clients['viewer'].get('/api/v1/export/leads/').status_code == status.HTTP_403_FORBIDDEN
        assert self.clients['member'].get('/api/v1/export/leads/').status_code == status.HTTP_403_FORBIDDEN
        assert self.clients['manager'].get('/api/v1/export/leads/').status_code == status.HTTP_200_OK
        assert self.clients['admin'].get('/api/v1/export/leads/').status_code == status.HTTP_200_OK
