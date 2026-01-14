"""
Advanced Workflow Engine Models
Visual workflow designer, multi-step approvals, event triggers, conditional logic
"""

import uuid

from django.conf import settings
from django.db import models


class WorkflowDefinition(models.Model):
    """Workflow template/definition"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ]

    TRIGGER_TYPES = [
        ('event', 'Event-Based'),
        ('schedule', 'Scheduled'),
        ('manual', 'Manual'),
        ('api', 'API Triggered'),
        ('record_change', 'Record Change'),
    ]

    CATEGORY_CHOICES = [
        ('sales', 'Sales'),
        ('marketing', 'Marketing'),
        ('support', 'Customer Support'),
        ('onboarding', 'Onboarding'),
        ('approval', 'Approval'),
        ('notification', 'Notification'),
        ('data_management', 'Data Management'),
        ('custom', 'Custom'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workflow_definitions'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='custom')

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Trigger configuration
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    trigger_config = models.JSONField(default=dict)  # Event name, schedule, etc.

    # Entry conditions (when to start workflow)
    entry_conditions = models.JSONField(default=list)  # Conditions to check

    # Visual designer data
    canvas_data = models.JSONField(default=dict)  # Node positions, connections

    # Settings
    allow_multiple = models.BooleanField(default=False)  # Multiple instances per record
    max_concurrent = models.IntegerField(blank=True)
    timeout_hours = models.IntegerField(blank=True)

    # Version control
    version = models.IntegerField(default=1)
    parent_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_versions'
    )

    # Sharing
    is_template = models.BooleanField(default=False)
    shared_with = models.JSONField(default=list)

    # Metrics
    run_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_definitions'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} (v{self.version})"


class WorkflowNode(models.Model):
    """Individual node/step in a workflow"""

    NODE_TYPES = [
        # Actions
        ('action_email', 'Send Email'),
        ('action_sms', 'Send SMS'),
        ('action_notification', 'Send Notification'),
        ('action_task', 'Create Task'),
        ('action_update_record', 'Update Record'),
        ('action_create_record', 'Create Record'),
        ('action_webhook', 'Call Webhook'),
        ('action_slack', 'Send to Slack'),

        # Control flow
        ('condition', 'Condition'),
        ('branch', 'Branch/Split'),
        ('merge', 'Merge'),
        ('delay', 'Delay/Wait'),
        ('schedule', 'Schedule'),

        # Approvals
        ('approval_single', 'Single Approval'),
        ('approval_multi', 'Multi-Person Approval'),
        ('approval_sequential', 'Sequential Approval'),

        # AI
        ('ai_decision', 'AI Decision'),
        ('ai_enrich', 'AI Enrichment'),
        ('ai_score', 'AI Scoring'),

        # Integration
        ('integration_sync', 'Sync to Integration'),
        ('integration_fetch', 'Fetch from Integration'),

        # Subworkflow
        ('subworkflow', 'Run Subworkflow'),

        # End
        ('end_success', 'End - Success'),
        ('end_failure', 'End - Failure'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name='nodes'
    )
    node_id = models.CharField(max_length=100)  # ID used in canvas
    name = models.CharField(max_length=255)
    node_type = models.CharField(max_length=50, choices=NODE_TYPES)

    # Configuration
    config = models.JSONField(default=dict)  # Type-specific configuration

    # Position in canvas
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)

    # Execution settings
    timeout_minutes = models.IntegerField(blank=True)
    retry_count = models.IntegerField(default=0)
    retry_delay_minutes = models.IntegerField(default=5)

    # Error handling
    on_error = models.CharField(
        max_length=20,
        choices=[
            ('stop', 'Stop Workflow'),
            ('continue', 'Continue'),
            ('branch', 'Branch to Error Handler'),
        ],
        default='stop'
    )
    error_branch_node = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_nodes'
        unique_together = ['workflow', 'node_id']

    def __str__(self):
        return f"{self.name} ({self.node_type})"


class WorkflowConnection(models.Model):
    """Connections between workflow nodes"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name='connections'
    )

    source_node = models.CharField(max_length=100)  # node_id
    source_port = models.CharField(max_length=50, default='output')  # output port
    target_node = models.CharField(max_length=100)  # node_id
    target_port = models.CharField(max_length=50, default='input')  # input port

    # For conditional connections
    condition = models.JSONField(default=dict)  # When to use this path
    label = models.CharField(max_length=100, blank=True)  # e.g., "Yes", "No"
    priority = models.IntegerField(default=0)  # For ordering conditions

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workflow_connections'

    def __str__(self):
        return f"{self.source_node} -> {self.target_node}"


