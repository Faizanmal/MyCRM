"""
Unit & Integration Tests for Audit Trail, Cryptographic Integrity, Credential Redaction,
DSAR Exports, and Legal Hold Deletion Workflows.
"""
import json
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from core.audit_models import AuditTrail, FieldHistory
from core.audit_service import log_audit_event, verify_audit_trail_integrity
from core.audit_utils import REDACTED_MASK
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


@pytest.fixture
def org_setup(db):
    org_a = Organization.objects.create(name="Test Org A", slug="test-org-a", email="a@org.com")
    org_b = Organization.objects.create(name="Test Org B", slug="test-org-b", email="b@org.com")

    user_a = User.objects.create_user(username="user_a", email="user_a@org.com", password="Password123!")
    user_b = User.objects.create_user(username="user_b", email="user_b@org.com", password="Password123!")

    OrganizationMember.objects.create(organization=org_a, user=user_a, role='admin', is_active=True)
    OrganizationMember.objects.create(organization=org_b, user=user_b, role='admin', is_active=True)

    return {
        'org_a': org_a,
        'org_b': org_b,
        'user_a': user_a,
        'user_b': user_b,
    }


@pytest.mark.django_db
def test_credential_redaction(org_setup):
    """Ensure sensitive credentials and tokens are masked with ***REDACTED***"""
    org_a = org_setup['org_a']
    user_a = org_setup['user_a']

    audit = log_audit_event(
        user=user_a,
        action='update',
        description="Changed API keys",
        changes={
            'api_key': 'sk-test-1234567890abcdef1234567890',
            'auth': 'Bearer secret-jwt-token-string',
            'password': 'PlainTextPassword123!',
            'normal_key': 'safe_value',
        },
        old_values={'password': 'OldPassword!'},
        organization=org_a,
    )

    audit.refresh_from_db()
    assert audit.changes['api_key'] == REDACTED_MASK
    assert audit.changes['password'] == REDACTED_MASK
    assert audit.changes['normal_key'] == 'safe_value'
    assert audit.old_values['password'] == REDACTED_MASK


@pytest.mark.django_db
def test_monotonic_hash_chaining_and_tamper_detection(org_setup):
    """Ensure monotonic sequencing and cryptographic SHA-256 tamper detection"""
    org_a = org_setup['org_a']
    user_a = org_setup['user_a']

    rec1 = log_audit_event(user=user_a, action='create', description="Item 1", organization=org_a)
    rec2 = log_audit_event(user=user_a, action='update', description="Item 2", organization=org_a)
    rec3 = log_audit_event(user=user_a, action='delete', description="Item 3", organization=org_a)

    assert rec1.sequence_number == 1
    assert rec2.sequence_number == 2
    assert rec3.sequence_number == 3

    assert rec1.prev_hash == "0" * 64
    assert rec2.prev_hash == rec1.record_hash
    assert rec3.prev_hash == rec2.record_hash

    is_valid, anomalies = verify_audit_trail_integrity(org_a.id)
    assert is_valid is True
    assert len(anomalies) == 0

    # Tampering test
    AuditTrail.objects.filter(id=rec2.id).update(description="TAMPERED")
    is_valid, anomalies = verify_audit_trail_integrity(org_a.id)
    assert is_valid is False
    assert any(a['error'] == 'TAMPERED_RECORD' for a in anomalies)


@pytest.mark.django_db
def test_cross_tenant_audit_isolation(org_setup):
    """Ensure Tenant B cannot access Tenant A's audit logs via list or detail IDOR"""
    org_a = org_setup['org_a']
    org_b = org_setup['org_b']
    user_a = org_setup['user_a']
    user_b = org_setup['user_b']

    log_a = log_audit_event(user=user_a, action='create', description="Org A Log", organization=org_a)
    log_b = log_audit_event(user=user_b, action='create', description="Org B Log", organization=org_b)

    client = APIClient()
    client.force_authenticate(user=user_b)

    # List endpoint
    res = client.get('/api/v1/audit-trail/')
    assert res.status_code == 200
    results = res.data.get('results', res.data)
    descriptions = [r['description'] for r in results]
    assert "Org A Log" not in descriptions
    assert "Org B Log" in descriptions

    # Detail endpoint IDOR test
    res_idor = client.get(f'/api/v1/audit-trail/{log_a.id}/')
    assert res_idor.status_code == 404


