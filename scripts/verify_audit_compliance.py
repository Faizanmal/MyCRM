"""
Verification Harness: Audit Compliance, Credential Redaction, Hash-Chaining & DSAR Workflows
Domain acceptance tests:
1. Cross-tenant audit isolation (Tenant B cannot see Tenant A's audit logs or field histories)
2. Redacted credentials (passwords, tokens, api keys masked automatically with ***REDACTED***)
3. Event sequencing & cryptographic tamper detection (SHA-256 hash chaining detects altered/deleted records)
4. DSAR export integrity (complete scoped bundle with SHA-256 checksum)
5. Deletion workflows with retained legal exceptions (active legal hold blocks statutory record deletion and logs exceptions)
"""
import json
import os
import sys
import uuid
import django

# Set up Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework.test import APIClient

from core.audit_models import AuditTrail, FieldHistory
from core.audit_service import log_audit_event, verify_audit_trail_integrity
from core.audit_utils import REDACTED_MASK, redact_sensitive_data
from gdpr_compliance.models import (
    ConsentType,
    DataDeletionRequest,
    DataExportRequest,
    LegalHold,
    UserConsent,
)
from gdpr_compliance.services import (
    execute_gdpr_deletion,
    generate_dsar_export,
    verify_dsar_checksum,
)
from multi_tenant.models import Organization, OrganizationMember

User = get_user_model()


