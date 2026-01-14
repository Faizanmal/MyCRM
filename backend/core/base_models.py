# MyCRM Backend - Enhanced Base Models and Mixins
"""
Core models, mixins, and base classes for the MyCRM application.
Provides standardized functionality across all apps.
"""

import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

# =============================================================================
# Abstract Base Models
# =============================================================================

class TimeStampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at fields.
    All models should inherit from this for consistent timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(models.Model):
    """
    Abstract base model with UUID as primary key.
    Use for models that need globally unique identifiers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base model with soft delete functionality.
    Objects are marked as deleted instead of being removed from the database.
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard_delete=False, user=None):
        """Soft delete by default, hard delete if specified."""
        if hard_delete:
            return super().delete(using=using, keep_parents=keep_parents)

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])


class OrganizationScopedModel(models.Model):
    """
    Abstract base model for multi-tenant organization scoping.
    All organization-specific data should inherit from this.
    """
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)ss'
    )

    class Meta:
        abstract = True


class OwnershipModel(models.Model):
    """
    Abstract base model for owner and assignee tracking.
    Common pattern for CRM entities.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_%(app_label)s_%(class)ss'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_%(app_label)s_%(class)ss'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(app_label)s_%(class)ss'
    )

    class Meta:
        abstract = True


# =============================================================================
# Comprehensive Base Model
# =============================================================================

class BaseModel(TimeStampedModel, SoftDeleteModel, OrganizationScopedModel, OwnershipModel):
    """
    Comprehensive base model combining all common functionality.
    Use this as the base for most CRM entities.
    """

    class Meta:
        abstract = True


# =============================================================================
# Audit Trail Mixin
# =============================================================================

class AuditTrailMixin:
    """
    Mixin to track all changes to a model.
    Call track_change() before save to log changes.
    """

    def get_changed_fields(self, old_instance):
        """Get dictionary of changed fields."""
        changes = {}
        for field in self._meta.fields:
            field_name = field.name
            old_value = getattr(old_instance, field_name, None)
            new_value = getattr(self, field_name, None)
            if old_value != new_value:
                changes[field_name] = {
                    'old': str(old_value) if old_value else None,
                    'new': str(new_value) if new_value else None
                }
        return changes

    def track_change(self, user, action='update', changes=None):
        """Log a change to the audit trail."""
        from core.models import AuditLog
        AuditLog.objects.create(
            user=user,
            action=action,
            content_type=ContentType.objects.get_for_model(self),
            object_id=str(self.pk),
            object_repr=str(self),
            changes=changes or {}
        )


# =============================================================================
# Tag Support Mixin
# =============================================================================

class TaggableMixin(models.Model):
    """
    Mixin to add tagging support to a model.
    Stores tags as a JSON array for flexibility.
    """
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        abstract = True

    def add_tag(self, tag):
        """Add a tag if not already present."""
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])

    def remove_tag(self, tag):
        """Remove a tag if present."""
        tag = tag.lower().strip()
        if tag in self.tags:
            self.tags.remove(tag)
            self.save(update_fields=['tags'])

    def has_tag(self, tag):
        """Check if tag exists."""
        return tag.lower().strip() in self.tags


# =============================================================================
# Custom Fields Mixin
# =============================================================================

class CustomFieldsMixin(models.Model):
    """
    Mixin to add custom fields support to a model.
    Stores custom fields as a JSON object.
    """
    custom_fields = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True

    def get_custom_field(self, key, default=None):
        """Get a custom field value."""
        return self.custom_fields.get(key, default)

    def set_custom_field(self, key, value):
        """Set a custom field value."""
        self.custom_fields[key] = value
        self.save(update_fields=['custom_fields'])

    def delete_custom_field(self, key):
        """Delete a custom field."""
        if key in self.custom_fields:
            del self.custom_fields[key]
            self.save(update_fields=['custom_fields'])


# =============================================================================
# Activity Tracking Mixin
# =============================================================================

class ActivityTrackableMixin(models.Model):
    """
    Mixin to add activity tracking to a model.
    Tracks last activity and activity count.
    """
    last_activity_at = models.DateTimeField(blank=True)
    activity_count = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def record_activity(self):
        """Record an activity occurrence."""
        self.last_activity_at = timezone.now()
        self.activity_count += 1
        self.save(update_fields=['last_activity_at', 'activity_count'])


# =============================================================================
# Core Audit Log Model
# =============================================================================