class WorkflowInstance(models.Model):
    """Running instance of a workflow"""

    STATUS_CHOICES = [
        ('running', 'Running'),
        ('waiting', 'Waiting'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('timeout', 'Timed Out'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name='instances'
    )

    # Trigger context
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_workflows'
    )
    trigger_event = models.CharField(max_length=100, blank=True)
    trigger_data = models.JSONField(default=dict)

    # Target record
    target_content_type = models.CharField(max_length=100, blank=True)
    target_object_id = models.CharField(max_length=100, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    current_node = models.CharField(max_length=100, blank=True)  # Current node_id

    # Context data
    context = models.JSONField(default=dict)  # Variables, state

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    # Error info
    error_message = models.TextField(blank=True)
    error_node = models.CharField(max_length=100, blank=True)

    # Resume info
    resume_at = models.DateTimeField(blank=True)  # For delays/schedules
    resume_data = models.JSONField(default=dict)

    class Meta:
        db_table = 'workflow_instances'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.workflow.name} - {self.status}"


class WorkflowNodeExecution(models.Model):
    """Execution record for each node"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
        ('waiting', 'Waiting'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='node_executions'
    )
    node = models.ForeignKey(
        WorkflowNode,
        on_delete=models.CASCADE,
        related_name='executions'
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Input/Output
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)

    # Timing
    started_at = models.DateTimeField(blank=True)
    completed_at = models.DateTimeField(blank=True)
    execution_time_ms = models.IntegerField(blank=True)

    # Retry info
    attempt_number = models.IntegerField(default=1)

    # Error info
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict)

    # Approval tracking
    approval_status = models.CharField(max_length=20, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_approvals'
    )
    approval_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workflow_node_executions'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.node.name} - {self.status}"


class WorkflowApprovalRequest(models.Model):
    """Pending approval requests"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('delegated', 'Delegated'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_execution = models.ForeignKey(
        WorkflowNodeExecution,
        on_delete=models.CASCADE,
        related_name='approval_requests'
    )

    # Approver
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pending_approvals'
    )

    # Request details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    data_to_review = models.JSONField(default=dict)

    # Approval options
    approval_options = models.JSONField(default=list)  # Custom buttons
    requires_comment = models.BooleanField(default=False)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    decision = models.CharField(max_length=50, blank=True)  # Selected option
    comment = models.TextField(blank=True)

    # Delegation
    delegated_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delegated_approvals'
    )
    delegated_reason = models.TextField(blank=True)

    # Timing
    due_date = models.DateTimeField(blank=True)
    responded_at = models.DateTimeField(blank=True)

    # Reminders
    reminder_sent_count = models.IntegerField(default=0)
    last_reminder_at = models.DateTimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workflow_approval_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Approval: {self.title} - {self.status}"


class WorkflowTrigger(models.Model):
    """Event triggers for workflows"""

    EVENT_TYPES = [
        # Record events
        ('record_created', 'Record Created'),
        ('record_updated', 'Record Updated'),
        ('record_deleted', 'Record Deleted'),
        ('field_changed', 'Field Changed'),

        # Sales events
        ('deal_stage_changed', 'Deal Stage Changed'),
        ('deal_won', 'Deal Won'),
        ('deal_lost', 'Deal Lost'),

        # Communication events
        ('email_received', 'Email Received'),
        ('email_opened', 'Email Opened'),
        ('email_clicked', 'Email Clicked'),
        ('form_submitted', 'Form Submitted'),

        # Time events
        ('schedule', 'Scheduled Time'),
        ('date_reached', 'Date Field Reached'),
        ('anniversary', 'Anniversary'),

        # Custom
        ('webhook', 'Webhook Received'),
        ('api', 'API Call'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name='triggers'
    )

    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)

    # Target
    entity_type = models.CharField(max_length=100, blank=True)  # e.g., 'opportunity'

    # Conditions
    conditions = models.JSONField(default=list)  # When to fire

    # Schedule (for time-based triggers)
    schedule_expression = models.CharField(max_length=100, blank=True)  # Cron expression
    schedule_timezone = models.CharField(max_length=50, default='UTC')

    # Field watching
    watched_fields = models.JSONField(default=list)  # For field_changed

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_triggers'

    def __str__(self):
        return f"{self.workflow.name} - {self.event_type}"


class WorkflowVariable(models.Model):
    """Custom variables for workflow context"""

    VARIABLE_TYPES = [
        ('string', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'Date/Time'),
        ('list', 'List'),
        ('object', 'Object'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name='variables'
    )

    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255)
    variable_type = models.CharField(max_length=20, choices=VARIABLE_TYPES)

    # Default value
    default_value = models.JSONField(blank=True)

    # Validation
    is_required = models.BooleanField(default=False)
    validation_rules = models.JSONField(default=list)

    # UI hints
    description = models.TextField(blank=True)
    input_type = models.CharField(max_length=50, default='text')  # text, select, etc.
    options = models.JSONField(default=list)  # For select inputs

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workflow_variables'
        unique_together = ['workflow', 'name']

    def __str__(self):
        return f"{self.display_name} ({self.variable_type})"


class WorkflowTemplate(models.Model):
    """Pre-built workflow templates"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50)

    # Template data
    definition_data = models.JSONField(default=dict)  # Complete workflow definition

    # Preview
    preview_image = models.URLField(blank=True)

    # Metadata
    use_count = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.IntegerField(default=0)

    # Source
    is_official = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflow_templates'
        ordering = ['-use_count']

    def __str__(self):
        return self.name


class WorkflowLog(models.Model):
    """Audit log for workflow activities"""

    LOG_TYPES = [
        ('workflow_started', 'Workflow Started'),
        ('workflow_completed', 'Workflow Completed'),
        ('workflow_failed', 'Workflow Failed'),
        ('node_started', 'Node Started'),
        ('node_completed', 'Node Completed'),
        ('node_failed', 'Node Failed'),
        ('approval_requested', 'Approval Requested'),
        ('approval_decision', 'Approval Decision'),
        ('delay_started', 'Delay Started'),
        ('delay_completed', 'Delay Completed'),
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    log_type = models.CharField(max_length=50, choices=LOG_TYPES)
    node_id = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    details = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workflow_logs'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.log_type}: {self.message[:50]}"