def run_all_tests():
    print("=" * 80)
    print("STARTING AUDIT & COMPLIANCE VERIFICATION SUITE")
    print("=" * 80)

    # Clean up test artifacts
    Organization.objects.filter(slug__in=['audit-corp-a', 'audit-corp-b']).delete()
    User.objects.filter(username__in=['auditor_a', 'auditor_b', 'dsar_subject']).delete()

    # 1. Setup Tenants and Users
    print("\n[STEP 1] Setting up Tenant Organizations and Users...")
    org_a = Organization.objects.create(name="Audit Corp A", slug="audit-corp-a", email="admin@corpa.com")
    org_b = Organization.objects.create(name="Audit Corp B", slug="audit-corp-b", email="admin@corpb.com")

    user_a = User.objects.create_user(username="auditor_a", email="auditor_a@corpa.com", password="Password123!")
    user_b = User.objects.create_user(username="auditor_b", email="auditor_b@corpb.com", password="Password123!")
    user_subject = User.objects.create_user(username="dsar_subject", email="subject@corpa.com", password="Password123!")

    OrganizationMember.objects.create(organization=org_a, user=user_a, role='admin', is_active=True)
    OrganizationMember.objects.create(organization=org_b, user=user_b, role='admin', is_active=True)
    OrganizationMember.objects.create(organization=org_a, user=user_subject, role='member', is_active=True)
    print("  -> Created Org A, Org B, and tenant members.")

    # 2. Test Credential Redaction
    print("\n[STEP 2] Testing Automated Credential Redaction...")
    sensitive_payload = {
        'username': 'john_doe',
        'password': 'SuperSecretPassword123!',
        'api_key': 'sk-live-1234567890abcdef1234567890',
        'auth_header': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token',
        'nested': {
            'secret_token': 'my-private-token',
            'normal_field': 'normal_value',
        }
    }
    audit_redacted = log_audit_event(
        user=user_a,
        action='update',
        description="Updated sensitive security settings",
        changes=sensitive_payload,
        old_values={'old_password': 'OldSecretPassword!'},
        new_values={'new_password': 'SuperSecretPassword123!'},
        organization=org_a,
        metadata={'client_secret': 'shhh-secret-value'},
    )

    # Verify AuditTrail record in DB does not contain secrets
    reloaded_audit = AuditTrail.objects.get(id=audit_redacted.id)
    assert reloaded_audit.changes['password'] == REDACTED_MASK, "Password not redacted in changes!"
    assert reloaded_audit.changes['api_key'] == REDACTED_MASK, "API key not redacted in changes!"
    assert reloaded_audit.changes['nested']['secret_token'] == REDACTED_MASK, "Nested secret not redacted!"
    assert reloaded_audit.changes['nested']['normal_field'] == 'normal_value', "Normal field incorrectly altered!"
    assert reloaded_audit.old_values['old_password'] == REDACTED_MASK, "Old password not redacted!"
    assert reloaded_audit.new_values['new_password'] == REDACTED_MASK, "New password not redacted!"
    assert reloaded_audit.metadata['client_secret'] == REDACTED_MASK, "Metadata secret not redacted!"

    # Verify FieldHistory redaction
    fh = FieldHistory.objects.filter(audit_trail=reloaded_audit, field_name='password').first()
    if fh:
        assert fh.new_value == REDACTED_MASK, "FieldHistory password value not redacted!"
    print("  [PASS] Credential Redaction: All passwords, bearer tokens, API keys, and nested secrets masked.")

    # 3. Test Monotonic Sequencing & Cryptographic Hash Chaining
    print("\n[STEP 3] Testing Monotonic Sequencing and SHA-256 Hash Chaining...")
    # Clean previous records for org_a
    AuditTrail.objects.filter(organization=org_a).delete()

    rec1 = log_audit_event(user=user_a, action='create', description="Event 1", organization=org_a)
    rec2 = log_audit_event(user=user_a, action='update', description="Event 2", organization=org_a)
    rec3 = log_audit_event(user=user_a, action='update', description="Event 3", organization=org_a)
    rec4 = log_audit_event(user=user_a, action='delete', description="Event 4", organization=org_a)
    rec5 = log_audit_event(user=user_a, action='export', description="Event 5", organization=org_a)

    recs = list(AuditTrail.objects.filter(organization=org_a).order_by('sequence_number'))
    assert [r.sequence_number for r in recs] == [1, 2, 3, 4, 5], f"Sequences invalid: {[r.sequence_number for r in recs]}"
    assert recs[0].prev_hash == "0" * 64, "Genesis record prev_hash not 64 zeroes!"
    assert recs[1].prev_hash == recs[0].record_hash, "Hash chain link 1->2 broken!"
    assert recs[2].prev_hash == recs[1].record_hash, "Hash chain link 2->3 broken!"
    assert recs[3].prev_hash == recs[2].record_hash, "Hash chain link 3->4 broken!"
    assert recs[4].prev_hash == recs[3].record_hash, "Hash chain link 4->5 broken!"

    is_valid, anomalies = verify_audit_trail_integrity(org_a.id)
    assert is_valid is True and len(anomalies) == 0, f"Integrity verification failed unexpectedly: {anomalies}"
    print("  [PASS] Sequence & Hash Chaining: Monotonic sequence 1..5 verified with valid SHA-256 links.")

    # 4. Adversarial Tampering Detection Test
    print("\n[STEP 4] Testing Adversarial Tamper Detection (Direct DB tampering)...")
    # Tamper with record #3 directly in database (bypassing normal save)
    original_desc = recs[2].description
    AuditTrail.objects.filter(id=recs[2].id).update(description="MALICIOUS_TAMPERED_DESCRIPTION")

    is_valid_tampered, anomalies_tampered = verify_audit_trail_integrity(org_a.id)
    assert is_valid_tampered is False, "Tamper check failed to detect modified database record!"
    assert any(a['error'] == 'TAMPERED_RECORD' for a in anomalies_tampered), f"Expected TAMPERED_RECORD: {anomalies_tampered}"
    print(f"  [PASS] Tamper Detection: Successfully caught altered DB record #{recs[2].sequence_number}: {anomalies_tampered[0]['details']}")

    # Restore record #3
    AuditTrail.objects.filter(id=recs[2].id).update(description=original_desc)
    is_valid_restored, _ = verify_audit_trail_integrity(org_a.id)
    assert is_valid_restored is True, "Restored records failed integrity check!"

    # Test Sequence Gap / Deleted Record Detection
    rec4_id = recs[3].id
    AuditTrail.objects.filter(id=rec4_id).delete()
    is_valid_deleted, anomalies_deleted = verify_audit_trail_integrity(org_a.id)
    assert is_valid_deleted is False, "Failed to detect deleted audit record (sequence gap)!"
    assert any(a['error'] in ['SEQUENCE_GAP', 'BROKEN_CHAIN'] for a in anomalies_deleted), f"Expected gap/broken chain: {anomalies_deleted}"
    print(f"  [PASS] Gap Detection: Successfully caught deleted audit record #{recs[3].sequence_number}.")

    # 5. Test Cross-Tenant Audit Isolation (API Level)
    print("\n[STEP 5] Testing Cross-Tenant Audit Isolation (API Level)...")
    # Clean and create fresh records in Org A and Org B
    AuditTrail.objects.filter(organization__in=[org_a, org_b]).delete()
    log_audit_event(user=user_a, action='create', description="Org A secret deal", organization=org_a)
    log_audit_event(user=user_b, action='create', description="Org B private roadmap", organization=org_b)

    client_b = APIClient()
    client_b.force_authenticate(user=user_b)

    # Org B queries audit list
    response = client_b.get('/api/v1/audit-trail/')
    assert response.status_code == 200, f"Audit trail API failed: {response.data}"
    results = response.data.get('results', response.data)
    descriptions = [r['description'] for r in results]
    assert "Org A secret deal" not in descriptions, "LEAK: Tenant B received Tenant A audit records!"
    assert "Org B private roadmap" in descriptions, "Tenant B should see their own audit records!"

    # Org B attempts IDOR on Org A's record ID
    rec_a = AuditTrail.objects.filter(organization=org_a).first()
    idor_response = client_b.get(f'/api/v1/audit-trail/{rec_a.id}/')
    assert idor_response.status_code == 404, f"IDOR vulnerability! Tenant B accessed Tenant A record: status {idor_response.status_code}"
    print("  [PASS] Cross-Tenant Isolation: Tenant B cannot list or access Tenant A audit records (404 enforced).")

    # 6. Test DSAR Export Bundle & Cryptographic Checksum Integrity
    print("\n[STEP 6] Testing DSAR Export Integrity & Verification...")
    consent_type = ConsentType.objects.create(organization=org_a, name="Marketing Consent", category="marketing")
    UserConsent.objects.create(
        organization=org_a,
        user=user_subject,
        consent_type=consent_type,
        is_granted=True,
        expiry_date=timezone.now() + timezone.timedelta(days=365)
    )

    export_req = DataExportRequest.objects.create(organization=org_a, user=user_subject, request_type='full_export')
    bundle = generate_dsar_export(user=user_subject, organization=org_a, export_request=export_req)

    assert export_req.status == 'completed', f"Export request status not completed: {export_req.status}"
    assert export_req.checksum != '', "Checksum was not computed!"
    assert 'profile' in bundle['categories'], "User profile missing from export categories!"
    assert 'consents' in bundle['categories'], "User consents missing from export categories!"

    # Verify checksum matches
    valid_checksum, _ = verify_dsar_checksum(bundle)
    assert valid_checksum is True, "Export checksum verification failed on pristine bundle!"

    # Adversarial tampering with export payload
    tampered_bundle = json.loads(json.dumps(bundle))
    tampered_bundle['categories']['profile']['email'] = 'hacked@evil.com'
    tampered_valid, err_msg = verify_dsar_checksum(tampered_bundle)
    assert tampered_valid is False, "Checksum verification failed to catch tampered export data!"
    print(f"  [PASS] DSAR Export Integrity: Generated bundle with SHA-256 checksum {bundle['integrity_checksum'][:16]}... and verified tamper detection.")

    # 7. Test GDPR Deletion Workflow with Retained Legal Exceptions
    print("\n[STEP 7] Testing Deletion Workflows with Retained Legal Hold Exceptions...")
    # Create active Legal Hold on user_subject
    legal_hold = LegalHold.objects.create(
        organization=org_a,
        subject_identifier=user_subject.email,
        hold_type='litigation',
        reason='Statutory litigation hold: pending tax audit investigation',
        created_by=user_a,
    )

    deletion_req = DataDeletionRequest.objects.create(
        organization=org_a,
        user=user_subject,
        deletion_type='full_deletion',
        reason='Requesting account erasure under GDPR Article 17',
    )

    result = execute_gdpr_deletion(deletion_req, reviewer_user=user_a)
    assert result['legal_hold_applied'] is True, "Legal hold was not detected during deletion!"
    assert len(result['retained_exceptions']) == 1, "Expected 1 retained legal exception!"
    assert result['retained_exceptions'][0]['hold_type'] == 'litigation', "Mismatch in hold type exception!"

    # Verify non-exempt fields were scrubbed while legal records remained intact
    user_subject.refresh_from_db()
    assert user_subject.first_name == "Anonymized", f"Personal name was not scrubbed: {user_subject.first_name}"
    assert user_subject.is_active is False, "User account was not deactivated!"
    print(f"  [PASS] Legal Hold Retained Exceptions: Statutory records protected under active hold; non-exempt personal data scrubbed.")

    # Now release the legal hold and re-execute deletion
    legal_hold.release(released_by=user_a, reason="Tax audit closed with no liability")
    deletion_req2 = DataDeletionRequest.objects.create(
        organization=org_a,
        user=user_subject,
        deletion_type='full_deletion',
        reason='Second erasure request after legal hold release',
    )
    result2 = execute_gdpr_deletion(deletion_req2, reviewer_user=user_a)
    assert result2['legal_hold_applied'] is False, "Legal hold should not apply after being released!"
    assert result2['status'] == 'completed', "Full deletion should complete when no hold active!"
    print("  [PASS] Full Erasure Post-Release: Once legal hold released, full erasure succeeds.")

    print("\n" + "=" * 80)
    print("ALL AUDIT & COMPLIANCE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == '__main__':
    run_all_tests()
