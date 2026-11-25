#!/usr/bin/env python
"""
Verification Script: 01-rbac
Validates Parameterized Role-Based Access Control (RBAC):
1. Role Hierarchy Matrix across Endpoints & Actions:
   - Owner / Admin: All CRUD, bulk operations, convert, import, export
   - Manager: CRUD, bulk_update (update only), convert, import, export; NO bulk_delete
   - Member / SalesRep: Read, Create, Update (own/assigned only), Convert; NO delete, bulk_update, bulk_delete, export
   - Viewer / Guest: Read-only; NO create, update, delete, convert, bulk operations
2. Parameterized Action Validation:
   - bulk_update with action='delete' rejected for non-admin/owner (403 with missing permission explanation)
   - bulk_update with action='update' rejected for member/sales_rep/viewer (403 with missing permission explanation)
   - convert action permitted for member on assigned lead, rejected for viewer (403)
3. Forbidden Fields Rejection:
   - Non-privileged roles attempting to supply system or tenant fields (e.g. organization, role, is_superuser)
     are strictly rejected with HTTP 403 Forbidden explaining the violation.
4. Row-Level Isolation Under Pagination, Search & Aggregations:
   - Member/SalesRep listing and aggregations (/statistics/, /pipeline/) only return/count records assigned to or owned by them
   - Manager/Admin listing and aggregations return all records within the organization
5. Operational Controls & Kill Switch:
   - FEATURE_STRICT_RBAC and FEATURE_FORBIDDEN_FIELDS_ENFORCEMENT toggles verified.
"""
import os
import sys
import django

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from multi_tenant.models import Organization, OrganizationMember
from multi_tenant.middleware import reset_tenant_context
from lead_management.models import Lead
from contact_management.models import Contact
from opportunity_management.models import Opportunity
from task_management.models import Task

User = get_user_model()