@pytest.mark.django_db
def test_dsar_export_integrity(org_setup):
    """Ensure DSAR bundle includes user data, SHA-256 checksum, and verifies accurately"""
    org_a = org_setup['org_a']
    user_a = org_setup['user_a']

    req = DataExportRequest.objects.create(organization=org_a, user=user_a)
    bundle = generate_dsar_export(user=user_a, organization=org_a, export_request=req)

    assert req.status == 'completed'
    assert len(req.checksum) == 64
    valid, _ = verify_dsar_checksum(bundle)
    assert valid is True

    # Tamper with bundle
    bundle['categories']['profile']['email'] = 'attacker@evil.com'
    valid_tampered, _ = verify_dsar_checksum(bundle)
    assert valid_tampered is False


@pytest.mark.django_db
def test_legal_hold_deletion_retention(org_setup):
    """Ensure active legal hold prevents deletion of statutory records and documents exceptions"""
    org_a = org_setup['org_a']
    user_a = org_setup['user_a']

    hold = LegalHold.objects.create(
        organization=org_a,
        subject_identifier=user_a.email,
        hold_type='tax_audit',
        reason='IRS Tax Audit in progress',
    )

    del_req = DataDeletionRequest.objects.create(
        organization=org_a,
        user=user_a,
        deletion_type='full_deletion',
    )

    result = execute_gdpr_deletion(del_req, reviewer_user=user_a)
    assert result['legal_hold_applied'] is True
    assert len(result['retained_exceptions']) == 1
    assert result['retained_exceptions'][0]['hold_type'] == 'tax_audit'

    user_a.refresh_from_db()
    assert user_a.first_name == "Anonymized"
    assert user_a.is_active is False


@pytest.mark.django_db
def test_adversarial_wrong_tenant_cannot_access_or_approve_deletion(org_setup):
    """Ensure Tenant B cannot access or approve Tenant A's deletion or export requests"""
    org_a = org_setup['org_a']
    org_b = org_setup['org_b']
    user_a = org_setup['user_a']
    user_b = org_setup['user_b']

    del_req = DataDeletionRequest.objects.create(
        organization=org_a,
        user=user_a,
        deletion_type='full_deletion',
    )
    exp_req = DataExportRequest.objects.create(
        organization=org_a,
        user=user_a,
    )

    client_b = APIClient()
    client_b.force_authenticate(user=user_b)

    # Tenant B tries to view Tenant A's deletion request detail
    res_del = client_b.get(f'/api/v1/gdpr/deletion-requests/{del_req.id}/')
    assert res_del.status_code == 404

    # Tenant B tries to approve Tenant A's deletion request
    res_approve = client_b.post(f'/api/v1/gdpr/deletion-requests/{del_req.id}/approve/')
    assert res_approve.status_code == 404

    # Tenant B tries to view Tenant A's export request detail
    res_exp = client_b.get(f'/api/v1/gdpr/export-requests/{exp_req.id}/')
    assert res_exp.status_code == 404


