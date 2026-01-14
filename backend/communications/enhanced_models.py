"""
Enhanced Communication Hubs - Unified Inbox and Multi-Channel Management
"""

import uuid

from django.conf import settings
from django.db import models


class UnifiedInboxMessage(models.Model):
    """Unified inbox for all communication channels"""

    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('chat', 'Chat'),
        ('social_linkedin', 'LinkedIn'),
        ('social_twitter', 'Twitter'),
        ('social_facebook', 'Facebook'),
        ('whatsapp', 'WhatsApp'),
        ('call', 'Call'),
        ('voicemail', 'Voicemail'),
    ]

    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
        ('snoozed', 'Snoozed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inbox_messages'
    )

    # Channel
    channel = models.CharField(max_length=30, choices=CHANNEL_TYPES)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)

    # Sender/Recipient
    from_address = models.CharField(max_length=500)
    from_name = models.CharField(max_length=300, blank=True)
    to_address = models.CharField(max_length=500)
    to_name = models.CharField(max_length=300, blank=True)

    # Content
    subject = models.CharField(max_length=500, blank=True)
    preview = models.TextField(help_text="First 200 chars of message")
    body = models.TextField()
    body_html = models.TextField(blank=True)

    # Attachments
    attachments = models.JSONField(default=list)
    attachment_count = models.IntegerField(default=0)

    # Threading
    thread_id = models.CharField(max_length=200, blank=True)
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        related_name='replies'
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')

    # AI Analysis
    sentiment = models.CharField(max_length=20, blank=True)
    ai_summary = models.TextField(blank=True)
    suggested_reply = models.TextField(blank=True)

    # Linked CRM objects
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        blank=True,
        related_name='inbox_messages'
    )
    lead = models.ForeignKey(
        'lead_management.Lead',
        on_delete=models.SET_NULL,
        blank=True,
        related_name='inbox_messages'
    )
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        blank=True,
        related_name='inbox_messages'
    )

    # Labels/Tags
    labels = models.JSONField(default=list)
    is_starred = models.BooleanField(default=False)

    # Snooze
    snoozed_until = models.DateTimeField(blank=True)

    # External references
    external_id = models.CharField(max_length=500, blank=True)
    external_thread_id = models.CharField(max_length=500, blank=True)

    # Timestamps
    received_at = models.DateTimeField()
    read_at = models.DateTimeField(blank=True)
    replied_at = models.DateTimeField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'unified_inbox_messages'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['user', 'status', 'received_at']),
            models.Index(fields=['channel', 'received_at']),
            models.Index(fields=['contact', 'received_at']),
        ]

    def __str__(self):
        return f"{self.channel}: {self.subject or self.preview[:50]}"


