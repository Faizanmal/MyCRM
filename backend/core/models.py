"""
Enterprise Core Models for MyCRM
Advanced security, audit, and enterprise features
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class AuditLog(models.Model):
    """Comprehensive audit logging for enterprise compliance"""
    
    RISK_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='core_audit_logs')
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=200, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='low')
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'crm_core_audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['risk_level', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} by {self.user or 'Anonymous'} at {self.timestamp}"


class SystemConfiguration(models.Model):
    """System-wide configuration settings"""
    
    CONFIG_TYPES = [
        ('security', 'Security'),
        ('integration', 'Integration'),
        ('business', 'Business Rules'),
        ('ui', 'User Interface'),
        ('notification', 'Notifications'),
    ]
    
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPES)
    description = models.TextField(blank=True)
    is_encrypted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_system_config'
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'
    
    def __str__(self):
        return f"{self.key} ({self.config_type})"


class APIKey(models.Model):
    """API key management for external integrations"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('revoked', 'Revoked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    key_hash = models.CharField(max_length=128, unique=True)  # Hashed API key
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    permissions = models.JSONField(default=list)  # List of allowed permissions
    rate_limit = models.IntegerField(default=1000)  # Requests per hour
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class DataBackup(models.Model):
    """Track data backups for disaster recovery"""
    
    BACKUP_TYPES = [
        ('full', 'Full Backup'),
        ('incremental', 'Incremental'),
        ('differential', 'Differential'),
    ]
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(null=True, blank=True)  # Size in bytes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    error_message = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_data_backups'
        verbose_name = 'Data Backup'
        verbose_name_plural = 'Data Backups'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.backup_type} backup - {self.started_at.strftime('%Y-%m-%d %H:%M')}"


class Workflow(models.Model):
    """Automated workflow definitions"""
    
    TRIGGER_TYPES = [
        ('record_created', 'Record Created'),
        ('record_updated', 'Record Updated'),
        ('field_changed', 'Field Changed'),
        ('time_based', 'Time Based'),
        ('email_received', 'Email Received'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    trigger_conditions = models.JSONField(default=dict)  # Conditions for trigger
    actions = models.JSONField(default=list)  # List of actions to perform
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_workflows'
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'
    
    def __str__(self):
        return self.name


class WorkflowExecution(models.Model):
    """Track workflow execution history"""
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='executions')
    trigger_data = models.JSONField(default=dict)  # Data that triggered the workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    steps_completed = models.IntegerField(default=0)
    total_steps = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    execution_log = models.JSONField(default=list)  # Detailed execution log
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_workflow_executions'
        verbose_name = 'Workflow Execution'
        verbose_name_plural = 'Workflow Executions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.workflow.name} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"


class Integration(models.Model):
    """External system integrations"""
    
    INTEGRATION_TYPES = [
        ('email', 'Email Service'),
        ('calendar', 'Calendar'),
        ('telephony', 'Phone System'),
        ('accounting', 'Accounting Software'),
        ('marketing', 'Marketing Platform'),
        ('social', 'Social Media'),
        ('analytics', 'Analytics Platform'),
        ('storage', 'Cloud Storage'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('configuring', 'Configuring'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    integration_type = models.CharField(max_length=30, choices=INTEGRATION_TYPES)
    provider = models.CharField(max_length=100)  # e.g., 'Gmail', 'Outlook', 'Zoom'
    configuration = models.JSONField(default=dict)  # Integration-specific config
    credentials = models.JSONField(default=dict)  # Encrypted credentials
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='configuring')
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_frequency = models.IntegerField(default=60)  # Minutes between syncs
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_integrations'
        verbose_name = 'Integration'
        verbose_name_plural = 'Integrations'
    
    def __str__(self):
        return f"{self.name} ({self.provider})"


class NotificationTemplate(models.Model):
    """Templates for automated notifications"""
    
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    subject_template = models.CharField(max_length=500, blank=True)  # For email/SMS
    body_template = models.TextField()
    variables = models.JSONField(default=list)  # Available template variables
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_notification_templates'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
    
    def __str__(self):
        return f"{self.name} ({self.notification_type})"


class SystemHealth(models.Model):
    """System health monitoring"""
    
    COMPONENT_TYPES = [
        ('database', 'Database'),
        ('cache', 'Cache'),
        ('email', 'Email Service'),
        ('storage', 'File Storage'),
        ('api', 'External API'),
        ('queue', 'Task Queue'),
    ]
    
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('down', 'Down'),
    ]
    
    component = models.CharField(max_length=50, choices=COMPONENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response_time = models.FloatField(null=True, blank=True)  # Response time in ms
    error_message = models.TextField(null=True, blank=True)
    metrics = models.JSONField(default=dict)  # Additional metrics
    checked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_system_health'
        verbose_name = 'System Health Check'
        verbose_name_plural = 'System Health Checks'
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['component', 'checked_at']),
            models.Index(fields=['status', 'checked_at']),
        ]
    
    def __str__(self):
        return f"{self.component} - {self.status} at {self.checked_at}"


class UserPermission(models.Model):
    """Custom user permissions for granular access control"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_permissions')
    permission = models.CharField(max_length=100)
    is_granted = models.BooleanField(default=True)  # True = grant, False = revoke
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_user_permissions'
        unique_together = ['user', 'permission']
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        action = 'Granted' if self.is_granted else 'Revoked'
        return f"{action} {self.permission} for {self.user.username}"


class PermissionGroup(models.Model):
    """Permission groups for easier permission management"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=list)  # List of permission codes
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_permission_groups'
        verbose_name = 'Permission Group'
        verbose_name_plural = 'Permission Groups'
    
    def __str__(self):
        return self.name


class UserPermissionGroup(models.Model):
    """Many-to-many relationship between users and permission groups"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permission_groups')
    group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE, related_name='user_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='group_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_user_permission_groups'
        unique_together = ['user', 'group']
        verbose_name = 'User Permission Group'
        verbose_name_plural = 'User Permission Groups'
    
    def __str__(self):
        return f"{self.user.username} - {self.group.name}"


class Team(models.Model):
    """Teams for collaborative access control"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_teams')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_teams'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
    
    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """Team membership for row-level permissions"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=50, default='member')  # 'manager', 'member', 'viewer'
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_team_members'
        unique_together = ['team', 'user']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'
    
    def __str__(self):
        return f"{self.user.username} in {self.team.name}"


class DataImportLog(models.Model):
    """Log of data import operations"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('completed_with_errors', 'Completed with Errors'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_name = models.CharField(max_length=100)
    file_format = models.CharField(max_length=10)
    total_records = models.IntegerField(default=0)
    imported_records = models.IntegerField(default=0)
    skipped_records = models.IntegerField(default=0)
    errors = models.JSONField(default=list)
    field_mapping = models.JSONField(default=dict)
    validate_only = models.BooleanField(default=False)
    imported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_data_import_logs'
        verbose_name = 'Data Import Log'
        verbose_name_plural = 'Data Import Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Import {self.model_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Notification(models.Model):
    """In-app notifications"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('task', 'Task Assignment'),
        ('mention', 'Mention'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    link = models.CharField(max_length=500, blank=True)  # Optional link to related resource
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class SavedSearch(models.Model):
    """Save search queries for quick access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    model_name = models.CharField(max_length=100)
    filters = models.JSONField(default=dict)  # Search filters
    sort_by = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    is_shared = models.BooleanField(default=False)  # Share with team
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_saved_searches'
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} - {self.model_name}"