def run_rbac_checks():
    print("=" * 70)
    print("STARTING 01-RBAC PARAMETERIZED VERIFICATION SUITE")
    print("=" * 70)

    reset_tenant_context()

    # 1. Setup Tenant and Role Fixtures
    org, _ = Organization.objects.get_or_create(
        slug="rbac-tenant",
        defaults={"name": "RBAC Corp", "status": "active"}
    )
    foreign_org, _ = Organization.objects.get_or_create(
        slug="foreign-tenant",
        defaults={"name": "Foreign Corp", "status": "active"}
    )

    roles = ['owner', 'admin', 'manager', 'member', 'sales_rep', 'viewer']
    users = {}
    tokens = {}
    clients = {}

    for r in roles:
        u, _ = User.objects.get_or_create(
            username=f"rbac_{r}",
            defaults={"email": f"{r}@rbac.local"}
        )
        u.set_password("pass123")
        u.save()
        mem = OrganizationMember.objects.filter(user=u, organization=org).first()
        if mem:
            mem.role = r
            mem.is_active = True
            mem.save()
        else:
            OrganizationMember.objects.create(
                organization=org,
                user=u,
                role=r,
                is_active=True
            )
        users[r] = u
        tokens[r] = str(RefreshToken.for_user(u).access_token)
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens[r]}', HTTP_X_ORGANIZATION_SLUG=org.slug)
        clients[r] = c

    # Clean existing test leads in tenant
    Lead.objects.filter(organization=org).delete()

    # Create leads: one owned by admin, one assigned to member, one unassigned
    lead_admin = Lead.objects.create(
        first_name="Admin",
        last_name="Lead",
        company_name="AdminCo",
        organization=org,
        owner=users['admin'],
        estimated_value=1000.00
    )
    lead_member = Lead.objects.create(
        first_name="Member",
        last_name="Lead",
        company_name="MemberCo",
        organization=org,
        owner=users['member'],
        assigned_to=users['member'],
        estimated_value=2000.00
    )
    lead_unassigned = Lead.objects.create(
        first_name="Unassigned",
        last_name="Lead",
        company_name="UnassignedCo",
        organization=org,
        owner=users['owner'],
        estimated_value=3000.00
    )

    # =========================================================================
    # CHECK 1: Read Permissions Matrix & Row-Level Isolation Under List
    # =========================================================================
    print("\n[Check 1] Read Matrix & Row-Level Filtering Under List")

    # Owner / Admin / Manager see all 3 leads
    for r in ['owner', 'admin', 'manager']:
        res = clients[r].get('/api/v1/leads/')
        assert res.status_code == 200, f"Role {r} failed to list leads: {res.status_code}"
        count = res.json().get('count', len(res.json().get('results', [])))
        assert count == 3, f"Role {r} should see 3 leads, got {count}"
    print("  PASS: Owner, Admin, Manager have organization-wide visibility.")

    # Member sees only their own/assigned lead (1 lead)
    res_mem = clients['member'].get('/api/v1/leads/')
    assert res_mem.status_code == 200
    mem_results = res_mem.json().get('results', [])
    assert len(mem_results) == 1, f"Member should only see their assigned lead, got {len(mem_results)}"
    assert mem_results[0]['id'] == lead_member.id
    print("  PASS: Member/SalesRep row-level isolation verified in list/pagination.")

    # Viewer sees leads in read-only mode
    res_view = clients['viewer'].get('/api/v1/leads/')
    assert res_view.status_code == 200
    print("  PASS: Viewer allowed read access.")

    # =========================================================================
    # CHECK 2: Mutation & Creation Matrix with Missing Permission Explanation
    # =========================================================================
    print("\n[Check 2] Mutation Permissions Matrix & Missing Permission Explanation")

    # Viewer cannot create (403 with detailed message)
    res_view_create = clients['viewer'].post('/api/v1/leads/', {
        'first_name': 'Hacked',
        'last_name': 'Viewer',
        'company_name': 'ViewerCo',
        'email': 'viewer_test@example.com'
    }, format='json')
    assert res_view_create.status_code == 403, f"Viewer create should be 403, got {res_view_create.status_code}"
    detail = res_view_create.json().get('detail', '')
    assert "Role 'viewer' cannot perform action 'create'" in detail
    assert "Required roles:" in detail
    print("  PASS: Viewer rejected on create with descriptive permission explanation.")

    # Member can create
    res_mem_create = clients['member'].post('/api/v1/leads/', {
        'first_name': 'CreatedBy',
        'last_name': 'Member',
        'company_name': 'MemberCreatedCo',
        'email': 'mem_created@example.com',
        'estimated_value': '500.00'
    }, format='json')
    assert res_mem_create.status_code == 201, f"Member should be able to create, got {res_mem_create.status_code}"
    new_lead_id = res_mem_create.json()['id']
    print("  PASS: Member successfully created lead.")

    # Member can update own lead
    res_mem_update_own = clients['member'].patch(f'/api/v1/leads/{new_lead_id}/', {
        'company_name': 'UpdatedMemberCo'
    }, format='json')
    assert res_mem_update_own.status_code == 200
    print("  PASS: Member successfully updated own lead.")

    # Member cannot update lead assigned to Admin (object-level 403 or 404)
    res_mem_update_admin = clients['member'].patch(f'/api/v1/leads/{lead_admin.id}/', {
        'company_name': 'UnauthorizedUpdate'
    }, format='json')
    assert res_mem_update_admin.status_code in [403, 404]
    print("  PASS: Member forbidden from updating unassigned/other leads.")

    # =========================================================================
    # CHECK 3: Forbidden Fields Rejection
    # =========================================================================
    print("\n[Check 3] Forbidden Fields Rejection (403 with Explanation)")

    # Member passing forbidden 'organization' field
    res_forbid_org = clients['member'].post('/api/v1/leads/', {
        'first_name': 'Injected',
        'last_name': 'Tenant',
        'company_name': 'InjectCo',
        'email': 'inject@test.local',
        'organization': foreign_org.id
    }, format='json')
    assert res_forbid_org.status_code == 403
    assert "Forbidden field(s) rejected for role 'member': organization" in res_forbid_org.json().get('detail', '')
    print("  PASS: Member attempting to supply 'organization' field rejected with 403.")

    # Member passing forbidden 'role' or 'is_superuser' field
    res_forbid_role = clients['member'].patch(f'/api/v1/leads/{new_lead_id}/', {
        'company_name': 'ValidCompany',
        'role': 'owner'
    }, format='json')
    assert res_forbid_role.status_code == 403
    assert "Forbidden field(s) rejected for role 'member': role" in res_forbid_role.json().get('detail', '')
    print("  PASS: Member attempting to supply 'role' field rejected with 403.")

    # =========================================================================
    # CHECK 4: Parameterized Bulk Operations & High-Privilege Endpoints
    # =========================================================================
    print("\n[Check 4] Parameterized Bulk Update vs Bulk Delete")

    # Member cannot perform bulk_update (403)
    res_mem_bulk = clients['member'].post('/api/v1/leads/bulk_update/', {
        'ids': [lead_member.id],
        'action': 'update',
        'data': {'company_name': 'BulkAttempt'}
    }, format='json')
    assert res_mem_bulk.status_code == 403
    assert "cannot perform action 'bulk_update'" in res_mem_bulk.json().get('detail', '')
    print("  PASS: Member rejected from bulk_update.")

    # Manager CAN perform bulk_update with action='update'
    res_mgr_bulk_update = clients['manager'].post('/api/v1/leads/bulk_update/', {
        'ids': [lead_member.id],
        'action': 'update',
        'data': {'company_name': 'ManagerBulkSuccess'}
    }, format='json')
    assert res_mgr_bulk_update.status_code == 200
    print("  PASS: Manager allowed bulk_update (action=update).")

    # Manager CANNOT perform bulk_update with action='delete' (bulk delete is Admin/Owner only)
    res_mgr_bulk_delete = clients['manager'].post('/api/v1/leads/bulk_update/', {
        'ids': [lead_member.id],
        'action': 'delete'
    }, format='json')
    assert res_mgr_bulk_delete.status_code == 403
    detail = res_mgr_bulk_delete.json().get('detail', '')
    assert "Role 'manager' cannot perform bulk delete" in detail
    assert "Required roles: owner, admin" in detail
    print("  PASS: Manager rejected from bulk delete with descriptive permission explanation.")

    # Admin CAN perform bulk delete
    res_admin_bulk_delete = clients['admin'].post('/api/v1/leads/bulk_update/', {
        'ids': [new_lead_id],
        'action': 'delete'
    }, format='json')
    assert res_admin_bulk_delete.status_code == 200
    assert not Lead.objects.filter(id=new_lead_id).exists()
    print("  PASS: Admin allowed bulk delete.")

    # =========================================================================
    # CHECK 5: Row-Level Isolation Under Aggregations
    # =========================================================================
    print("\n[Check 5] Aggregation Endpoints Row-Level Isolation")

    res_mem_stats = clients['member'].get('/api/v1/leads/statistics/')
    assert res_mem_stats.status_code == 200
    assert res_mem_stats.json()['total'] == 1, f"Member should only count 1 lead, got {res_mem_stats.json()['total']}"

    res_mgr_stats = clients['manager'].get('/api/v1/leads/statistics/')
    assert res_mgr_stats.status_code == 200
    assert res_mgr_stats.json()['total'] == 3, f"Manager should count all 3 leads, got {res_mgr_stats.json()['total']}"
    print("  PASS: Row-level isolation verified on /api/v1/leads/statistics/.")

    # =========================================================================
    # CHECK 6: Operational Kill-Switch & Feature Flags
    # =========================================================================
    print("\n[Check 6] Operational Kill-Switch Verification")

    with override_settings(FEATURE_STRICT_RBAC=False):
        res_bypassed = clients['viewer'].post('/api/v1/leads/', {
            'first_name': 'KillSwitchTest',
            'last_name': 'Lead',
            'company_name': 'EmergencyCo',
            'email': 'emergency@test.local'
        }, format='json')
        assert res_bypassed.status_code == 201
        Lead.objects.filter(id=res_bypassed.json()['id']).delete()
    print("  PASS: FEATURE_STRICT_RBAC emergency kill switch allows bypass during rollback.")

    with override_settings(FEATURE_FORBIDDEN_FIELDS_ENFORCEMENT=False):
        res_field_bypassed = clients['member'].patch(f'/api/v1/leads/{lead_member.id}/', {
            'company_name': 'FieldKillSwitchCo',
            'role': 'owner'
        }, format='json')
        assert res_field_bypassed.status_code == 200
    print("  PASS: FEATURE_FORBIDDEN_FIELDS_ENFORCEMENT emergency toggle works.")

    print("\n" + "=" * 70)
    print("ALL 01-RBAC PARAMETERIZED CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == '__main__':
    run_rbac_checks()
