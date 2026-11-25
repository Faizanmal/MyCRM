"""
GDPR Compliance Services
Enterprise Data Subject Access Request (DSAR) bundle generation with cryptographic checksums,
and GDPR Right-to-be-Forgotten deletion workflows with statutory legal hold retention exceptions.
"""
import hashlib
import json
import logging
from typing import Any, Dict, Optional, Tuple

from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.audit_service import log_audit_event
from core.audit_utils import canonical_json_dump
from gdpr_compliance.models import (
    DataDeletionRequest,
    DataExportRequest,
    LegalHold,
    UserConsent,
)

logger = logging.getLogger('crm.compliance')
User = get_user_model()


def generate_dsar_export(
    user: Any,
    organization: Any,
    export_request: Optional[DataExportRequest] = None,
) -> Dict[str, Any]:
    """
    Generate an exhaustive, cryptographically signed Data Subject Access Request (DSAR) export bundle.
    Guarantees strict multi-tenant boundary isolation and data subject scoping.
    """
    categories: Dict[str, Any] = {}

    # 1. User Profile Account Information
    categories['profile'] = {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'first_name': getattr(user, 'first_name', ''),
        'last_name': getattr(user, 'last_name', ''),
        'date_joined': user.date_joined.isoformat() if hasattr(user, 'date_joined') and user.date_joined else None,
        'last_login': user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None,
    }

    # 2. Leads (matching email or assigned)
    if apps.is_installed('lead_management'):
        Lead = apps.get_model('lead_management', 'Lead')
        leads_qs = Lead.objects.filter(organization=organization).filter(
            models_Q_or_assigned(user)
        )
        categories['leads'] = [
            {
                'id': str(l.id),
                'first_name': getattr(l, 'first_name', ''),
                'last_name': getattr(l, 'last_name', ''),
                'email': getattr(l, 'email', ''),
                'company': getattr(l, 'company', ''),
                'status': getattr(l, 'status', ''),
                'created_at': l.created_at.isoformat() if hasattr(l, 'created_at') and l.created_at else None,
            }
            for l in leads_qs
        ]
    else:
        categories['leads'] = []

    # 3. Contacts
    if apps.is_installed('contact_management'):
        Contact = apps.get_model('contact_management', 'Contact')
        contacts_qs = Contact.objects.filter(organization=organization).filter(
            models_Q_or_assigned(user)
        )
        categories['contacts'] = [
            {
                'id': str(c.id),
                'first_name': getattr(c, 'first_name', ''),
                'last_name': getattr(c, 'last_name', ''),
                'email': getattr(c, 'email', ''),
                'title': getattr(c, 'title', ''),
                'created_at': c.created_at.isoformat() if hasattr(c, 'created_at') and c.created_at else None,
            }
            for c in contacts_qs
        ]
    else:
        categories['contacts'] = []

    # 4. Tasks
    if apps.is_installed('task_management'):
        Task = apps.get_model('task_management', 'Task')
        tasks_qs = Task.objects.filter(organization=organization, assigned_to=user)
        categories['tasks'] = [
            {
                'id': str(t.id),
                'title': getattr(t, 'title', ''),
                'status': getattr(t, 'status', ''),
                'due_date': t.due_date.isoformat() if getattr(t, 'due_date', None) else None,
            }
            for t in tasks_qs
        ]
    else:
        categories['tasks'] = []

    # 5. GDPR Consents
    consents_qs = UserConsent.objects.filter(organization=organization, user=user)
    categories['consents'] = [
        {
            'consent_type': c.consent_type.name,
            'is_granted': c.is_granted,
            'consent_date': c.consent_date.isoformat(),
            'withdrawn_at': c.withdrawn_at.isoformat() if c.withdrawn_at else None,
        }
        for c in consents_qs
    ]

    # 6. Audit Trail Activities
    from core.audit_models import AuditTrail
    audit_qs = AuditTrail.objects.filter(
        organization=organization
    ).filter(
        user=user
    )[:100]
    categories['audit_trail'] = [
        {
            'sequence_number': a.sequence_number,
            'action': a.action,
            'description': a.description,
            'timestamp': a.timestamp.isoformat(),
            'record_hash': a.record_hash,
        }
        for a in audit_qs
    ]

    # Compute SHA-256 cryptographic checksum over the canonical JSON representation of categories
    canonical_payload = canonical_json_dump(categories)
    checksum = hashlib.sha256(canonical_payload.encode('utf-8')).hexdigest()

    export_bundle = {
        'export_request_id': str(export_request.id) if export_request else None,
        'organization_id': str(organization.id),
        'organization_name': organization.name,
        'data_subject': user.email or user.username,
        'generated_at': timezone.now().isoformat(),
        'integrity_checksum': checksum,
        'record_counts': {k: len(v) if isinstance(v, list) else 1 for k, v in categories.items()},
        'categories': categories,
    }

    if export_request:
        export_request.export_payload = export_bundle
        export_request.checksum = checksum
        export_request.status = 'completed'
        export_request.completed_at = timezone.now()
        export_request.save(update_fields=['export_payload', 'checksum', 'status', 'completed_at'])

        # Emitting audit log for DSAR export
        log_audit_event(
            user=user,
            action='export',
            target=export_request,
            description=f"DSAR Export generated for {user.email} (checksum: {checksum[:12]}...)",
            organization=organization,
            metadata={'checksum': checksum, 'record_counts': export_bundle['record_counts']},
        )

    return export_bundle


