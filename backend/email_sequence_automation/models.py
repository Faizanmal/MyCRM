"""
AI-Powered Email Sequence Automation Models
Smart drip campaigns, AI content generation, A/B testing, and automated triggers
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class EmailSequence(models.Model):
    """Email drip campaign sequence"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    TRIGGER_TYPES = [
        ('manual', 'Manual Enrollment'),
        ('lead_score', 'Lead Score Threshold'),
        ('stage_change', 'Deal Stage Change'),
        ('form_submission', 'Form Submission'),
        ('page_visit', 'Website Page Visit'),
        ('inactivity', 'Inactivity Period'),
        ('tag_added', 'Tag Added'),
        ('custom_event', 'Custom Event'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Owner and sharing
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_sequences')
    shared_with_team = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Enrollment triggers
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES, default='manual')
    trigger_config = models.JSONField(default=dict, help_text="Trigger-specific configuration")
    
    # Settings
    settings = models.JSONField(default=dict, help_text="Sequence settings like send window, timezone")
    
    # Exit conditions
    exit_conditions = models.JSONField(default=dict, help_text="Conditions to auto-remove contacts")
    
    # Personalization
    personalization_enabled = models.BooleanField(default=True)
    ai_optimization_enabled = models.BooleanField(default=True)
    
    # Analytics
    total_enrolled = models.IntegerField(default=0)
    total_completed = models.IntegerField(default=0)
    total_converted = models.IntegerField(default=0)
    avg_open_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_click_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_reply_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'email_sequences'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    @property
    def conversion_rate(self):
        if self.total_enrolled == 0:
            return 0
        return round((self.total_converted / self.total_enrolled) * 100, 2)


class SequenceStep(models.Model):
    """Individual step in an email sequence"""
    
    STEP_TYPES = [
        ('email', 'Send Email'),
        ('wait', 'Wait Period'),
        ('condition', 'Conditional Branch'),
        ('task', 'Create Task'),
        ('update_field', 'Update Contact Field'),
        ('add_tag', 'Add Tag'),
        ('remove_tag', 'Remove Tag'),
        ('notify', 'Notify Team Member'),
        ('webhook', 'Call Webhook'),
    ]
    
    CONDITION_TYPES = [
        ('email_opened', 'Email Opened'),
        ('email_clicked', 'Email Clicked'),
        ('email_replied', 'Email Replied'),
        ('lead_score_above', 'Lead Score Above'),
        ('lead_score_below', 'Lead Score Below'),
        ('has_tag', 'Has Tag'),
        ('field_equals', 'Field Equals'),
        ('visited_page', 'Visited Page'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE, related_name='steps')
    
    # Step configuration
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    step_number = models.IntegerField()
    name = models.CharField(max_length=200)
    
    # Wait time configuration
    wait_days = models.IntegerField(default=0)
    wait_hours = models.IntegerField(default=0)
    wait_minutes = models.IntegerField(default=0)
    
    # Conditional logic
    condition_type = models.CharField(max_length=30, choices=CONDITION_TYPES, blank=True)
    condition_config = models.JSONField(default=dict)
    branch_yes_step = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='yes_branches')
    branch_no_step = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='no_branches')
    
    # Step-specific configuration
    config = models.JSONField(default=dict, help_text="Type-specific configuration")
    
    # A/B Testing
    ab_test_enabled = models.BooleanField(default=False)
    
    # Analytics
    total_executed = models.IntegerField(default=0)
    total_completed = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'email_sequence_steps'
        ordering = ['sequence', 'step_number']
        unique_together = ['sequence', 'step_number']
    
    def __str__(self):
        return f"{self.sequence.name} - Step {self.step_number}: {self.name}"
    
    @property
    def wait_total_minutes(self):
        return (self.wait_days * 24 * 60) + (self.wait_hours * 60) + self.wait_minutes


