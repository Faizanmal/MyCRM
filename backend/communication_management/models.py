from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Communication(models.Model):
    """Track all communications (emails, calls, meetings)"""
    COMMUNICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('call', 'Call'),
        ('meeting', 'Meeting'),
        ('sms', 'SMS'),
        ('chat', 'Chat'),
        ('letter', 'Letter'),
        ('other', 'Other'),
    ]

    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    # Basic Information
    subject = models.CharField(max_length=200)
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPE_CHOICES)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)

    # Content
    content = models.TextField(blank=True)
    summary = models.TextField(blank=True)

    # Participants
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='sent_communications')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='received_communications')

    # External Information
    from_email = models.EmailField(blank=True)
    to_email = models.EmailField(blank=True)
    from_phone = models.CharField(max_length=20, blank=True)
    to_phone = models.CharField(max_length=20, blank=True)

    # Related Objects
    contact = models.ForeignKey('contact_management.Contact', on_delete=models.CASCADE, blank=True, related_name='communications')
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.CASCADE, blank=True, related_name='communications')
    opportunity = models.ForeignKey('opportunity_management.Opportunity', on_delete=models.CASCADE, blank=True, related_name='communications')
    task = models.ForeignKey('task_management.Task', on_delete=models.CASCADE, blank=True, related_name='communications')

    # Email Specific Fields
    email_id = models.CharField(max_length=255, blank=True)  # External email ID
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True)
    is_replied = models.BooleanField(default=False)
    replied_at = models.DateTimeField(blank=True)

    # Call Specific Fields
    call_duration = models.IntegerField(blank=True)  # Duration in seconds
    call_recording_url = models.URLField(blank=True)

    # Additional Information
    tags = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)

    # Timestamps
    communication_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_communications'
        verbose_name = 'Communication'
        verbose_name_plural = 'Communications'
        ordering = ['-communication_date']

    def __str__(self):
        return f"{self.communication_type.title()} - {self.subject}"


class EmailTemplate(models.Model):
    """Email templates for marketing and communication"""
    TEMPLATE_TYPE_CHOICES = [
        ('marketing', 'Marketing'),
        ('follow_up', 'Follow Up'),
        ('welcome', 'Welcome'),
        ('proposal', 'Proposal'),
        ('invoice', 'Invoice'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES, default='custom')
    content = models.TextField()
    html_content = models.TextField(blank=True)

    # Variables that can be used in the template
    variables = models.JSONField(default=list, blank=True)  # List of available variables

    # Usage tracking
    usage_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Ownership
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communication_email_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_email_templates'
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'

    def __str__(self):
        return self.name


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

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)

    # Scheduling
    scheduled_date = models.DateTimeField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Recipients
    recipient_list = models.JSONField(default=list, blank=True)  # List of contact/lead IDs
    recipient_count = models.IntegerField(default=0)

    # Tracking
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    unsubscribed_count = models.IntegerField(default=0)
    bounced_count = models.IntegerField(default=0)

    # Ownership
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communication_email_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'crm_email_campaigns'
        verbose_name = 'Email Campaign'
        verbose_name_plural = 'Email Campaigns'

    def __str__(self):
        return self.name


class CommunicationRule(models.Model):
    """Automated communication rules"""
    RULE_TYPE_CHOICES = [
        ('auto_email', 'Auto Email'),
        ('follow_up', 'Follow Up'),
        ('reminder', 'Reminder'),
        ('notification', 'Notification'),
    ]

    TRIGGER_CHOICES = [
        ('lead_created', 'Lead Created'),
        ('lead_status_changed', 'Lead Status Changed'),
        ('opportunity_stage_changed', 'Opportunity Stage Changed'),
        ('task_due', 'Task Due'),
        ('no_activity', 'No Activity'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    trigger = models.CharField(max_length=30, choices=TRIGGER_CHOICES)

    # Conditions
    conditions = models.JSONField(default=dict, blank=True)

    # Actions
    actions = models.JSONField(default=list, blank=True)  # List of actions to perform

    # Scheduling
    delay_minutes = models.IntegerField(default=0)  # Delay before executing
    is_active = models.BooleanField(default=True)

    # Ownership
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_communication_rules'
        verbose_name = 'Communication Rule'
        verbose_name_plural = 'Communication Rules'

    def __str__(self):
        return self.name


class CommunicationLog(models.Model):
    """Log of communication rule executions"""
    rule = models.ForeignKey(CommunicationRule, on_delete=models.CASCADE, related_name='execution_logs')
    communication = models.ForeignKey(Communication, on_delete=models.CASCADE, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='success')  # success, failed, skipped
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'crm_communication_logs'
        verbose_name = 'Communication Log'
        verbose_name_plural = 'Communication Logs'
        ordering = ['-executed_at']
