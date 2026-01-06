"""
Admin Control Center Models - System administration, health monitoring, and bulk operations.
"""

import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class SystemHealthMetric(models.Model):
    """Stores system health metrics over time."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Metric identification
    metric_name = models.CharField(max_length=100)
    metric_category = models.CharField(
        max_length=50,
        choices=[
            ('performance', 'Performance'),
            ('database', 'Database'),
            ('cache', 'Cache'),
            ('queue', 'Queue'),
            ('storage', 'Storage'),
            ('api', 'API'),
            ('external', 'External Services'),
        ]
    )

    # Values
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    threshold_warning = models.FloatField(null=True)
    threshold_critical = models.FloatField(null=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('healthy', 'Healthy'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
            ('unknown', 'Unknown'),
        ],
        default='healthy'
    )

    # Context
    server_id = models.CharField(max_length=100, blank=True)
    additional_data = models.JSONField(default=dict)

    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_system_health_metric'
        indexes = [
            models.Index(fields=['metric_name', 'recorded_at']),
            models.Index(fields=['metric_category', 'recorded_at']),
            models.Index(fields=['status', 'recorded_at']),
        ]


class SystemAlert(models.Model):
    """System alerts and notifications."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=200)
    message = models.TextField()

    severity = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Info'),
            ('warning', 'Warning'),
            ('error', 'Error'),
            ('critical', 'Critical'),
        ]
    )

    category = models.CharField(max_length=50)
    source = models.CharField(max_length=100)  # Component that raised the alert

    # Related metric if applicable
    related_metric = models.ForeignKey(
        SystemHealthMetric,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('acknowledged', 'Acknowledged'),
            ('resolved', 'Resolved'),
            ('suppressed', 'Suppressed'),
        ],
        default='active'
    )

    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True)
    resolved_at = models.DateTimeField(null=True)

    # Notification tracking
    notifications_sent = models.JSONField(default=list)  # [{channel, sent_at}]

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_system_alert'
        ordering = ['-created_at']


class BulkOperation(models.Model):
    """Tracks bulk operations like imports, exports, mass updates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    operation_type = models.CharField(
        max_length=50,
        choices=[
            ('import', 'Import'),
            ('export', 'Export'),
            ('update', 'Mass Update'),
            ('delete', 'Mass Delete'),
            ('assign', 'Mass Assign'),
            ('merge', 'Merge Records'),
            ('migrate', 'Data Migration'),
        ]
    )

    entity_type = models.CharField(max_length=50)  # contacts, leads, etc.

    # Initiator
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bulk_operations'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
            ('paused', 'Paused'),
        ],
        default='pending'
    )

    # Progress
    total_records = models.PositiveIntegerField(default=0)
    processed_records = models.PositiveIntegerField(default=0)
    successful_records = models.PositiveIntegerField(default=0)
    failed_records = models.PositiveIntegerField(default=0)
    progress_percent = models.FloatField(default=0.0)

    # Configuration
    operation_config = models.JSONField(default=dict)
    # E.g., {"update_fields": {"status": "active"}, "filter": {...}}

    # Results
    result_file_url = models.URLField(blank=True)  # For exports
    error_log = models.JSONField(default=list)  # [{record_id, error}]

    # Timing
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    estimated_completion = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_bulk_operation'
        ordering = ['-created_at']


class CustomField(models.Model):
    """Custom fields that can be added to entities."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Target entity
    entity_type = models.CharField(max_length=50)  # contact, lead, opportunity, etc.

    # Field definition
    field_name = models.CharField(max_length=100)
    field_label = models.CharField(max_length=200)
    field_type = models.CharField(
        max_length=30,
        choices=[
            ('text', 'Text'),
            ('textarea', 'Text Area'),
            ('number', 'Number'),
            ('decimal', 'Decimal'),
            ('currency', 'Currency'),
            ('date', 'Date'),
            ('datetime', 'Date Time'),
            ('boolean', 'Boolean'),
            ('select', 'Single Select'),
            ('multiselect', 'Multi Select'),
            ('lookup', 'Lookup'),
            ('url', 'URL'),
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('file', 'File Attachment'),
        ]
    )

    # Field options
    options = models.JSONField(default=list)  # For select/multiselect
    default_value = models.JSONField(null=True, blank=True)
    placeholder = models.CharField(max_length=200, blank=True)
    help_text = models.TextField(blank=True)

    # Validation
    is_required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    min_length = models.PositiveIntegerField(null=True, blank=True)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    regex_pattern = models.CharField(max_length=500, blank=True)

    # Lookup configuration (for lookup type)
    lookup_entity = models.CharField(max_length=50, blank=True)
    lookup_display_field = models.CharField(max_length=100, blank=True)

    # Display settings
    show_in_list = models.BooleanField(default=False)
    show_in_create = models.BooleanField(default=True)
    show_in_detail = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    field_group = models.CharField(max_length=100, blank=True)

    # Access control
    editable_by_roles = ArrayField(models.CharField(max_length=50), default=list)
    visible_to_roles = ArrayField(models.CharField(max_length=50), default=list)

    # Status
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)  # System fields can't be deleted

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_custom_fields'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_custom_field'
        unique_together = ['entity_type', 'field_name']
        ordering = ['entity_type', 'display_order', 'field_name']


