"""
Meeting Follow-up Models
Models for automated follow-up sequences after meetings
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class MeetingFollowUp(models.Model):
    """Follow-up actions and sequences after meetings"""

    FOLLOW_UP_TYPES = [
        ('thank_you', 'Thank You Email'),
        ('summary', 'Meeting Summary'),
        ('action_items', 'Action Items Reminder'),
        ('proposal', 'Send Proposal'),
        ('check_in', 'Check-In'),
        ('reschedule', 'Reschedule Request'),
        ('feedback', 'Feedback Request'),
        ('custom', 'Custom Follow-up'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('replied', 'Replied'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    meeting = models.ForeignKey(
        'smart_scheduling.Meeting',
        on_delete=models.CASCADE,
        related_name='follow_ups'
    )

    follow_up_type = models.CharField(max_length=20, choices=FOLLOW_UP_TYPES)

    # Scheduling
    scheduled_at = models.DateTimeField()
    delay_hours = models.IntegerField(default=1, help_text="Hours after meeting ends")

    # Content
    subject = models.CharField(max_length=300)
    body = models.TextField()
    is_ai_generated = models.BooleanField(default=False)

    # Personalization
    personalization_context = models.JSONField(default=dict)
    attachments = models.JSONField(default=list)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(blank=True)
    opened_at = models.DateTimeField(blank=True)
    clicked_at = models.DateTimeField(blank=True)
    replied_at = models.DateTimeField(blank=True)

    # Error tracking
    last_error = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'meeting_follow_ups'
        ordering = ['scheduled_at']

    def __str__(self):
        return f"{self.follow_up_type} for {self.meeting}"


class FollowUpSequence(models.Model):
    """Predefined follow-up sequences"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_up_sequences')

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Apply to specific meeting types
    meeting_types = models.ManyToManyField(
        'smart_scheduling.MeetingType',
        blank=True,
        related_name='follow_up_sequences'
    )
    apply_to_all = models.BooleanField(default=False)

    # Sequence steps as JSON
    steps = models.JSONField(default=list, help_text="""
        [
            {"delay_hours": 1, "type": "thank_you", "subject_template": "...", "body_template": "..."},
            {"delay_hours": 24, "type": "summary", "include_action_items": true},
            {"delay_days": 7, "type": "check_in", "condition": "no_reply"}
        ]
    """)

    # Settings
    is_active = models.BooleanField(default=True)
    use_ai_personalization = models.BooleanField(default=True)

    # Stats
    times_used = models.IntegerField(default=0)
    avg_reply_rate = models.FloatField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'follow_up_sequences'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({len(self.steps)} steps)"


class MeetingOutcome(models.Model):
    """Recorded outcomes and notes from meetings"""

    OUTCOME_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    meeting = models.OneToOneField(
        'smart_scheduling.Meeting',
        on_delete=models.CASCADE,
        related_name='outcome'
    )

    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    notes = models.TextField(blank=True)

    # Action items
    action_items = models.JSONField(default=list, help_text="""
        [{"task": "Send proposal", "assignee": "self", "due_date": "2024-01-15"}]
    """)

    # Next steps
    next_meeting_scheduled = models.BooleanField(default=False)
    next_meeting_date = models.DateTimeField(blank=True)

    # AI-generated summary
    ai_summary = models.TextField(blank=True)
    key_points = models.JSONField(default=list)
    sentiment_score = models.FloatField(blank=True, help_text="-1 to 1")

    # Deal progression
    deal_progressed = models.BooleanField(null=True)
    new_deal_stage = models.CharField(max_length=100, blank=True)

    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'meeting_outcomes'

    def __str__(self):
        return f"Outcome: {self.outcome} for {self.meeting}"


class RecurringMeetingPattern(models.Model):
    """Patterns for recurring meetings"""

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_patterns')
    meeting_type = models.ForeignKey(
        'smart_scheduling.MeetingType',
        on_delete=models.CASCADE,
        related_name='recurring_patterns'
    )

    name = models.CharField(max_length=200)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)

    # Schedule
    day_of_week = models.IntegerField(blank=True, help_text="0=Monday, 6=Sunday")
    day_of_month = models.IntegerField(blank=True)
    preferred_time = models.TimeField()

    # Contact (optional - for recurring 1:1s)
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        blank=True,
        related_name='recurring_meetings'
    )

    # Status
    is_active = models.BooleanField(default=True)
    next_occurrence = models.DateTimeField(null=True)

    # Auto-scheduling
    auto_schedule = models.BooleanField(default=False)
    auto_schedule_days_ahead = models.IntegerField(default=7)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recurring_meeting_patterns'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.frequency})"


class MeetingAnalytics(models.Model):
    """Aggregated meeting analytics"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_analytics')

    # Period
    period_type = models.CharField(max_length=20)  # 'daily', 'weekly', 'monthly'
    period_start = models.DateField()
    period_end = models.DateField()

    # Meeting counts
    total_meetings = models.IntegerField(default=0)
    completed_meetings = models.IntegerField(default=0)
    cancelled_meetings = models.IntegerField(default=0)
    no_show_meetings = models.IntegerField(default=0)
    rescheduled_meetings = models.IntegerField(default=0)

    # Time metrics
    total_meeting_minutes = models.IntegerField(default=0)
    avg_meeting_duration = models.IntegerField(default=0)

    # Distribution
    meetings_by_type = models.JSONField(default=dict)
    meetings_by_day = models.JSONField(default=dict)
    meetings_by_hour = models.JSONField(default=dict)

    # Outcomes
    positive_outcomes = models.IntegerField(default=0)
    neutral_outcomes = models.IntegerField(default=0)
    negative_outcomes = models.IntegerField(default=0)

    # Follow-up metrics
    follow_ups_sent = models.IntegerField(default=0)
    follow_ups_opened = models.IntegerField(default=0)
    follow_ups_replied = models.IntegerField(default=0)

    # Conversion
    meetings_to_opportunities = models.IntegerField(default=0)
    conversion_rate = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'meeting_analytics_summary'
        ordering = ['-period_start']
        unique_together = ['user', 'period_type', 'period_start']

    def __str__(self):
        return f"Analytics for {self.user.username}: {self.period_start}"


class CalendarEvent(models.Model):
    """External calendar events synced from integrations"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    integration = models.ForeignKey(
        'smart_scheduling.CalendarIntegration',
        on_delete=models.CASCADE,
        related_name='synced_events'
    )

    # External ID
    external_id = models.CharField(max_length=500)
    external_link = models.URLField(blank=True)

    # Event details
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=500, blank=True)

    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default='UTC')

    # Status
    status = models.CharField(max_length=50, default='confirmed')
    is_busy = models.BooleanField(default=True)

    # Attendees
    organizer_email = models.EmailField(blank=True)
    attendees = models.JSONField(default=list)

    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurrence_id = models.CharField(max_length=500, blank=True)

    # Sync tracking
    last_synced_at = models.DateTimeField(auto_now=True)
    etag = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'calendar_events_synced'
        ordering = ['start_time']
        unique_together = ['integration', 'external_id']

    def __str__(self):
        return f"{self.title} ({self.start_time})"