class InboxLabel(models.Model):
    """Custom labels for inbox organization"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inbox_labels'
    )

    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='gray')
    icon = models.CharField(max_length=50, blank=True)

    # Smart label rules
    is_smart = models.BooleanField(default=False)
    rules = models.JSONField(default=list)  # Auto-apply rules

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inbox_labels'
        unique_together = ['user', 'name']

    def __str__(self):
        return self.name


class MultiChannelCampaign(models.Model):
    """Coordinated campaigns across multiple channels"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='multi_channel_campaigns'
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Targeting
    target_audience = models.JSONField(default=dict)  # Segment criteria
    target_count = models.IntegerField(default=0)

    # Channels
    channels = models.JSONField(default=list)  # ['email', 'sms', 'linkedin']

    # Schedule
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateTimeField(blank=True)
    end_date = models.DateTimeField(blank=True)

    # Goals
    goals = models.JSONField(default=dict)  # Expected outcomes

    # Budget
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Metrics
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_opens = models.IntegerField(default=0)
    total_clicks = models.IntegerField(default=0)
    total_conversions = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'multi_channel_campaigns'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CampaignStep(models.Model):
    """Individual steps in a multi-channel campaign"""

    STEP_TYPES = [
        ('email', 'Send Email'),
        ('sms', 'Send SMS'),
        ('linkedin_message', 'LinkedIn Message'),
        ('linkedin_connect', 'LinkedIn Connection'),
        ('twitter_dm', 'Twitter DM'),
        ('call_task', 'Call Task'),
        ('delay', 'Wait/Delay'),
        ('condition', 'Condition'),
        ('ab_test', 'A/B Test'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    campaign = models.ForeignKey(
        MultiChannelCampaign,
        on_delete=models.CASCADE,
        related_name='steps'
    )

    step_type = models.CharField(max_length=30, choices=STEP_TYPES)
    name = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    # Step configuration
    config = models.JSONField(default=dict)  # Template, delay duration, conditions

    # Content (for message steps)
    subject = models.CharField(max_length=500, blank=True)
    body = models.TextField(blank=True)
    template_id = models.UUIDField(blank=True)

    # Delay (for delay steps)
    delay_days = models.IntegerField(default=0)
    delay_hours = models.IntegerField(default=0)

    # Conditions (for condition steps)
    conditions = models.JSONField(default=list)

    # Branching
    on_success_step = models.UUIDField(blank=True)
    on_failure_step = models.UUIDField(blank=True)

    # Metrics
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    replied_count = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'campaign_steps'
        ordering = ['order']

    def __str__(self):
        return f"{self.campaign.name} - {self.name}"


class CampaignRecipient(models.Model):
    """Track recipients in a campaign"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('unsubscribed', 'Unsubscribed'),
        ('bounced', 'Bounced'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    campaign = models.ForeignKey(
        MultiChannelCampaign,
        on_delete=models.CASCADE,
        related_name='recipients'
    )

    # Recipient
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.CASCADE,
        blank=True
    )
    lead = models.ForeignKey(
        'lead_management.Lead',
        on_delete=models.CASCADE,
        blank=True
    )
    email = models.EmailField()

    # Progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_step = models.ForeignKey(
        CampaignStep,
        on_delete=models.SET_NULL,
        blank=True
    )

    # Engagement
    opens = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    replies = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)

    # Timing
    entered_at = models.DateTimeField(auto_now_add=True)
    next_step_at = models.DateTimeField(blank=True)
    completed_at = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'campaign_recipients'
        unique_together = ['campaign', 'email']

    def __str__(self):
        return f"{self.campaign.name} - {self.email}"


class AdvancedEmailTracking(models.Model):
    """Advanced email tracking with engagement scoring"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='advanced_email_tracking'
    )

    # Email reference
    tracking_id = models.CharField(max_length=200, unique=True)
    email_id = models.CharField(max_length=200, blank=True)

    # Recipient
    recipient_email = models.EmailField()
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        blank=True
    )

    # Email details
    subject = models.CharField(max_length=500)
    sent_at = models.DateTimeField()

    # Tracking events
    delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(blank=True)

    opened = models.BooleanField(default=False)
    open_count = models.IntegerField(default=0)
    first_opened_at = models.DateTimeField(blank=True)
    last_opened_at = models.DateTimeField(blank=True)

    clicked = models.BooleanField(default=False)
    click_count = models.IntegerField(default=0)
    clicked_urls = models.JSONField(default=list)
    first_clicked_at = models.DateTimeField(blank=True)
    last_clicked_at = models.DateTimeField(blank=True)

    replied = models.BooleanField(default=False)
    replied_at = models.DateTimeField(blank=True)

    bounced = models.BooleanField(default=False)
    bounce_type = models.CharField(max_length=50, blank=True)
    bounced_at = models.DateTimeField(blank=True)

    unsubscribed = models.BooleanField(default=False)
    unsubscribed_at = models.DateTimeField(blank=True)

    complained = models.BooleanField(default=False)
    complained_at = models.DateTimeField(blank=True)

    # Engagement scoring
    engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    time_to_open_seconds = models.IntegerField(blank=True)
    read_duration_seconds = models.IntegerField(blank=True)

    # Predictive
    unsubscribe_risk = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reply_likelihood = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Device/Location
    devices = models.JSONField(default=list)
    locations = models.JSONField(default=list)

    class Meta:
        db_table = 'advanced_email_tracking'
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.subject} to {self.recipient_email}"

    def calculate_engagement_score(self):
        """Calculate engagement score based on interactions"""
        score = 0

        if self.opened:
            score += 20
            # Bonus for quick opens (within 1 hour)
            if self.time_to_open_seconds and self.time_to_open_seconds < 3600:
                score += 10
            # Bonus for multiple opens
            if self.open_count > 1:
                score += min(10, self.open_count * 2)

        if self.clicked:
            score += 30
            # Bonus for multiple clicks
            if self.click_count > 1:
                score += min(15, self.click_count * 3)

        if self.replied:
            score += 40

        self.engagement_score = min(100, score)
        return self.engagement_score


class EmailTrackingEvent(models.Model):
    """Individual tracking events for emails"""

    EVENT_TYPES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('replied', 'Replied'),
        ('bounced', 'Bounced'),
        ('unsubscribed', 'Unsubscribed'),
        ('complained', 'Complained'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tracking = models.ForeignKey(
        AdvancedEmailTracking,
        on_delete=models.CASCADE,
        related_name='events'
    )

    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    # Event details
    url = models.URLField(blank=True)  # For click events

    # Device info
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)

    # Location
    ip_address = models.GenericIPAddressField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email_tracking_events'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} - {self.tracking.subject}"


class CommunicationPreference(models.Model):
    """Track communication preferences per contact"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    contact = models.OneToOneField(
        'contact_management.Contact',
        on_delete=models.CASCADE,
        related_name='communication_preferences'
    )

    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    phone_enabled = models.BooleanField(default=True)
    social_enabled = models.BooleanField(default=True)

    # Email preferences
    email_frequency = models.CharField(max_length=20, default='normal')
    preferred_email_time = models.TimeField(blank=True)

    # Topics/Categories
    opted_in_topics = models.JSONField(default=list)
    opted_out_topics = models.JSONField(default=list)

    # Best contact times
    best_contact_times = models.JSONField(default=list)
    timezone = models.CharField(max_length=50, blank=True)

    # Engagement history
    avg_response_time_hours = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True
    )
    most_engaged_channel = models.CharField(max_length=30, blank=True)

    # Unsubscribe tracking
    global_unsubscribe = models.BooleanField(default=False)
    unsubscribed_at = models.DateTimeField(blank=True)
    unsubscribe_reason = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'communication_preferences'

    def __str__(self):
        return f"Preferences for {self.contact}"