class SequenceEmail(models.Model):
    """Email content for a sequence step with A/B variants"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step = models.ForeignKey(SequenceStep, on_delete=models.CASCADE, related_name='emails')
    
    # Email content
    subject = models.CharField(max_length=500)
    preview_text = models.CharField(max_length=300, blank=True)
    body_html = models.TextField()
    body_text = models.TextField(blank=True)
    
    # AI-generated content
    ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True, help_text="Prompt used to generate this email")
    ai_context = models.JSONField(default=dict, help_text="Context data for AI generation")
    
    # A/B testing variant
    variant_name = models.CharField(max_length=50, default='A')  # A, B, C, etc.
    variant_weight = models.IntegerField(default=100, validators=[MinValueValidator(1), MaxValueValidator(100)])
    is_winner = models.BooleanField(default=False)
    
    # Personalization tokens
    personalization_tokens = models.JSONField(default=list, help_text="Dynamic tokens used in email")
    
    # Analytics
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_opened = models.IntegerField(default=0)
    total_clicked = models.IntegerField(default=0)
    total_replied = models.IntegerField(default=0)
    total_bounced = models.IntegerField(default=0)
    total_unsubscribed = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'email_sequence_emails'
        ordering = ['step', 'variant_name']
    
    def __str__(self):
        return f"{self.step.name} - Variant {self.variant_name}: {self.subject}"
    
    @property
    def open_rate(self):
        if self.total_delivered == 0:
            return 0
        return round((self.total_opened / self.total_delivered) * 100, 2)
    
    @property
    def click_rate(self):
        if self.total_delivered == 0:
            return 0
        return round((self.total_clicked / self.total_delivered) * 100, 2)
    
    @property
    def reply_rate(self):
        if self.total_delivered == 0:
            return 0
        return round((self.total_replied / self.total_delivered) * 100, 2)


class SequenceEnrollment(models.Model):
    """Contact enrollment in a sequence"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('converted', 'Converted'),
        ('unsubscribed', 'Unsubscribed'),
        ('bounced', 'Bounced'),
        ('exited', 'Exited (Condition Met)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE, related_name='enrollments')
    contact = models.ForeignKey('contact_management.Contact', on_delete=models.CASCADE, related_name='sequence_enrollments')
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.CASCADE, null=True, blank=True, related_name='sequence_enrollments')
    
    # Current position
    current_step = models.ForeignKey(SequenceStep, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Scheduling
    next_action_at = models.DateTimeField(null=True, blank=True)
    
    # Enrollment source
    enrolled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sequence_enrollments')
    enrollment_trigger = models.CharField(max_length=100, blank=True)
    
    # Exit tracking
    exit_reason = models.CharField(max_length=200, blank=True)
    exited_at = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    emails_sent = models.IntegerField(default=0)
    emails_opened = models.IntegerField(default=0)
    emails_clicked = models.IntegerField(default=0)
    emails_replied = models.IntegerField(default=0)
    
    # Personalization data snapshot
    personalization_data = models.JSONField(default=dict)
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'email_sequence_enrollments'
        ordering = ['-enrolled_at']
        unique_together = ['sequence', 'contact']
        indexes = [
            models.Index(fields=['sequence', 'status']),
            models.Index(fields=['contact', 'status']),
            models.Index(fields=['next_action_at', 'status']),
        ]
    
    def __str__(self):
        return f"{self.contact} in {self.sequence.name}"


class SequenceActivity(models.Model):
    """Activity log for sequence enrollments"""
    
    ACTIVITY_TYPES = [
        ('enrolled', 'Enrolled'),
        ('step_started', 'Step Started'),
        ('email_sent', 'Email Sent'),
        ('email_opened', 'Email Opened'),
        ('email_clicked', 'Email Clicked'),
        ('email_replied', 'Email Replied'),
        ('email_bounced', 'Email Bounced'),
        ('condition_evaluated', 'Condition Evaluated'),
        ('branched', 'Branched'),
        ('task_created', 'Task Created'),
        ('field_updated', 'Field Updated'),
        ('tag_added', 'Tag Added'),
        ('tag_removed', 'Tag Removed'),
        ('paused', 'Paused'),
        ('resumed', 'Resumed'),
        ('completed', 'Completed'),
        ('exited', 'Exited'),
        ('error', 'Error Occurred'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(SequenceEnrollment, on_delete=models.CASCADE, related_name='activities')
    step = models.ForeignKey(SequenceStep, on_delete=models.SET_NULL, null=True, blank=True)
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    
    # Related data
    metadata = models.JSONField(default=dict)
    
    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_sequence_activities'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['enrollment', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.enrollment.contact} - {self.activity_type}"


class ABTest(models.Model):
    """A/B test configuration and results"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('winner_selected', 'Winner Selected'),
    ]
    
    METRIC_CHOICES = [
        ('open_rate', 'Open Rate'),
        ('click_rate', 'Click Rate'),
        ('reply_rate', 'Reply Rate'),
        ('conversion_rate', 'Conversion Rate'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step = models.OneToOneField(SequenceStep, on_delete=models.CASCADE, related_name='ab_test')
    
    # Test configuration
    name = models.CharField(max_length=200)
    test_metric = models.CharField(max_length=20, choices=METRIC_CHOICES, default='open_rate')
    sample_size = models.IntegerField(default=100, help_text="Number of contacts before determining winner")
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2, default=95.0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Winner
    winning_variant = models.ForeignKey(SequenceEmail, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_tests')
    winner_selected_at = models.DateTimeField(null=True, blank=True)
    auto_select_winner = models.BooleanField(default=True)
    
    # Results
    results = models.JSONField(default=dict, help_text="Statistical test results")
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'email_sequence_ab_tests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"A/B Test: {self.name}"


class AutomatedTrigger(models.Model):
    """Automated triggers for enrolling contacts in sequences"""
    
    TRIGGER_TYPES = [
        ('lead_score', 'Lead Score Threshold'),
        ('stage_change', 'Deal Stage Change'),
        ('inactivity', 'Contact Inactivity'),
        ('form_submission', 'Form Submission'),
        ('page_visit', 'Website Page Visit'),
        ('email_event', 'Email Event'),
        ('tag_change', 'Tag Added/Removed'),
        ('field_change', 'Field Value Change'),
        ('date_based', 'Date-based Trigger'),
        ('api_event', 'API Event'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Trigger configuration
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    trigger_config = models.JSONField(default=dict, help_text="Trigger-specific configuration")
    
    # Target sequence
    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE, related_name='triggers')
    
    # Conditions
    conditions = models.JSONField(default=list, help_text="Additional conditions to evaluate")
    
    # Settings
    is_active = models.BooleanField(default=True)
    prevent_re_enrollment = models.BooleanField(default=True)
    
    # Analytics
    total_triggered = models.IntegerField(default=0)
    total_enrolled = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'email_automated_triggers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trigger_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} -> {self.sequence.name}"


class EmailPersonalizationToken(models.Model):
    """Custom personalization tokens for emails"""
    
    TOKEN_TYPES = [
        ('contact_field', 'Contact Field'),
        ('company_field', 'Company Field'),
        ('deal_field', 'Deal Field'),
        ('dynamic', 'Dynamic Calculation'),
        ('ai_generated', 'AI Generated'),
        ('custom', 'Custom Value'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)  # e.g., {first_name}
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    
    # Configuration
    source_field = models.CharField(max_length=200, blank=True)  # For field-based tokens
    default_value = models.CharField(max_length=500, blank=True)
    formula = models.TextField(blank=True, help_text="Formula for dynamic tokens")
    ai_prompt = models.TextField(blank=True, help_text="Prompt for AI-generated tokens")
    
    # Ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='personalization_tokens')
    is_system = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'email_personalization_tokens'
        ordering = ['name']
        unique_together = ['owner', 'name']
    
    def __str__(self):
        return f"{{{self.name}}}"


class SequenceAnalytics(models.Model):
    """Daily analytics snapshots for sequences"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    
    # Enrollment metrics
    new_enrollments = models.IntegerField(default=0)
    active_enrollments = models.IntegerField(default=0)
    completed_enrollments = models.IntegerField(default=0)
    exited_enrollments = models.IntegerField(default=0)
    
    # Email metrics
    emails_sent = models.IntegerField(default=0)
    emails_delivered = models.IntegerField(default=0)
    emails_opened = models.IntegerField(default=0)
    emails_clicked = models.IntegerField(default=0)
    emails_replied = models.IntegerField(default=0)
    emails_bounced = models.IntegerField(default=0)
    
    # Conversion
    conversions = models.IntegerField(default=0)
    conversion_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Rates
    open_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    click_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reply_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_sequence_analytics'
        ordering = ['-date']
        unique_together = ['sequence', 'date']
        indexes = [
            models.Index(fields=['sequence', '-date']),
        ]
    
    def __str__(self):
        return f"{self.sequence.name} - {self.date}"
