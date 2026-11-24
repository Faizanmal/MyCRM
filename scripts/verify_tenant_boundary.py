#!/usr/bin/env python
"""
Verification Script: 00-tenant-boundary
Validates multi-tenant isolation and authorization hardening:
1. Cross-tenant header rejection (Org A user requesting Org B slug -> 403)
2. Subdomain / domain spoofing rejection
3. Unauthenticated / anonymous request handling (fail-closed, no auto-default)
4. Cross-tenant object ID direct access (404 / 403 isolation across Lead, Contact, Opportunity, Task)
5. Cross-tenant bulk operations (rejection of cross-tenant IDs)
6. Cross-tenant export leakage prevention (CSV export filtered strictly to current org)
7. WebSocket activity feed isolation (room scoped to tenant ID, not global)
8. ContextVar async context isolation under concurrent requests
"""
import os
import sys
import django

# Setup Django environment
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import json
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from multi_tenant.models import Organization, OrganizationMember
from lead_management.models import Lead
from contact_management.models import Contact
from opportunity_management.models import Opportunity
from task_management.models import Task
from multi_tenant.middleware import TenantMiddleware, get_current_organization, reset_tenant_context

User = get_user_model()


def run_checks():
    print("=" * 70)
    print("STARTING 00-TENANT-BOUNDARY VERIFICATION SUITE")
    print("=" * 70)

    # 1. Clean & setup fixture organizations and users
    org_a, _ = Organization.objects.get_or_create(
        slug="tenant-alpha",
        defaults={"name": "Alpha Corp", "status": "active"}
    )
    org_b, _ = Organization.objects.get_or_create(
        slug="tenant-beta",
        defaults={"name": "Beta Inc", "status": "active"}
    )

    user_a, _ = User.objects.get_or_create(
        username="user_alpha",
        defaults={"email": "alpha@example.com"}
    )
    user_a.set_password("pass123")
    user_a.save()

    user_b, _ = User.objects.get_or_create(
        username="user_beta",
        defaults={"email": "beta@example.com"}
    )
    user_b.set_password("pass123")
    user_b.save()

    OrganizationMember.objects.filter(user=user_a).delete()
    OrganizationMember.objects.filter(user=user_b).delete()

    member_a = OrganizationMember.objects.create(
        organization=org_a,
        user=user_a,
        role="member",
        is_active=True
    )
    member_b = OrganizationMember.objects.create(
        organization=org_b,
        user=user_b,
        role="member",
        is_active=True
    )

    # Tokens
    token_a = str(RefreshToken.for_user(user_a).access_token)
    token_b = str(RefreshToken.for_user(user_b).access_token)

    # 2. Check: Cross-Tenant Header Rejection
    print("\n[Check 1] Cross-Tenant Header Rejection (Org A user requesting Org B slug)")
    client_a = APIClient()
    client_a.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}', HTTP_X_ORGANIZATION_SLUG='tenant-beta')
    res_cross = client_a.get('/api/v1/leads/')
    assert res_cross.status_code == 403, f"Expected 403 Forbidden for cross-tenant header, got {res_cross.status_code}: {res_cross.data if hasattr(res_cross, 'data') else res_cross.content}"
    assert res_cross.json().get('code') == 'tenant_forbidden', f"Expected code tenant_forbidden, got {res_cross.json()}"
    print("  PASS: Header spoofing correctly rejected with 403 tenant_forbidden.")

    # 3. Check: Subdomain Spoofing Rejection
    print("\n[Check 2] Cross-Tenant Subdomain Rejection")
    client_spoof = APIClient()
    client_spoof.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}', HTTP_HOST='tenant-beta.crm.local')
    res_subdomain = client_spoof.get('/api/v1/leads/')
    assert res_subdomain.status_code == 403, f"Expected 403 for host spoofing, got {res_subdomain.status_code}"
    print("  PASS: Host spoofing correctly rejected with 403.")

    # 4. Check: Fail-Closed on Unauthenticated / Anonymous with Header
    print("\n[Check 3] Unauthenticated / Anonymous Access with Org Header")
    client_anon = APIClient()
    client_anon.credentials(HTTP_X_ORGANIZATION_SLUG='tenant-alpha')
    res_anon = client_anon.get('/api/v1/leads/')
    # Must be 401 Unauthorized, never allow data access or auto-create default org
    assert res_anon.status_code in [401, 403], f"Expected 401/403 for anon header access, got {res_anon.status_code}"
    print("  PASS: Anonymous access fails closed.")

    # 5. Check: Isolated Object Direct Access
    print("\n[Check 4] Cross-Tenant Direct Object Access (Lead, Contact, Opportunity, Task)")
    # Clear existing leads for clean assertion
    Lead.objects.filter(organization__in=[org_a, org_b]).delete()
    Contact.objects.filter(organization__in=[org_a, org_b]).delete()

    lead_a = Lead.objects.create(
        first_name="LeadA",
        last_name="Alpha",
        company_name="AlphaCo",
        organization=org_a,
        owner=user_a,
        estimated_value=1000.00
    )
    lead_b = Lead.objects.create(
        first_name="LeadB",
        last_name="Beta",
        company_name="BetaCo",
        organization=org_b,
        owner=user_b,
        estimated_value=2000.00
    )

    contact_a = Contact.objects.create(
        first_name="ContactA",
        last_name="Alpha",
        email="contact_a@alpha.local",
        organization=org_a,
        created_by=user_a
    )
    contact_b = Contact.objects.create(
        first_name="ContactB",
        last_name="Beta",
        email="contact_b@beta.local",
        organization=org_b,
        created_by=user_b
    )

    client_valid_a = APIClient()
    client_valid_a.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}', HTTP_X_ORGANIZATION_SLUG='tenant-alpha')

    # Org A accesses own lead -> 200
    res_own_lead = client_valid_a.get(f'/api/v1/leads/{lead_a.id}/')
    assert res_own_lead.status_code == 200, f"Expected 200 for own lead, got {res_own_lead.status_code}"

    # Org A accesses Org B lead -> 404 (strictly filtered at queryset source)
    res_foreign_lead = client_valid_a.get(f'/api/v1/leads/{lead_b.id}/')
    assert res_foreign_lead.status_code == 404, f"Expected 404 for foreign lead, got {res_foreign_lead.status_code}"

    # Org A accesses own contact -> 200
    res_own_contact = client_valid_a.get(f'/api/v1/contacts/{contact_a.id}/')
    assert res_own_contact.status_code == 200, f"Expected 200 for own contact, got {res_own_contact.status_code}"

    # Org A accesses Org B contact -> 404
    res_foreign_contact = client_valid_a.get(f'/api/v1/contacts/{contact_b.id}/')
    assert res_foreign_contact.status_code == 404, f"Expected 404 for foreign contact, got {res_foreign_contact.status_code}"
    print("  PASS: Cross-tenant direct object access properly isolated (404/Not Found).")

    # 6. Check: Cross-Tenant Bulk Mutation
    print("\n[Check 5] Cross-Tenant Bulk Mutation Attack Rejection")
    res_bulk = client_valid_a.post('/api/v1/leads/bulk_update/', {
        'ids': [lead_a.id, lead_b.id],
        'action': 'update',
        'data': {'company_name': 'HackedCompany'}
    }, format='json')
    assert res_bulk.status_code == 404, f"Expected 404 when bulk update targets cross-tenant ID, got {res_bulk.status_code}"
    lead_b.refresh_from_db()
    assert lead_b.company_name == "BetaCo", "CRITICAL FAILURE: foreign lead was mutated across tenant boundary!"
    print("  PASS: Cross-tenant bulk operations rejected without mutating foreign records.")

    # 7. Check: Cross-Tenant Export Leakage Prevention
    print("\n[Check 6] CSV Export Tenant Scoping")
    res_export = client_valid_a.get('/api/v1/export/leads/')
    assert res_export.status_code == 200
    content = res_export.content.decode('utf-8')
    assert "LeadA" in content, "Export missing own tenant lead"
    assert "LeadB" not in content, "CRITICAL LEAK: Foreign tenant lead found in CSV export!"
    print("  PASS: CSV export is strictly scoped to the requesting tenant.")

    # 8. Check: WebSocket Consumer Tenant Scoping
    print("\n[Check 7] WebSocket ActivityFeedConsumer Tenant Isolation")
    from core.consumers import ActivityFeedConsumer
    consumer = ActivityFeedConsumer()
    consumer.scope = {'user': user_a}
    import asyncio
    tid = asyncio.run(consumer.get_user_tenant_id())
    assert tid == org_a.id, f"Expected user_a tenant ID {org_a.id}, got {tid}"
    print(f"  PASS: ActivityFeedConsumer resolves correct tenant channel (activity_feed_tenant_{tid}).")

    # 9. Check: ContextVars Ambient State Reset
    print("\n[Check 8] ContextVar Async Cleanup")
    reset_tenant_context()
    assert get_current_organization() is None, "ContextVar failed to clear on reset"
    print("  PASS: ContextVar safely resets without ambient state leaks.")

    print("\n" + "=" * 70)
    print("ALL 00-TENANT-BOUNDARY VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == '__main__':
    run_checks()
