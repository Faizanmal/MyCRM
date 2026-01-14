"""
Email Tracking Models
Track every email interaction - opens, clicks, replies
This is what HubSpot Sales Hub charges $$$$ for!
"""

import hashlib
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class TrackedEmail(models.Model):
    """Individual tracked emails"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('replied', 'Replied'),
        ('bounced', 'Bounced'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Sender info
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_tracked_emails')
    from_email = models.EmailField()
    from_name = models.CharField(max_length=200, blank=True)

    # Recipient info
    to_email = models.EmailField()
    to_name = models.CharField(max_length=200, blank=True)
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        blank=True,
        related_name='tracked_emails'
    )

    # Related objects
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        blank=True,
        related_name='emails'
    )

    # Email content
    subject = models.CharField(max_length=500)
    body_text = models.TextField(blank=True)
    body_html = models.TextField(blank=True)

    # Template used
    template = models.ForeignKey(
        'EmailTemplate',
        on_delete=models.SET_NULL,
        blank=True
    )

    # Tracking
    tracking_id = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Scheduling
    scheduled_at = models.DateTimeField(blank=True)

    # Timestamps
    sent_at = models.DateTimeField(blank=True)
    delivered_at = models.DateTimeField(blank=True)
    first_opened_at = models.DateTimeField(blank=True)
    last_opened_at = models.DateTimeField(blank=True)
    first_clicked_at = models.DateTimeField(blank=True)
    replied_at = models.DateTimeField(blank=True)

    # Counts
    open_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)

    # Thread tracking
    thread_id = models.CharField(max_length=200, blank=True, db_index=True)
    in_reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        related_name='replies'
    )

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tracked_emails'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['to_email']),
            models.Index(fields=['sent_at']),
        ]

    def __str__(self):
        return f"{self.subject} → {self.to_email}"

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = self._generate_tracking_id()
        super().save(*args, **kwargs)

    def _generate_tracking_id(self):
        """Generate unique tracking ID"""
        data = f"{self.id}{self.to_email}{timezone.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    @property
    def is_opened(self):
        return self.open_count > 0

    @property
    def is_clicked(self):
        return self.click_count > 0

    @property
    def engagement_score(self):
        """Calculate engagement score for this email"""
        score = 0
        if self.status == 'delivered':
            score += 10
        if self.is_opened:
            score += 30
        if self.open_count > 1:
            score += min(self.open_count * 5, 20)  # Multiple opens
        if self.is_clicked:
            score += 40
        if self.status == 'replied':
            score += 50
        return min(score, 100)


class EmailEvent(models.Model):
    """Track individual email events (opens, clicks, etc.)"""

    EVENT_TYPES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('open', 'Opened'),
        ('click', 'Clicked'),
        ('reply', 'Replied'),
        ('bounce', 'Bounced'),
        ('unsubscribe', 'Unsubscribed'),
        ('spam', 'Marked as Spam'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.ForeignKey(TrackedEmail, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)

    # For click events
    clicked_url = models.URLField(blank=True)

    # Client info
    ip_address = models.GenericIPAddressField(blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)  # desktop, mobile, tablet
    email_client = models.CharField(max_length=100, blank=True)  # Gmail, Outlook, etc.

    # Location (from IP)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'email_events'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['email', 'event_type']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.email.subject}"


class EmailTemplate(models.Model):
    """Reusable email templates with tracking"""

    CATEGORY_CHOICES = [
        ('outreach', 'Outreach'),
        ('follow_up', 'Follow Up'),
        ('proposal', 'Proposal'),
        ('meeting', 'Meeting'),
        ('thank_you', 'Thank You'),
        ('nurture', 'Nurture'),
        ('custom', 'Custom'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='custom')

    subject = models.CharField(max_length=500)
    body_text = models.TextField(blank=True)
    body_html = models.TextField()

    # Template variables (e.g., {{first_name}}, {{company}})
    variables = models.JSONField(default=list, help_text="List of template variables")

    # Ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_templates')
    is_shared = models.BooleanField(default=False)

    # Performance metrics
    times_used = models.IntegerField(default=0)
    avg_open_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_click_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_reply_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'email_templates'
        ordering = ['-times_used', 'name']

    def __str__(self):
        return self.name


class EmailSequence(models.Model):
    """Automated email sequences (like HubSpot Sequences)"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracking_email_sequences')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Sequence settings
    send_window_start = models.TimeField(default='09:00')  # Don't send before this time
    send_window_end = models.TimeField(default='18:00')  # Don't send after this time
    send_on_weekends = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default='UTC')

    # Exit conditions
    exit_on_reply = models.BooleanField(default=True)
    exit_on_meeting_booked = models.BooleanField(default=True)
    exit_on_unsubscribe = models.BooleanField(default=True)

    # Performance
    total_enrolled = models.IntegerField(default=0)
    total_completed = models.IntegerField(default=0)
    total_replied = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tracking_email_sequences'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def reply_rate(self):
        if self.total_enrolled == 0:
            return 0
        return round((self.total_replied / self.total_enrolled) * 100, 1)


