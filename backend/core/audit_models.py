"""
Audit Trail System
Track all changes with detailed audit logs, version history,
monotonic sequencing, cryptographic SHA-256 tamper detection, and credential redaction.
"""
import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from core.audit_utils import (
    SENSITIVE_KEY_PATTERN,
    compute_audit_record_hash,
    redact_sensitive_data,
)

User = get_user_model()


class AuditTrail(models.Model):
    """Comprehensive, tamper-evident audit trail for CRM entities"""

    ACTION_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),
        ('export', 'Exported'),
        ('import', 'Imported'),
        ('share', 'Shared'),
        ('permission_change', 'Permission Changed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Multi-tenant isolation
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='audit_trails',
        db_index=True,
    )

    # Actor
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='audit_trails', null=True)
    user_email = models.EmailField(help_text="Store email in case user is deleted")

    # Target object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    target = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=500, help_text="String representation of object")

    # Action details
    action = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.TextField(help_text="Human-readable description of the change")

    # Change details (strictly redacted)
    changes = models.JSONField(default=dict, help_text="Field-by-field changes")
    old_values = models.JSONField(default=dict, help_text="Previous values")
    new_values = models.JSONField(default=dict, help_text="New values")

    # Request metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    request_id = models.UUIDField(default=uuid.uuid4, help_text="Group related changes")

    # Additional context
    metadata = models.JSONField(default=dict, blank=True)

    # Monotonic sequencing & cryptographic tamper-evident hash chaining
    sequence_number = models.PositiveBigIntegerField(default=0, db_index=True)
    prev_hash = models.CharField(max_length=64, blank=True, default='')
    record_hash = models.CharField(max_length=64, blank=True, default='', db_index=True)
    is_tampered = models.BooleanField(default=False)

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'crm_audit_trail'
        verbose_name = 'Audit Trail'
        verbose_name_plural = 'Audit Trails'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['organization', '-timestamp']),
            models.Index(fields=['organization', 'sequence_number']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['content_type', 'object_id', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['request_id']),
        ]

    def __str__(self):
        org_name = self.organization.name if self.organization else "System"
        return f"[{org_name}] #{self.sequence_number} {self.user_email} {self.action} {self.content_type.model} at {self.timestamp}"

    def save(self, *args, **kwargs):
        # 1. Enforce strict credential redaction
        if self.changes:
            self.changes = redact_sensitive_data(self.changes)
        if self.old_values:
            self.old_values = redact_sensitive_data(self.old_values)
        if self.new_values:
            self.new_values = redact_sensitive_data(self.new_values)
        if self.metadata:
            self.metadata = redact_sensitive_data(self.metadata)

        # 2. Resolve organization if not explicitly passed
        if not self.organization_id:
            from multi_tenant.middleware import get_current_organization
            org = get_current_organization()
            if org:
                self.organization = org
            elif self.target and hasattr(self.target, 'organization_id') and self.target.organization_id:
                self.organization_id = self.target.organization_id
            elif self.user and hasattr(self.user, 'organization_memberships'):
                first_membership = self.user.organization_memberships.first()
                if first_membership:
                    self.organization = first_membership.organization

        # 3. Monotonic sequence & Cryptographic SHA-256 hash chaining
        if not self.sequence_number or not self.record_hash:
            if not self.timestamp:
                self.timestamp = timezone.now()

            # Find latest existing audit record for this tenant
            if self.organization_id:
                latest = (
                    AuditTrail.objects.filter(organization_id=self.organization_id)
                    .exclude(id=self.id)
                    .order_by('-sequence_number')
                    .first()
                )
                if latest and latest.sequence_number > 0:
                    self.sequence_number = latest.sequence_number + 1
                    self.prev_hash = latest.record_hash
                else:
                    self.sequence_number = 1
                    self.prev_hash = "0" * 64
            else:
                latest = (
                    AuditTrail.objects.filter(organization__isnull=True)
                    .exclude(id=self.id)
                    .order_by('-sequence_number')
                    .first()
                )
                if latest and latest.sequence_number > 0:
                    self.sequence_number = latest.sequence_number + 1
                    self.prev_hash = latest.record_hash
                else:
                    self.sequence_number = 1
                    self.prev_hash = "0" * 64

            # Compute SHA-256 hash
            self.record_hash = compute_audit_record_hash(
                prev_hash=self.prev_hash,
                sequence_number=self.sequence_number,
                timestamp_iso=self.timestamp.isoformat(),
                organization_id=str(self.organization_id or 'none'),
                user_id=str(self.user_id or 'none'),
                action=str(self.action or ''),
                description=str(self.description or ''),
                content_type_id=str(self.content_type_id or ''),
                object_id=str(self.object_id or ''),
                changes=self.changes or {},
                new_values=self.new_values or {},
                metadata=self.metadata or {},
            )

        super().save(*args, **kwargs)