@pytest.mark.django_db
def test_adversarial_insufficient_role_rejected(org_setup):
    """Ensure regular tenant member without admin/compliance role is rejected with 403"""
    org_a = org_setup['org_a']
    user_member = User.objects.create_user(username="member_user", email="member@org.com", password="Password123!")
    OrganizationMember.objects.create(organization=org_a, user=user_member, role='member', is_active=True)

    del_req = DataDeletionRequest.objects.create(
        organization=org_a,
        user=user_member,
        deletion_type='full_deletion',
    )

    client = APIClient()
    client.force_authenticate(user=user_member)

    # Member tries to approve a deletion request -> 403 Forbidden
    res_approve = client.post(f'/api/v1/gdpr/deletion-requests/{del_req.id}/approve/')
    assert res_approve.status_code == 403

    # Member tries to create a legal hold -> 403 Forbidden
    res_hold = client.post('/api/v1/gdpr/legal-holds/', {
        'subject_identifier': 'target@org.com',
        'hold_type': 'litigation',
        'reason': 'Unauthorized legal hold attempt',
    })
    assert res_hold.status_code == 403

    # Member tries to verify audit integrity -> 403 Forbidden
    res_verify = client.get('/api/v1/audit-trail/verify_integrity/')
    assert res_verify.status_code == 403


@pytest.mark.django_db
def test_adversarial_anonymous_rejected():
    """Ensure unauthenticated requests are rejected with 401 across all endpoints"""
    client = APIClient()

    assert client.get('/api/v1/audit-trail/').status_code == 401
    assert client.get('/api/v1/audit-trail/verify_integrity/').status_code == 401
    assert client.get('/api/v1/gdpr/export-requests/').status_code == 401
    assert client.get('/api/v1/gdpr/deletion-requests/').status_code == 401
    assert client.get('/api/v1/gdpr/legal-holds/').status_code == 401


@pytest.mark.django_db
def test_async_tasks_idempotency_and_poison_quarantine(org_setup):
    """Ensure Celery tasks are idempotent against duplicate triggers and poison pills are quarantined"""
    from core.async_models import PoisonPillQuarantine
    from gdpr_compliance.tasks import execute_gdpr_deletion_task, process_dsar_export_task

    org_a = org_setup['org_a']
    user_a = org_setup['user_a']

    exp_req = DataExportRequest.objects.create(organization=org_a, user=user_a)

    # First execution completes
    res1 = process_dsar_export_task(str(exp_req.id))
    assert res1['status'] == 'completed'
    assert len(res1['checksum']) == 64

    # Second execution returns cached/already completed result without duplicate work
    res2 = process_dsar_export_task(str(exp_req.id))
    assert res2.get('status') in ('already_completed', 'completed')
    assert res2.get('checksum') == res1['checksum']

    # Poison pill test: non-existent ID triggers quarantine
    poison_res = process_dsar_export_task('00000000-0000-0000-0000-000000000000')
    assert poison_res['status'] == 'quarantined'
    assert PoisonPillQuarantine.objects.filter(task_name='process_dsar_export_task').exists()


@pytest.mark.django_db
def test_feature_flags_and_api_verify_integrity(org_setup, monkeypatch):
    """Ensure feature flag toggles work and API verify_integrity endpoint functions properly"""
    org_a = org_setup['org_a']
    user_a = org_setup['user_a']

    client = APIClient()
    client.force_authenticate(user=user_a)

    # 1. API audit integrity check succeeds for admin
    res = client.get('/api/v1/audit-trail/verify_integrity/')
    assert res.status_code == 200
    assert res.data['is_valid'] is True

    # 2. When AUDIT_TAMPER_DETECTION_ENABLED is false -> 503
    monkeypatch.setenv('AUDIT_TAMPER_DETECTION_ENABLED', '0')
    res_disabled = client.get('/api/v1/audit-trail/verify_integrity/')
    assert res_disabled.status_code == 503

    # 3. When GDPR_DSAR_EXPORT_ENABLED is false -> 503
    monkeypatch.setenv('GDPR_DSAR_EXPORT_ENABLED', '0')
    exp_req = DataExportRequest.objects.create(organization=org_a, user=user_a)
    res_export = client.post(f'/api/v1/gdpr/export-requests/{exp_req.id}/process_export/')
    assert res_export.status_code == 503