class AuditLog(models.Model):
    """
    Comprehensive audit log for tracking all changes.
    Stores who did what, when, and what changed.
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Actor information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    ip_address = models.GenericIPAddressField(blank=True)
    user_agent = models.TextField(blank=True, default='')
    session_id = models.CharField(max_length=255, blank=True, default='')

    # Action information
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)

    # Target object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255, blank=True, default='')
    object_repr = models.CharField(max_length=500, blank=True, default='')

    # Changes
    changes = models.JSONField(default=dict, blank=True)

    # Organization for multi-tenancy
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Request context
    request_id = models.CharField(max_length=255, blank=True, default='')
    endpoint = models.CharField(max_length=500, blank=True, default='')
    method = models.CharField(max_length=10, blank=True, default='')

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['organization', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.object_repr} - {self.timestamp}"


# =============================================================================
# System Configuration Model
# =============================================================================

class SystemConfiguration(models.Model):
    """
    Key-value store for system-wide configuration.
    Supports different value types and organization-specific overrides.
    """
    VALUE_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ]

    key = models.CharField(max_length=255, db_index=True)
    value = models.TextField()
    value_type = models.CharField(max_length=20, choices=VALUE_TYPES, default='string')
    description = models.TextField(blank=True, default='')

    # Organization for tenant-specific config (null = global)
    organization = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Metadata
    is_sensitive = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['key', 'organization']
        ordering = ['key']

    def __str__(self):
        org = self.organization.name if self.organization else 'Global'
        return f"{self.key} ({org})"

    def get_typed_value(self):
        """Return the value cast to its proper type."""
        if self.value_type == 'integer':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.value_type == 'json':
            import json
            return json.loads(self.value)
        return self.value

    @classmethod
    def get(cls, key, organization=None, default=None):
        """Get a configuration value with fallback to global."""
        try:
            # Try organization-specific first
            if organization:
                config = cls.objects.get(key=key, organization=organization)
                return config.get_typed_value()
        except cls.DoesNotExist:
            pass

        try:
            # Fall back to global
            config = cls.objects.get(key=key, organization=None)
            return config.get_typed_value()
        except cls.DoesNotExist:
            return default


# =============================================================================
# Feature Flag Model
# =============================================================================

class FeatureFlag(models.Model):
    """
    Feature flags for controlling feature rollouts.
    Supports global, organization, and user-level targeting.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')

    # Enable states
    is_enabled = models.BooleanField(default=False)
    enabled_for_staff = models.BooleanField(default=False)
    enabled_for_superuser = models.BooleanField(default=True)

    # Percentage rollout
    rollout_percentage = models.PositiveIntegerField(default=0)

    # Organization targeting
    enabled_organizations = models.ManyToManyField(
        'multi_tenant.Organization',
        blank=True,
        related_name='enabled_features'
    )

    # User targeting
    enabled_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='enabled_features'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        status = '✓' if self.is_enabled else '✗'
        return f"{status} {self.name}"

    def is_enabled_for(self, user):
        """Check if feature is enabled for a specific user."""
        # Superuser override
        if user.is_superuser and self.enabled_for_superuser:
            return True

        # Staff override
        if user.is_staff and self.enabled_for_staff:
            return True

        # Global disabled
        if not self.is_enabled:
            return False

        # User-specific
        if self.enabled_users.filter(pk=user.pk).exists():
            return True

        # Organization-specific
        if hasattr(user, 'organization') and user.organization:
            if self.enabled_organizations.filter(pk=user.organization.pk).exists():
                return True

        # Percentage rollout
        if self.rollout_percentage > 0:
            import hashlib
            hash_input = f"{self.name}:{user.pk}"
            hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
            return (hash_value % 100) < self.rollout_percentage

        return False


# =============================================================================
# Notification Model
# =============================================================================

class Notification(TimeStampedModel):
    """
    User notifications supporting multiple channels.
    """
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    CHANNELS = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('push', 'Push'),
        ('sms', 'SMS'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Recipient
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    # Content
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')

    # Channel
    channel = models.CharField(max_length=20, choices=CHANNELS, default='in_app')

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True)

    # Related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True)
    object_id = models.CharField(max_length=255, blank=True, default='')

    # Action URL
    action_url = models.URLField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


# =============================================================================
# Model Managers
# =============================================================================

class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        return super().get_queryset()

    def deleted_only(self):
        return super().get_queryset().filter(is_deleted=True)


class OrganizationScopedManager(models.Manager):
    """Manager that scopes queries to current organization."""

    def for_organization(self, organization):
        return self.get_queryset().filter(organization=organization)
