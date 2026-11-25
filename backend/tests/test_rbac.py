"""
Comprehensive Unit & Integration Test Suite for Role-Based Access Control (RBAC) Hardening
========================================================================================
Validates:
1. Parameterized Role Matrix across roles (owner, admin, manager, member, sales_rep, viewer, guest)
   and actions (list, retrieve, create, update, destroy, convert, complete, bulk_update, bulk_delete, export, merge).
2. Forbidden Fields Enforcement: rejection with HTTP 403 Forbidden and explicit missing permission explanation.
3. Row-Level Isolation under Pagination, Search, and Aggregations (statistics, pipeline).
4. Adversarial Scenarios: wrong-tenant, insufficient-role, anonymous, malformed payload, kill-switch / feature flag toggles.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from multi_tenant.models import Organization, OrganizationMember
from multi_tenant.middleware import reset_tenant_context
from lead_management.models import Lead
from contact_management.models import Contact
from opportunity_management.models import Opportunity
from task_management.models import Task

User = get_user_model()


@pytest.mark.django_db
class TestRBACParameterizedMatrix:
    """Rigorous tests verifying RBAC matrix across endpoints and actions"""

    def setup_method(self):
        reset_tenant_context()
        self.org_a = Organization.objects.create(slug="rbac-org-a", name="RBAC Tenant A", status="active")
        self.org_b = Organization.objects.create(slug="rbac-org-b", name="RBAC Tenant B", status="active")

        self.roles = ['owner', 'admin', 'manager', 'member', 'sales_rep', 'viewer', 'guest']
        self.users = {}
        self.clients = {}

        for role in self.roles:
            u = User.objects.create_user(
                username=f"rbac_{role}",
                email=f"{role}@rbac.test",
                password="testpassword123"
            )
            # Guest has inactive or minimal membership
            is_active = (role != 'guest')
            OrganizationMember.objects.create(
                organization=self.org_a,
                user=u,
                role=role,
                is_active=is_active
            )
            self.users[role] = u

            token = str(RefreshToken.for_user(u).access_token)
            client = APIClient()
            client.credentials(
                HTTP_AUTHORIZATION=f'Bearer {token}',
                HTTP_X_ORGANIZATION_SLUG=self.org_a.slug
            )
            self.clients[role] = client

        # Create Leads in Org A:
        # Lead 1: Owned by Admin
        self.lead_admin = Lead.objects.create(
            first_name="AdminLead",
            last_name="One",
            company_name="CorpAdmin",
            organization=self.org_a,
            owner=self.users['admin'],
            estimated_value=10000.00
        )
        # Lead 2: Assigned to and owned by Member
        self.lead_member = Lead.objects.create(
            first_name="MemberLead",
            last_name="Two",
            company_name="CorpMember",
            organization=self.org_a,
            owner=self.users['member'],
            assigned_to=self.users['member'],
            estimated_value=25000.00
        )
        # Lead 3: Assigned to Sales Rep
        self.lead_rep = Lead.objects.create(
            first_name="RepLead",
            last_name="Three",
            company_name="CorpRep",
            organization=self.org_a,
            owner=self.users['owner'],
            assigned_to=self.users['sales_rep'],
            estimated_value=15000.00
        )
        # Lead in Org B (for cross-tenant checks)
        self.lead_org_b = Lead.objects.create(
            first_name="OrgBLead",
            last_name="Foreign",
            company_name="ForeignCorp",
            organization=self.org_b,
            owner=self.users['admin'],
            estimated_value=50000.00
        )

        from django.utils import timezone

        # Create Contact in Org A
        self.contact = Contact.objects.create(
            first_name="Test",
            last_name="Contact",
            email="contact@rbac.test",
            organization=self.org_a,
            created_by=self.users['admin']
        )

        # Create Opportunity in Org A
        today = timezone.now().date()
        now = timezone.now()
        self.opp_member = Opportunity.objects.create(
            name="Member Opp",
            contact=self.contact,
            organization=self.org_a,
            owner=self.users['member'],
            assigned_to=self.users['member'],
            company_name="MemberCorp",
            amount=20000.00,
            stage='qualification',
            probability=50,
            currency='USD',
            expected_close_date=today + timezone.timedelta(days=30),
            actual_close_date=today + timezone.timedelta(days=30),
            last_activity_date=now,
            description="",
            notes="",
            tags=[],
            custom_fields={}
        )
        self.opp_admin = Opportunity.objects.create(
            name="Admin Opp",
            contact=self.contact,
            organization=self.org_a,
            owner=self.users['admin'],
            assigned_to=self.users['admin'],
            company_name="AdminCorp",
            amount=80000.00,
            stage='negotiation',
            probability=80,
            currency='USD',
            expected_close_date=today + timezone.timedelta(days=30),
            actual_close_date=today + timezone.timedelta(days=30),
            last_activity_date=now,
            description="",
            notes="",
            tags=[],
            custom_fields={}
        )

        # Create Task in Org A
        self.task_member = Task.objects.create(
            title="Member Task",
            description="",
            task_type="call",
            status='pending',
            priority='medium',
            notes="",
            tags=[],
            custom_fields={},
            due_date=now + timezone.timedelta(days=1),
            contact=self.contact,
            lead=self.lead_member,
            opportunity=self.opp_member,
            organization=self.org_a,
            assigned_to=self.users['member'],
            created_by=self.users['member']
        )
        self.task_admin = Task.objects.create(
            title="Admin Task",
            description="",
            task_type="call",
            status='pending',
            priority='medium',
            notes="",
            tags=[],
            custom_fields={},
            due_date=now + timezone.timedelta(days=1),
            contact=self.contact,
            lead=self.lead_admin,
            opportunity=self.opp_admin,
            organization=self.org_a,
            assigned_to=self.users['admin'],
            created_by=self.users['admin']
        )

    def teardown_method(self):
        reset_tenant_context()

    # =========================================================================
    # 1. READ PERMISSIONS MATRIX & ROW-LEVEL ISOLATION UNDER PAGINATION & SEARCH
    # =========================================================================

    def test_list_visibility_by_role(self):
        """
        Owner, Admin, Manager have organization-wide visibility.
        Member and SalesRep only see their own/assigned records.
        Viewer sees all records in read-only mode.
        Guest (inactive) is rejected with 403.
        """
        # Org-wide roles see all 3 Org A leads
        for role in ['owner', 'admin', 'manager', 'viewer']:
            res = self.clients[role].get('/api/v1/leads/')
            assert res.status_code == status.HTTP_200_OK, f"Role {role} failed list"
            data = res.json()
            count = data.get('count', len(data.get('results', [])))
            assert count == 3, f"Role {role} expected 3 leads, got {count}"

        # Member only sees their 1 lead
        res_mem = self.clients['member'].get('/api/v1/leads/')
        assert res_mem.status_code == status.HTTP_200_OK
        results_mem = res_mem.json().get('results', [])
        assert len(results_mem) == 1
        assert results_mem[0]['id'] == self.lead_member.id

        # SalesRep only sees their 1 assigned lead
        res_rep = self.clients['sales_rep'].get('/api/v1/leads/')
        assert res_rep.status_code == status.HTTP_200_OK
        results_rep = res_rep.json().get('results', [])
        assert len(results_rep) == 1
        assert results_rep[0]['id'] == self.lead_rep.id

        # Guest (inactive membership) rejected
        res_guest = self.clients['guest'].get('/api/v1/leads/')
        assert res_guest.status_code == status.HTTP_403_FORBIDDEN

    def test_search_respects_row_level_isolation(self):
        """
        Search queries cannot bypass row-level isolation for member/sales_rep.
        Searching for AdminLead by member must return 0 records.
        """
        res = self.clients['member'].get('/api/v1/leads/?search=AdminLead')
        assert res.status_code == status.HTTP_200_OK
        assert len(res.json().get('results', [])) == 0

        # Searching for own lead works
        res_own = self.clients['member'].get('/api/v1/leads/?search=MemberLead')
        assert res_own.status_code == status.HTTP_200_OK
        assert len(res_own.json().get('results', [])) == 1

        # Manager search finds AdminLead
        res_mgr = self.clients['manager'].get('/api/v1/leads/?search=AdminLead')
        assert res_mgr.status_code == status.HTTP_200_OK
        assert len(res_mgr.json().get('results', [])) == 1

    # =========================================================================
    # 2. AGGREGATION ENDPOINTS ROW-LEVEL ISOLATION
    # =========================================================================

    def test_statistics_aggregation_row_level_isolation(self):
        """
        Statistics endpoint enforces row-level isolation:
        Member receives total=1, Admin/Manager receives total=3.
        """
        # Member statistics
        res_mem = self.clients['member'].get('/api/v1/leads/statistics/')
        assert res_mem.status_code == status.HTTP_200_OK
        stats_mem = res_mem.json()
        assert stats_mem['total'] == 1
        assert stats_mem['assigned_to_me'] == 1

        # Admin statistics
        res_adm = self.clients['admin'].get('/api/v1/leads/statistics/')
        assert res_adm.status_code == status.HTTP_200_OK
        stats_adm = res_adm.json()
        assert stats_adm['total'] == 3

    def test_pipeline_aggregation_row_level_isolation(self):
        """
        Pipeline aggregation endpoint scopes sums to member's records:
        Member pipeline sums only 20000.0, Admin pipeline sums 100000.0.
        """
        # Member pipeline
        res_mem = self.clients['member'].get('/api/v1/opportunities/pipeline/')
        assert res_mem.status_code == status.HTTP_200_OK
        pipe_mem = res_mem.json()
        assert pipe_mem['total_value'] == 20000.0

        # Manager pipeline
        res_mgr = self.clients['manager'].get('/api/v1/opportunities/pipeline/')
        assert res_mgr.status_code == status.HTTP_200_OK
        pipe_mgr = res_mgr.json()
        assert pipe_mgr['total_value'] == 100000.0

    # =========================================================================
    # 3. MUTATION (CREATE, UPDATE, DELETE) MATRIX & MISSING PERMISSION EXPLANATION
    # =========================================================================

    def test_viewer_mutation_rejected_with_explanation(self):
        """Viewer cannot create, update, or delete; receives 403 explaining missing permission"""
        # Create rejected
        res_create = self.clients['viewer'].post('/api/v1/leads/', {
            'first_name': 'ViewerLead',
            'last_name': 'Bad',
            'company_name': 'BadCorp',
            'email': 'viewer_bad@test.local'
        }, format='json')
        assert res_create.status_code == status.HTTP_403_FORBIDDEN
        detail = res_create.json().get('detail', '')
        assert "Role 'viewer' cannot perform action 'create'" in detail
        assert "Required roles:" in detail

        # Update rejected
        res_update = self.clients['viewer'].patch(f'/api/v1/leads/{self.lead_admin.id}/', {
            'company_name': 'ViewerTampered'
        }, format='json')
        assert res_update.status_code == status.HTTP_403_FORBIDDEN
        assert "cannot perform action 'partial_update'" in res_update.json().get('detail', '')

        # Destroy rejected
        res_del = self.clients['viewer'].delete(f'/api/v1/leads/{self.lead_admin.id}/')
        assert res_del.status_code == status.HTTP_403_FORBIDDEN
        assert "Role 'viewer' cannot perform action 'destroy'" in res_del.json().get('detail', '')

    def test_member_destroy_rejected_with_explanation(self):
        """Member cannot delete records; receives 403 explaining required roles"""
        res_del = self.clients['member'].delete(f'/api/v1/leads/{self.lead_member.id}/')
        assert res_del.status_code == status.HTTP_403_FORBIDDEN
        detail = res_del.json().get('detail', '')
        assert "Role 'member' cannot perform action 'destroy'" in detail
        assert "Required roles: owner, admin, manager" in detail

    def test_manager_destroy_allowed(self):
        """Manager can delete records within the organization"""
        res_del = self.clients['manager'].delete(f'/api/v1/leads/{self.lead_rep.id}/')
        assert res_del.status_code == status.HTTP_204_NO_CONTENT
        assert not Lead.objects.filter(id=self.lead_rep.id).exists()

    def test_member_update_own_allowed_other_rejected(self):
        """Member can update their own lead, but updating admin lead returns 403/404 with detail"""
        # Own lead
        res_own = self.clients['member'].patch(f'/api/v1/leads/{self.lead_member.id}/', {
            'company_name': 'UpdatedOwnCorp'
        }, format='json')
        assert res_own.status_code == status.HTTP_200_OK

        # Admin lead: DRF get_queryset filters it out (404), or object permission rejects (403)
        res_other = self.clients['member'].patch(f'/api/v1/leads/{self.lead_admin.id}/', {
            'company_name': 'HijackedCorp'
        }, format='json')
        assert res_other.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    # =========================================================================
    # 4. CUSTOM ACTIONS: CONVERT, COMPLETE, BULK_UPDATE, BULK_DELETE, EXPORT
    # =========================================================================

    def test_convert_role_and_ownership_constraints(self):
        """
        Lead convert action:
        - Viewer: rejected (403)
        - Member on own lead: allowed (200)
        """
        # Viewer rejected
        res_view = self.clients['viewer'].post(f'/api/v1/leads/{self.lead_member.id}/convert/')
        assert res_view.status_code == status.HTTP_403_FORBIDDEN

        # Member converts own lead
        res_conv = self.clients['member'].post(f'/api/v1/leads/{self.lead_member.id}/convert/')
        assert res_conv.status_code == status.HTTP_200_OK
        data = res_conv.json()
        assert data['success'] is True
        assert data['contact_id'] is not None

        # Verify converted contact has tenant set
        contact = Contact.objects.get(id=data['contact_id'])
        assert contact.organization == self.org_a

    def test_task_complete_role_constraints(self):
        """
        Task complete action:
        - Viewer: rejected (403)
        - Member on own task: allowed (200)
        """
        res_view = self.clients['viewer'].post(f'/api/v1/tasks/{self.task_member.id}/complete/')
        assert res_view.status_code == status.HTTP_403_FORBIDDEN

        res_mem = self.clients['member'].post(f'/api/v1/tasks/{self.task_member.id}/complete/')
        assert res_mem.status_code == status.HTTP_200_OK
        assert res_mem.json()['status'] == 'completed'

    def test_bulk_update_and_bulk_delete_matrix(self):
        """
        bulk_update action='update':
          - member / viewer: rejected (403)
          - manager: allowed (200)
        bulk_update action='delete':
          - manager: rejected (403) explaining bulk delete requires owner/admin
          - admin: allowed (200)
        """
        # Member bulk update rejected
        res_mem = self.clients['member'].post('/api/v1/leads/bulk_update/', {
            'ids': [self.lead_member.id],
            'action': 'update',
            'data': {'company_name': 'BulkAttempt'}
        }, format='json')
        assert res_mem.status_code == status.HTTP_403_FORBIDDEN
        assert "cannot perform action 'bulk_update'" in res_mem.json().get('detail', '')

        # Manager bulk update allowed
        res_mgr = self.clients['manager'].post('/api/v1/leads/bulk_update/', {
            'ids': [self.lead_member.id],
            'action': 'update',
            'data': {'company_name': 'ManagerBulkUpdated'}
        }, format='json')
        assert res_mgr.status_code == status.HTTP_200_OK
        self.lead_member.refresh_from_db()
        assert self.lead_member.company_name == 'ManagerBulkUpdated'

        # Manager bulk delete rejected with explanation
        res_mgr_del = self.clients['manager'].post('/api/v1/leads/bulk_update/', {
            'ids': [self.lead_member.id],
            'action': 'delete'
        }, format='json')
        assert res_mgr_del.status_code == status.HTTP_403_FORBIDDEN
        detail = res_mgr_del.json().get('detail', '')
        assert "Role 'manager' cannot perform bulk delete" in detail
        assert "Required roles: owner, admin" in detail

        # Admin bulk delete allowed
        res_adm_del = self.clients['admin'].post('/api/v1/leads/bulk_update/', {
            'ids': [self.lead_member.id],
            'action': 'delete'
        }, format='json')
        assert res_adm_del.status_code == status.HTTP_200_OK
        assert not Lead.objects.filter(id=self.lead_member.id).exists()

    def test_export_role_scoping(self):
        """Export endpoints are restricted to manager, admin, owner"""
        assert self.clients['viewer'].get('/api/v1/export/leads/').status_code == status.HTTP_403_FORBIDDEN
        assert self.clients['member'].get('/api/v1/export/leads/').status_code == status.HTTP_403_FORBIDDEN
        assert self.clients['manager'].get('/api/v1/export/leads/').status_code == status.HTTP_200_OK
        assert self.clients['admin'].get('/api/v1/export/leads/').status_code == status.HTTP_200_OK

    # =========================================================================
    # 5. FORBIDDEN FIELDS REJECTION
    # =========================================================================

    def test_forbidden_fields_rejected_for_member(self):
        """
        When member attempts to modify forbidden system/tenant fields:
        (organization, role, created_by, is_superuser), request is rejected
        with HTTP 403 Forbidden explaining the violation.
        """
        # Attempt to inject organization on create
        res_org = self.clients['member'].post('/api/v1/leads/', {
            'first_name': 'Tampered',
            'last_name': 'Lead',
            'company_name': 'TamperCo',
            'email': 'tamper@test.local',
            'organization': self.org_b.id
        }, format='json')
        assert res_org.status_code == status.HTTP_403_FORBIDDEN
        detail = res_org.json().get('detail', '')
        assert "Forbidden field(s) rejected for role 'member': organization" in detail

        # Attempt to inject is_superuser on patch
        res_super = self.clients['member'].patch(f'/api/v1/leads/{self.lead_member.id}/', {
            'company_name': 'ValidCompany',
            'is_superuser': True
        }, format='json')
        assert res_super.status_code == status.HTTP_403_FORBIDDEN
        assert "Forbidden field(s) rejected for role 'member': is_superuser" in res_super.json().get('detail', '')

        # Attempt to inject role on patch
        res_role = self.clients['member'].patch(f'/api/v1/leads/{self.lead_member.id}/', {
            'role': 'owner'
        }, format='json')
        assert res_role.status_code == status.HTTP_403_FORBIDDEN
        assert "Forbidden field(s) rejected for role 'member': role" in res_role.json().get('detail', '')

    def test_forbidden_fields_rejected_for_manager(self):
        """Manager cannot modify organization or is_superuser"""
        res = self.clients['manager'].patch(f'/api/v1/leads/{self.lead_admin.id}/', {
            'organization': self.org_b.id
        }, format='json')
        assert res.status_code == status.HTTP_403_FORBIDDEN
        assert "Forbidden field(s) rejected for role 'manager': organization" in res.json().get('detail', '')

    # =========================================================================
    # 6. ADVERSARIAL VALIDATION & OPERATIONAL CONTROLS
    # =========================================================================

    def test_cross_tenant_isolation(self):
        """Attempting to access resource in Org B using Org A credentials yields 404/403"""
        res = self.clients['admin'].get(f'/api/v1/leads/{self.lead_org_b.id}/')
        assert res.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]

    def test_anonymous_access_rejected(self):
        """Unauthenticated request yields 401 Unauthorized"""
        anon_client = APIClient()
        res = anon_client.get('/api/v1/leads/')
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_malformed_bulk_update_payload_rejected(self):
        """Malformed payload yields 400 Bad Request"""
        res = self.clients['admin'].post('/api/v1/leads/bulk_update/', {
            'ids': 'not-a-list',
            'action': 'invalid_action'
        }, format='json')
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_operational_strict_rbac_kill_switch(self):
        """
        When FEATURE_STRICT_RBAC is set to False (emergency rollback):
        Role-based check is bypassed (e.g. viewer can perform write).
        """
        with override_settings(FEATURE_STRICT_RBAC=False):
            res = self.clients['viewer'].post('/api/v1/leads/', {
                'first_name': 'Emergency',
                'last_name': 'Lead',
                'company_name': 'BypassedCorp',
                'email': 'bypassed@test.local'
            }, format='json')
            assert res.status_code == status.HTTP_201_CREATED

    def test_operational_forbidden_fields_kill_switch(self):
        """
        When FEATURE_FORBIDDEN_FIELDS_ENFORCEMENT is set to False:
        Payload with extra fields is not blocked by RBAC permission.
        """
        with override_settings(FEATURE_FORBIDDEN_FIELDS_ENFORCEMENT=False):
            # Member sends extra field that is ignored by serializer rather than 403-rejected by RBAC
            res = self.clients['member'].patch(f'/api/v1/leads/{self.lead_member.id}/', {
                'company_name': 'BypassFieldCheck',
                'is_superuser': True
            }, format='json')
            assert res.status_code == status.HTTP_200_OK