class FieldHistory(models.Model):
    """Track individual field value history with tenant isolation and redaction"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Multi-tenant isolation
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='field_histories',
        db_index=True,
    )

    # Target object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    target = GenericForeignKey('content_type', 'object_id')

    # Field details
    field_name = models.CharField(max_length=100)
    field_label = models.CharField(max_length=100, blank=True)

    # Values
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    old_value_display = models.TextField(blank=True, help_text="Human-readable old value")
    new_value_display = models.TextField(blank=True, help_text="Human-readable new value")

    # Change metadata
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(default=timezone.now)
    audit_trail = models.ForeignKey(AuditTrail, on_delete=models.CASCADE, related_name='field_changes')

    class Meta:
        db_table = 'crm_field_history'
        verbose_name = 'Field History'
        verbose_name_plural = 'Field Histories'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['organization', '-changed_at']),
            models.Index(fields=['content_type', 'object_id', 'field_name', '-changed_at']),
        ]

    def __str__(self):
        return f"{self.field_name}: {self.old_value_display} → {self.new_value_display}"

    def save(self, *args, **kwargs):
        # Enforce credential redaction on field changes
        if SENSITIVE_KEY_PATTERN.search(self.field_name):
            self.old_value = '***REDACTED***'
            self.new_value = '***REDACTED***'
            self.old_value_display = '***REDACTED***'
            self.new_value_display = '***REDACTED***'
        else:
            self.old_value = redact_sensitive_data(self.old_value)
            self.new_value = redact_sensitive_data(self.new_value)
            self.old_value_display = redact_sensitive_data(self.old_value_display)
            self.new_value_display = redact_sensitive_data(self.new_value_display)

        if not self.organization_id and self.audit_trail and self.audit_trail.organization_id:
            self.organization_id = self.audit_trail.organization_id

        super().save(*args, **kwargs)


class DataSnapshot(models.Model):
    """Periodic snapshots of important data for recovery"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Target object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    target = GenericForeignKey('content_type', 'object_id')

    # Snapshot data
    snapshot_data = models.JSONField(help_text="Complete object data at this point in time")
    version = models.IntegerField(default=1, help_text="Version number")

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, help_text="Optional note about this snapshot")

    class Meta:
        db_table = 'crm_data_snapshots'
        verbose_name = 'Data Snapshot'
        verbose_name_plural = 'Data Snapshots'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-created_at']),
        ]

    def __str__(self):
        return f"{self.content_type.model} {self.object_id} v{self.version}"


class AuditConfiguration(models.Model):
    """Configuration for audit trail settings"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What to audit
    model_name = models.CharField(max_length=100, unique=True)
    enabled = models.BooleanField(default=True)

    # Audit settings
    track_creates = models.BooleanField(default=True)
    track_updates = models.BooleanField(default=True)
    track_deletes = models.BooleanField(default=True)
    track_views = models.BooleanField(default=False, help_text="Track read operations")

    # Fields to exclude from tracking
    excluded_fields = models.JSONField(default=list, help_text="Fields to not track changes for")

    # Retention
    retention_days = models.IntegerField(default=365, help_text="Days to keep audit records")

    # Snapshots
    enable_snapshots = models.BooleanField(default=False)
    snapshot_frequency_days = models.IntegerField(default=7, help_text="Days between automatic snapshots")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_audit_configuration'
        verbose_name = 'Audit Configuration'
        verbose_name_plural = 'Audit Configurations'

    def __str__(self):
        return f"Audit config for {self.model_name}"
