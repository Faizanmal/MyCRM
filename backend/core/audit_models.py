"""
Audit Trail System
Track all changes with detailed audit logs and version history
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import uuid

User = get_user_model()


class AuditTrail(models.Model):
    """Comprehensive audit trail for all CRM entities"""
    
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
    
    # Actor
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_trails')
    user_email = models.EmailField(help_text="Store email in case user is deleted")
    
    # Target object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    target = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=500, help_text="String representation of object")
    
    # Action details
    action = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.TextField(help_text="Human-readable description of the change")
    
    # Change details
    changes = models.JSONField(default=dict, help_text="Field-by-field changes")
    old_values = models.JSONField(default=dict, help_text="Previous values")
    new_values = models.JSONField(default=dict, help_text="New values")
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.UUIDField(default=uuid.uuid4, help_text="Group related changes")
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        db_table = 'crm_audit_trail'
        verbose_name = 'Audit Trail'
        verbose_name_plural = 'Audit Trails'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['content_type', 'object_id', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['request_id']),
        ]
    
    def __str__(self):
        return f"{self.user_email} {self.action} {self.content_type.model} at {self.timestamp}"


class FieldHistory(models.Model):
    """Track individual field value history"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Target object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    target = GenericForeignKey('content_type', 'object_id')
    
    # Field details
    field_name = models.CharField(max_length=100)
    field_label = models.CharField(max_length=100, blank=True)
    
    # Values
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
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
            models.Index(fields=['content_type', 'object_id', 'field_name', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.field_name}: {self.old_value_display} → {self.new_value_display}"


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
