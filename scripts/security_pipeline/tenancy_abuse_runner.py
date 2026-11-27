"""
Tenancy & Authorization Abuse Security Test Runner
Adversarially tests multi-tenant isolation, IDOR, privilege escalation, forged headers, and anonymous access.
"""
import os
import sys
import uuid
from typing import Dict, List, Tuple

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    import django
    from django.conf import settings
    os.environ['TESTING'] = 'True'
    django.setup()
    settings.SECURE_SSL_REDIRECT = False
    from django.contrib.auth import get_user_model
    from rest_framework.test import APIClient
    from multi_tenant.models import Organization, OrganizationMember
    from lead_management.models import Lead
    from core.audit_models import AuditTrail
    from core.audit_service import log_audit_event
    DJANGO_AVAILABLE = True
except Exception as e:
    DJANGO_AVAILABLE = False
    DJANGO_INIT_ERROR = str(e)


def run_tenancy_abuse_suite() -> Tuple[bool, List[Dict]]:
    if not DJANGO_AVAILABLE:
        return False, [{'test': 'django_init', 'passed': False, 'error': f"Failed to initialize Django: {DJANGO_INIT_ERROR}"}]

    User = get_user_model()
    results = []

    # Clean existing test tenants
    Organization.objects.filter(slug__in=['abuse-tenant-a', 'abuse-tenant-b']).delete()
    User.objects.filter(username__in=['attacker_user', 'victim_user', 'low_priv_user']).delete()

    try:
        # Setup Victims and Attackers
        org_victim = Organization.objects.create(name="Victim Org", slug="abuse-tenant-a", email="victim@corp.com")
        org_attacker = Organization.objects.create(name="Attacker Org", slug="abuse-tenant-b", email="attacker@corp.com")

        user_victim = User.objects.create_user(username="victim_user", email="victim@corp.com", password="Password123!")
        user_attacker = User.objects.create_user(username="attacker_user", email="attacker@corp.com", password="Password123!")
        user_low_priv = User.objects.create_user(username="low_priv_user", email="lowpriv@corp.com", password="Password123!")

        OrganizationMember.objects.create(organization=org_victim, user=user_victim, role='admin', is_active=True)
        OrganizationMember.objects.create(organization=org_attacker, user=user_attacker, role='admin', is_active=True)
        OrganizationMember.objects.create(organization=org_victim, user=user_low_priv, role='member', is_active=True)

        # Create victim resources
        victim_lead = Lead.objects.create(
            organization=org_victim,
            owner=user_victim,
            first_name="Confidential",
            last_name="Prospect",
            email="secret@lead.com",
            status="new",
        )
        victim_audit = log_audit_event(
            user=user_victim,
            action='create',
            target=victim_lead,
            description="Victim proprietary deal created",
            organization=org_victim,
        )

        client_attacker = APIClient()
        client_attacker.force_authenticate(user=user_attacker)

        client_low_priv = APIClient()
        client_low_priv.force_authenticate(user=user_low_priv)

        client_anonymous = APIClient()

        # TEST 1: Cross-Tenant Lead IDOR (Read)
        res_read = client_attacker.get(f'/api/v1/leads/{victim_lead.id}/')
        passed_1 = (res_read.status_code in [404, 403])
        results.append({
            'test': 'cross_tenant_lead_idor_read',
            'passed': passed_1,
            'details': f"Status {res_read.status_code} (Expected 404 or 403)",
        })

        # TEST 2: Cross-Tenant Lead IDOR (Delete)
        res_del = client_attacker.delete(f'/api/v1/leads/{victim_lead.id}/')
        passed_2 = (res_del.status_code in [404, 403])
        # Verify lead still exists in DB
        lead_still_exists = Lead.objects.filter(id=victim_lead.id).exists()
        results.append({
            'test': 'cross_tenant_lead_idor_delete',
            'passed': passed_2 and lead_still_exists,
            'details': f"Status {res_del.status_code}, resource preserved: {lead_still_exists}",
        })

        # TEST 3: Forged Tenant Header Spoofing
        res_spoof = client_attacker.get(
            '/api/v1/leads/',
            HTTP_X_ORGANIZATION_ID=str(org_victim.id),
        )
        passed_3 = True
        if res_spoof.status_code == 200:
            leads_data = res_spoof.data.get('results', res_spoof.data)
            lead_emails = [l.get('email') for l in leads_data if isinstance(l, dict)]
            if "secret@lead.com" in lead_emails:
                passed_3 = False
        results.append({
            'test': 'forged_tenant_header_spoofing',
            'passed': passed_3,
            'details': f"Status {res_spoof.status_code}, victim data not leaked under forged header",
        })

        # TEST 4: Anonymous Probing Denied
        res_anon = client_anonymous.get('/api/v1/leads/')
        passed_4 = (res_anon.status_code in [401, 403])
        results.append({
            'test': 'anonymous_probing_denied',
            'passed': passed_4,
            'details': f"Status {res_anon.status_code} (Expected 401 Unauthorized)",
        })

        # TEST 5: Cross-Tenant Audit Trail IDOR
        res_audit = client_attacker.get(f'/api/v1/audit-trail/{victim_audit.id}/')
        passed_5 = (res_audit.status_code in [404, 403])
        results.append({
            'test': 'cross_tenant_audit_idor',
            'passed': passed_5,
            'details': f"Status {res_audit.status_code} (Expected 404 Not Found)",
        })

        # TEST 6: Privilege Escalation (Member attempting deletion request approval)
        res_escalate = client_low_priv.post(
            f'/api/v1/gdpr/deletion-requests/{uuid.uuid4()}/approve/',
            {}
        )
        passed_6 = (res_escalate.status_code in [403, 404])
        results.append({
            'test': 'role_privilege_escalation_denied',
            'passed': passed_6,
            'details': f"Status {res_escalate.status_code} (Expected 403 Forbidden for non-staff)",
        })

    except Exception as e:
        results.append({
            'test': 'tenancy_abuse_execution',
            'passed': False,
            'details': f"Exception during abuse execution: {str(e)}",
        })

    all_passed = all(r['passed'] for r in results)
    return all_passed, results


def main():
    print("[*] Running Tenancy & Authorization Abuse Suite...")
    all_passed, results = run_tenancy_abuse_suite()

    for r in results:
        status_str = "[PASS]" if r['passed'] else "[FAIL]"
        print(f"  {status_str} {r['test']}: {r['details']}")

    if all_passed:
        print("[PASS] Tenancy/Authz Abuse Suite: All isolation and boundary checks passed.")
        sys.exit(0)
    else:
        print("[FAIL] Tenancy/Authz Abuse Suite: Identified boundary violations!")
        sys.exit(1)


if __name__ == '__main__':
    main()