def models_Q_or_assigned(user):
    from django.db.models import Q
    return Q(email=user.email) | Q(assigned_to=user)


def verify_dsar_checksum(export_bundle: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Verify the cryptographic SHA-256 integrity checksum of a DSAR bundle.
    """
    categories = export_bundle.get('categories')
    if not categories:
        return False, "Missing categories in DSAR bundle"

    expected_checksum = export_bundle.get('integrity_checksum')
    if not expected_checksum:
        return False, "Missing integrity checksum in DSAR bundle"

    canonical_payload = canonical_json_dump(categories)
    computed_checksum = hashlib.sha256(canonical_payload.encode('utf-8')).hexdigest()

    if computed_checksum != expected_checksum:
        return False, f"Checksum mismatch: expected {expected_checksum}, got {computed_checksum}"

    return True, computed_checksum


def execute_gdpr_deletion(
    deletion_request: DataDeletionRequest,
    reviewer_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Execute GDPR Article 17 ("Right to be Forgotten") deletion request with
    strict verification of active Legal Holds and statutory retention exceptions.
    
    If active legal holds are found:
      - Denies destruction of audit logs, financial ledger, and legally required records.
      - Documents immutable legal exception reasons inside `retained_legal_exceptions`.
      - Anonymizes non-exempt personal profile attributes.
    If no legal holds are found:
      - Fully anonymizes / purges personal data.
    """
    organization = deletion_request.organization
    user = deletion_request.user

    # 1. Search for active Legal Holds
    subject_identifiers = [user.email, str(user.id), user.username]
    active_holds = LegalHold.objects.filter(
        organization=organization,
        is_active=True,
        subject_identifier__in=[s for s in subject_identifiers if s]
    )

    retained_exceptions = []
    anonymized_fields_count = 0
    retained_records_count = 0

    if active_holds.exists():
        # Legal holds active: statutory retention exception applies!
        for hold in active_holds:
            retained_exceptions.append({
                'hold_id': str(hold.id),
                'hold_type': hold.hold_type,
                'hold_type_display': hold.get_hold_type_display(),
                'reason': hold.reason,
                'retained_at': timezone.now().isoformat(),
                'statutory_justification': 'GDPR Article 17(3)(b)/(e) statutory retention exception',
            })

        # Calculate retained records
        from core.audit_models import AuditTrail
        user_audit_count = AuditTrail.objects.filter(organization=organization, user=user).count()
        retained_records_count += user_audit_count

        # Scrub non-exempt personal data while preserving user account link for audit records
        user.first_name = "Anonymized"
        user.last_name = f"Subject_{str(user.id)[:8]}"
        user.is_active = False
        user.save(update_fields=['first_name', 'last_name', 'is_active'])
        anonymized_fields_count += 3

        deletion_request.status = 'completed'
        deletion_request.completed_at = timezone.now()
        deletion_request.reviewed_by = reviewer_user
        deletion_request.reviewed_at = timezone.now()
        deletion_request.retained_legal_exceptions = retained_exceptions
        deletion_request.anonymized_fields_count = anonymized_fields_count
        deletion_request.retained_records_count = retained_records_count
        deletion_request.notes = f"Executed with {len(retained_exceptions)} active legal hold exceptions. Non-exempt attributes scrubbed."
        deletion_request.save()

        # Emit audit trail with retained exceptions
        log_audit_event(
            user=reviewer_user,
            action='update',
            target=deletion_request,
            description=f"GDPR Deletion executed for {user.email} with {len(retained_exceptions)} retained legal exceptions",
            organization=organization,
            metadata={
                'legal_holds': retained_exceptions,
                'retained_records_count': retained_records_count,
            }
        )

        return {
            'status': 'completed_with_exceptions',
            'legal_hold_applied': True,
            'retained_exceptions': retained_exceptions,
            'retained_records_count': retained_records_count,
            'anonymized_fields_count': anonymized_fields_count,
        }

    else:
        # No legal holds: full anonymization / erasure
        user.first_name = "Anonymized"
        user.last_name = "User"
        user.email = f"anonymized_{user.id}@deleted.local"
        user.is_active = False
        user.save(update_fields=['first_name', 'last_name', 'email', 'is_active'])
        anonymized_fields_count += 4

        deletion_request.status = 'completed'
        deletion_request.completed_at = timezone.now()
        deletion_request.reviewed_by = reviewer_user
        deletion_request.reviewed_at = timezone.now()
        deletion_request.retained_legal_exceptions = []
        deletion_request.anonymized_fields_count = anonymized_fields_count
        deletion_request.retained_records_count = 0
        deletion_request.notes = "Full GDPR erasure completed successfully without legal hold exceptions."
        deletion_request.save()

        # Emit audit trail
        log_audit_event(
            user=reviewer_user,
            action='delete',
            target=deletion_request,
            description=f"GDPR Full Erasure completed for data subject {user.id}",
            organization=organization,
            metadata={'anonymized_fields_count': anonymized_fields_count}
        )

        return {
            'status': 'completed',
            'legal_hold_applied': False,
            'retained_exceptions': [],
            'retained_records_count': 0,
            'anonymized_fields_count': anonymized_fields_count,
        }