class CustomFieldValue(models.Model):
    """Stores values for custom fields."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    custom_field = models.ForeignKey(
        CustomField,
        on_delete=models.CASCADE,
        related_name='values'
    )

    # Generic foreign key simulation
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()

    # Value storage (use appropriate field based on type)
    value_text = models.TextField(blank=True)
    value_number = models.FloatField(null=True, blank=True)
    value_boolean = models.BooleanField(null=True)
    value_date = models.DateField(null=True, blank=True)
    value_datetime = models.DateTimeField(null=True, blank=True)
    value_json = models.JSONField(null=True, blank=True)  # For multiselect, lookup

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_custom_field_value'
        unique_together = ['custom_field', 'entity_type', 'entity_id']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
        ]


class SystemConfiguration(models.Model):
    """Global system configuration settings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    key = models.CharField(max_length=200, unique=True)
    value = models.JSONField()

    category = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    # Type information
    value_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('number', 'Number'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
            ('secret', 'Secret'),
        ],
        default='string'
    )

    # Validation
    allowed_values = models.JSONField(null=True, blank=True)  # For enum-like settings

    # Access control
    is_public = models.BooleanField(default=False)  # Whether exposed to frontend
    requires_restart = models.BooleanField(default=False)

    # Audit
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='modified_configurations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_system_configuration'
        ordering = ['category', 'key']


class AuditLog(models.Model):
    """Comprehensive audit log for admin actions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Actor
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_audit_logs'
    )
    user_email = models.EmailField()  # Store email in case user is deleted
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)

    # Action
    action = models.CharField(max_length=100)
    action_category = models.CharField(max_length=50)

    # Target
    target_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=100, blank=True)
    target_description = models.CharField(max_length=500, blank=True)

    # Changes
    changes = models.JSONField(default=dict)  # {field: {old, new}}

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failure', 'Failure'),
            ('partial', 'Partial'),
        ],
        default='success'
    )
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_audit_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_category', 'created_at']),
            models.Index(fields=['target_type', 'target_id']),
        ]


class ScheduledTask(models.Model):
    """Scheduled tasks and jobs configuration."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Task definition
    task_type = models.CharField(max_length=100)  # The celery task or function
    task_args = models.JSONField(default=list)
    task_kwargs = models.JSONField(default=dict)

    # Schedule
    schedule_type = models.CharField(
        max_length=20,
        choices=[
            ('cron', 'Cron Expression'),
            ('interval', 'Interval'),
            ('once', 'One Time'),
        ]
    )
    cron_expression = models.CharField(max_length=100, blank=True)
    interval_seconds = models.PositiveIntegerField(null=True, blank=True)
    run_at = models.DateTimeField(null=True, blank=True)  # For one-time

    # Status
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True)
    last_run_status = models.CharField(max_length=20, blank=True)
    next_run_at = models.DateTimeField(null=True)

    # Execution settings
    timeout_seconds = models.PositiveIntegerField(default=3600)
    max_retries = models.PositiveIntegerField(default=3)
    retry_delay_seconds = models.PositiveIntegerField(default=60)

    # Notifications
    notify_on_failure = models.BooleanField(default=True)
    notify_emails = ArrayField(models.EmailField(), default=list)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_scheduled_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_scheduled_task'


class TaskExecution(models.Model):
    """Tracks scheduled task executions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    task = models.ForeignKey(
        ScheduledTask,
        on_delete=models.CASCADE,
        related_name='executions'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
            ('timeout', 'Timeout'),
        ],
        default='pending'
    )

    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    duration_seconds = models.FloatField(null=True)

    # Results
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)

    # Retry tracking
    attempt_number = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_task_execution'
        ordering = ['-created_at']


class FeatureFlag(models.Model):
    """Feature flags for controlled rollouts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # Status
    is_enabled = models.BooleanField(default=False)

    # Targeting
    target_type = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All Users'),
            ('percentage', 'Percentage'),
            ('users', 'Specific Users'),
            ('roles', 'Specific Roles'),
            ('organizations', 'Specific Organizations'),
        ],
        default='all'
    )

    rollout_percentage = models.PositiveIntegerField(default=100)  # 0-100
    target_user_ids = ArrayField(models.UUIDField(), default=list)
    target_roles = ArrayField(models.CharField(max_length=50), default=list)
    target_org_ids = ArrayField(models.UUIDField(), default=list)

    # Additional conditions
    conditions = models.JSONField(default=dict)  # Custom conditions

    # Metadata
    owner = models.CharField(max_length=100, blank=True)
    jira_ticket = models.CharField(max_length=50, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_feature_flags'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_feature_flag'


class MaintenanceWindow(models.Model):
    """Scheduled maintenance windows."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Impact
    impact_level = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No Impact'),
            ('minimal', 'Minimal'),
            ('partial', 'Partial Outage'),
            ('full', 'Full Outage'),
        ]
    )
    affected_services = ArrayField(models.CharField(max_length=100), default=list)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='scheduled'
    )

    # Notifications
    notify_users = models.BooleanField(default=True)
    notification_message = models.TextField(blank=True)
    notifications_sent_at = models.DateTimeField(null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_maintenance_windows'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_maintenance_window'
        ordering = ['-start_time']