class SequenceStep(models.Model):
    """Individual steps in an email sequence"""

    STEP_TYPES = [
        ('email', 'Send Email'),
        ('task', 'Create Task'),
        ('wait', 'Wait'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE, related_name='steps')
    order = models.IntegerField()
    step_type = models.CharField(max_length=20, choices=STEP_TYPES, default='email')

    # For email steps
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, blank=True)
    subject_override = models.CharField(max_length=500, blank=True)
    body_override = models.TextField(blank=True)

    # For wait steps
    delay_days = models.IntegerField(default=1)
    delay_hours = models.IntegerField(default=0)

    # For task steps
    task_title = models.CharField(max_length=200, blank=True)
    task_description = models.TextField(blank=True)

    # Performance
    sent_count = models.IntegerField(default=0)
    open_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sequence_steps'
        ordering = ['sequence', 'order']
        unique_together = ['sequence', 'order']

    def __str__(self):
        return f"{self.sequence.name} - Step {self.order}"

    @property
    def open_rate(self):
        if self.sent_count == 0:
            return 0
        return round((self.open_count / self.sent_count) * 100, 1)

    @property
    def reply_rate(self):
        if self.sent_count == 0:
            return 0
        return round((self.reply_count / self.sent_count) * 100, 1)


class SequenceEnrollment(models.Model):
    """Track contacts enrolled in sequences"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('replied', 'Replied'),
        ('unsubscribed', 'Unsubscribed'),
        ('bounced', 'Bounced'),
        ('manually_removed', 'Manually Removed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE, related_name='enrollments')
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.CASCADE,
        related_name='tracking_sequence_enrollments'
    )

    enrolled_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Progress
    current_step = models.IntegerField(default=1)
    next_action_at = models.DateTimeField(blank=True)

    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True)
    exited_at = models.DateTimeField(blank=True)
    exit_reason = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'sequence_enrollments'
        ordering = ['-enrolled_at']
        unique_together = ['sequence', 'contact']

    def __str__(self):
        return f"{self.contact.email} in {self.sequence.name}"


class EmailAnalytics(models.Model):
    """Aggregated email analytics by user/period"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_analytics')
    date = models.DateField()

    # Counts
    emails_sent = models.IntegerField(default=0)
    emails_delivered = models.IntegerField(default=0)
    emails_opened = models.IntegerField(default=0)
    emails_clicked = models.IntegerField(default=0)
    emails_replied = models.IntegerField(default=0)
    emails_bounced = models.IntegerField(default=0)

    # Unique counts
    unique_opens = models.IntegerField(default=0)
    unique_clicks = models.IntegerField(default=0)

    # Rates (pre-calculated for performance)
    open_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    click_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reply_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Best performing
    best_subject = models.CharField(max_length=500, blank=True)
    best_send_time = models.TimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email_analytics'
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"