class Dashboard(models.Model):
    """Custom user dashboards"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    layout = models.JSONField(default=dict)  # Dashboard layout configuration
    widgets = models.JSONField(default=list)  # List of widgets
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='core_dashboards')
    is_default = models.BooleanField(default=False)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_core_dashboards'
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Report(models.Model):
    """Saved reports"""
    REPORT_TYPES = [
        ('table', 'Table'),
        ('chart', 'Chart'),
        ('pivot', 'Pivot Table'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='table')
    model_name = models.CharField(max_length=100)
    configuration = models.JSONField(default=dict)  # Report configuration
    filters = models.JSONField(default=dict)
    columns = models.JSONField(default=list)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='core_created_reports')
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_core_reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class ScheduledReport(models.Model):
    """Schedule automatic report generation"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='schedules')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    recipients = models.JSONField(default=list)  # Email addresses
    export_format = models.CharField(max_length=10, default='pdf')
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_scheduled_reports'
        verbose_name = 'Scheduled Report'
        verbose_name_plural = 'Scheduled Reports'
    
    def __str__(self):
        return f"{self.report.name} - {self.frequency}"


class SearchLog(models.Model):
    """Log search queries for analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    model_name = models.CharField(max_length=100)
    query = models.TextField()
    filters = models.JSONField(default=dict)
    result_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_search_logs'
        verbose_name = 'Search Log'
        verbose_name_plural = 'Search Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_name', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.query} on {self.model_name}"


class EmailLog(models.Model):
    """Log sent emails"""
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    to_emails = models.JSONField(default=list)
    cc_emails = models.JSONField(default=list)
    bcc_emails = models.JSONField(default=list)
    subject = models.CharField(max_length=500)
    body = models.TextField()
    html_body = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    error_message = models.TextField(blank=True)
    tracking_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    open_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_email_logs'
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['tracking_id']),
            models.Index(fields=['status', 'sent_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"


class EmailClick(models.Model):
    """Track email link clicks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_log = models.ForeignKey(EmailLog, on_delete=models.CASCADE, related_name='clicks')
    url = models.URLField()
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_email_clicks'
        verbose_name = 'Email Click'
        verbose_name_plural = 'Email Clicks'
    
    def __str__(self):
        return f"{self.url} - {self.clicked_at}"


class EmailCampaign(models.Model):
    """Email marketing campaigns"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True)
    recipients = models.JSONField(default=list)
    recipient_count = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='core_email_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_core_email_campaigns'
        verbose_name = 'Email Campaign'
        verbose_name_plural = 'Email Campaigns'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


# Import settings models to make them available from core.models
from .settings_models import (  # noqa: E402, F401
    UserPreference,
    NotificationPreference,
    NotificationTypeSetting,
    ExportJob,
    UserRole,
    UserRoleAssignment,
)