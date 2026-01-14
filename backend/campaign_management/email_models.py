"""
Email Campaign System
Campaign management, templates, tracking, and automation
"""
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class EmailCampaign(models.Model):
    """Email marketing campaign"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]

    CAMPAIGN_TYPES = [
        ('one_time', 'One-Time'),
        ('drip', 'Drip Campaign'),
        ('trigger', 'Triggered'),
        ('recurring', 'Recurring'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES, default='one_time')

    # Email content
    subject = models.CharField(max_length=500)
    from_email = models.EmailField()
    from_name = models.CharField(max_length=100, blank=True)
    reply_to = models.EmailField(blank=True)

    # Template
    template = models.ForeignKey('EmailTemplate', on_delete=models.SET_NULL, blank=True)
    html_content = models.TextField(help_text="HTML email content")
    text_content = models.TextField(blank=True, help_text="Plain text fallback")

    # Targeting
    target_segment = models.JSONField(default=dict, help_text="Audience segment criteria")
    exclude_segment = models.JSONField(default=dict, blank=True, help_text="Exclusion criteria")

    # Scheduling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(blank=True)
    sent_at = models.DateTimeField(blank=True)

    # Drip campaign settings
    drip_sequence = models.JSONField(default=list, blank=True, help_text="List of drip emails")

    # Tracking
    track_opens = models.BooleanField(default=True)
    track_clicks = models.BooleanField(default=True)

    # Statistics
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    bounced_count = models.IntegerField(default=0)
    unsubscribed_count = models.IntegerField(default=0)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign_email_campaigns'
        verbose_name = 'Email Campaign'
        verbose_name_plural = 'Email Campaigns'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def open_rate(self):
        """Calculate email open rate"""
        return (self.opened_count / self.sent_count * 100) if self.sent_count > 0 else 0

    @property
    def click_rate(self):
        """Calculate click-through rate"""
        return (self.clicked_count / self.sent_count * 100) if self.sent_count > 0 else 0

    @property
    def click_to_open_rate(self):
        """Calculate click-to-open rate"""
        return (self.clicked_count / self.opened_count * 100) if self.opened_count > 0 else 0


class EmailRecipient(models.Model):
    """Individual email recipient tracking"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('bounced', 'Bounced'),
        ('unsubscribed', 'Unsubscribed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='recipients')

    # Recipient info
    email = models.EmailField()
    contact = models.ForeignKey('contact_management.Contact', on_delete=models.SET_NULL, blank=True)
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.SET_NULL, blank=True)

    # Personalization data
    personalization_data = models.JSONField(default=dict)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(blank=True)
    delivered_at = models.DateTimeField(blank=True)
    first_opened_at = models.DateTimeField(blank=True)
    last_opened_at = models.DateTimeField(blank=True)
    first_clicked_at = models.DateTimeField(blank=True)
    last_clicked_at = models.DateTimeField(blank=True)

    # Engagement metrics
    open_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)

    # Error tracking
    error_message = models.TextField(blank=True)
    bounce_reason = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'campaign_email_recipients'
        verbose_name = 'Email Recipient'
        verbose_name_plural = 'Email Recipients'
        indexes = [
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.email} - {self.campaign.name}"


class EmailLink(models.Model):
    """Track links in email campaigns"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='tracked_links')

    original_url = models.URLField()
    tracking_url = models.URLField(unique=True)
    label = models.CharField(max_length=200, blank=True)

    click_count = models.IntegerField(default=0)
    unique_click_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'campaign_email_clicks'
        verbose_name = 'Email Link'
        verbose_name_plural = 'Email Links'

    def __str__(self):
        return f"{self.label or self.original_url} ({self.click_count} clicks)"


class EmailClick(models.Model):
    """Individual link click tracking"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(EmailRecipient, on_delete=models.CASCADE, related_name='clicks')
    link = models.ForeignKey(EmailLink, on_delete=models.CASCADE, related_name='clicks')

    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = 'campaign_email_individual_clicks'
        verbose_name = 'Email Click'
        verbose_name_plural = 'Email Clicks'
        indexes = [
            models.Index(fields=['recipient', 'clicked_at']),
            models.Index(fields=['link', 'clicked_at']),
        ]


class EmailUnsubscribe(models.Model):
    """Email unsubscribe tracking"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    contact = models.ForeignKey('contact_management.Contact', on_delete=models.SET_NULL, blank=True)
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.SET_NULL, blank=True)

    campaign = models.ForeignKey(EmailCampaign, on_delete=models.SET_NULL, blank=True)
    reason = models.TextField(blank=True)

    unsubscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'campaign_email_unsubscribes'
        verbose_name = 'Email Unsubscribe'
        verbose_name_plural = 'Email Unsubscribes'

    def __str__(self):
        return self.email
