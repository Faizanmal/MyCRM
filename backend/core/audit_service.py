"""
Audit Service
Centralized service for writing tamper-evident audit logs and verifying cryptographic integrity.
"""
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from core.audit_models import AuditTrail, FieldHistory
from core.audit_utils import (
    compute_audit_record_hash,
    redact_sensitive_data,
)

logger = logging.getLogger('crm.audit')
User = get_user_model()


def log_audit_event(
    user: Optional[Any],
    action: str,
    target: Optional[Any] = None,
    description: str = "",
    changes: Optional[Dict[str, Any]] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    organization: Optional[Any] = None,
    request: Optional[Any] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditTrail:
    """
    Log an enterprise audit event with tenant boundary enforcement,
    cryptographic SHA-256 hash chaining, and automatic credential redaction.
    """
    # 1. Resolve actor details
    user_email = ""
    if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
        user_email = getattr(user, 'email', '') or getattr(user, 'username', '')
    elif user and hasattr(user, 'email'):
        user_email = user.email

    # 2. Extract request metadata if available
    if request:
        if not ip_address:
            x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded:
                ip_address = x_forwarded.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')
        if not user_agent:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not organization:
            organization = getattr(request, 'organization', None)

    # 3. Resolve organization
    if not organization and target:
        organization = getattr(target, 'organization', None)

    if not organization and user and hasattr(user, 'organization_memberships'):
        first_mem = user.organization_memberships.first()
        if first_mem:
            organization = first_mem.organization

    # 4. Resolve target details
    content_type = None
    object_id = ""
    object_repr = ""
    if target:
        content_type = ContentType.objects.get_for_model(target.__class__)
        object_id = str(getattr(target, 'pk', getattr(target, 'id', '')))
        object_repr = str(target)[:500]
    else:
        # Generic content type fallback (e.g. for system-level actions)
        content_type = ContentType.objects.get_for_model(AuditTrail)
        object_id = str(uuid.uuid4())
        object_repr = description[:500] if description else action

    # 5. Sanitize and redact all payloads
    sanitized_changes = redact_sensitive_data(changes or {})
    sanitized_old = redact_sensitive_data(old_values or {})
    sanitized_new = redact_sensitive_data(new_values or {})
    sanitized_meta = redact_sensitive_data(metadata or {})

    if not description:
        description = f"{action.capitalize()} {content_type.model} {object_repr}"

    # 6. Create AuditTrail record (triggers sequence & hash computation in save)
    audit_record = AuditTrail(
        organization=organization,
        user=user if user and hasattr(user, 'is_authenticated') and user.is_authenticated else None,
        user_email=user_email,
        content_type=content_type,
        object_id=object_id,
        object_repr=object_repr,
        action=action,
        description=description,
        changes=sanitized_changes,
        old_values=sanitized_old,
        new_values=sanitized_new,
        ip_address=ip_address,
        user_agent=user_agent or "",
        metadata=sanitized_meta,
        timestamp=timezone.now(),
    )
    audit_record.save()

    # 7. Record granular FieldHistory entries if field changes exist
    if sanitized_changes and isinstance(sanitized_changes, dict):
        for field_name, delta in sanitized_changes.items():
            old_val = ""
            new_val = ""
            if isinstance(delta, (list, tuple)) and len(delta) >= 2:
                old_val = str(delta[0])
                new_val = str(delta[1])
            elif isinstance(delta, dict) and ('old' in delta or 'new' in delta):
                old_val = str(delta.get('old', ''))
                new_val = str(delta.get('new', ''))
            else:
                new_val = str(delta)

            FieldHistory.objects.create(
                organization=organization,
                content_type=content_type,
                object_id=object_id,
                field_name=field_name,
                field_label=field_name.replace('_', ' ').title(),
                old_value=old_val,
                new_value=new_val,
                old_value_display=old_val,
                new_value_display=new_val,
                changed_by=audit_record.user,
                changed_at=audit_record.timestamp,
                audit_trail=audit_record,
            )

    return audit_record


def verify_audit_trail_integrity(organization_id: Any) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Validate the cryptographic SHA-256 hash chain and monotonic sequencing
    for a given organization's audit trail.
    
    Detects:
    1. SEQUENCE_GAP: Missing or deleted audit records in the sequence.
    2. BROKEN_CHAIN: prev_hash does not match the predecessor's record_hash.
    3. TAMPERED_RECORD: Record data was altered in DB, invalidating its cryptographic hash.
    """
    records = list(
        AuditTrail.objects.filter(organization_id=organization_id)
        .order_by('sequence_number', 'timestamp')
    )

    if not records:
        return True, []

    anomalies: List[Dict[str, Any]] = []
    expected_sequence = 1
    expected_prev_hash = "0" * 64

    for rec in records:
        # Check monotonic sequence order
        if rec.sequence_number != expected_sequence:
            anomalies.append({
                "record_id": str(rec.id),
                "sequence_number": rec.sequence_number,
                "error": "SEQUENCE_GAP",
                "details": f"Expected sequence {expected_sequence}, got {rec.sequence_number}",
                "expected": expected_sequence,
                "actual": rec.sequence_number,
            })

        # Check cryptographic chain link
        if rec.prev_hash != expected_prev_hash:
            anomalies.append({
                "record_id": str(rec.id),
                "sequence_number": rec.sequence_number,
                "error": "BROKEN_CHAIN",
                "details": f"prev_hash mismatch: expected {expected_prev_hash[:16]}..., got {rec.prev_hash[:16]}...",
                "expected_prev_hash": expected_prev_hash,
                "actual_prev_hash": rec.prev_hash,
            })

        # Recompute SHA-256 hash from canonical record components
        computed_hash = compute_audit_record_hash(
            prev_hash=rec.prev_hash,
            sequence_number=rec.sequence_number,
            timestamp_iso=rec.timestamp.isoformat(),
            organization_id=str(rec.organization_id or 'none'),
            user_id=str(rec.user_id or 'none'),
            action=str(rec.action or ''),
            description=str(rec.description or ''),
            content_type_id=str(rec.content_type_id or ''),
            object_id=str(rec.object_id or ''),
            changes=rec.changes or {},
            new_values=rec.new_values or {},
            metadata=rec.metadata or {},
        )

        if computed_hash != rec.record_hash:
            anomalies.append({
                "record_id": str(rec.id),
                "sequence_number": rec.sequence_number,
                "error": "TAMPERED_RECORD",
                "details": f"Cryptographic signature mismatch! Stored: {rec.record_hash[:16]}..., Computed: {computed_hash[:16]}...",
                "expected_hash": rec.record_hash,
                "computed_hash": computed_hash,
            })
            if not rec.is_tampered:
                rec.is_tampered = True
                rec.save(update_fields=['is_tampered'])

        # Advance expectations
        expected_sequence = rec.sequence_number + 1
        expected_prev_hash = rec.record_hash

    is_valid = len(anomalies) == 0
    return is_valid, anomalies
