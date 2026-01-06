"""
Smart Scheduling Models
Built-in Calendly alternative - saves $$$!
"""

import secrets
import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


class SchedulingPage(models.Model):
    """User's public scheduling page (like Calendly page)"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduling_pages')

    # Page settings
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)  # For URL: /schedule/john-doe
    description = models.TextField(blank=True)

    # Branding
    welcome_message = models.TextField(default="Book a time with me")
    logo = models.URLField(blank=True)
    brand_color = models.CharField(max_length=7, default='#3B82F6')  # Hex color

    # Settings
    is_active = models.BooleanField(default=True)
    require_approval = models.BooleanField(default=False)

    # Timezone
    timezone = models.CharField(max_length=50, default='UTC')

    # Analytics
    page_views = models.IntegerField(default=0)
    bookings_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scheduling_pages'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.owner.username}"

    @property
    def booking_url(self):
        return f"/schedule/{self.slug}"

    @property
    def conversion_rate(self):
        if self.page_views == 0:
            return 0
        return round((self.bookings_count / self.page_views) * 100, 1)


class MeetingType(models.Model):
    """Types of meetings users can book (like Calendly event types)"""

    LOCATION_TYPES = [
        ('video_zoom', 'Zoom'),
        ('video_meet', 'Google Meet'),
        ('video_teams', 'Microsoft Teams'),
        ('phone', 'Phone Call'),
        ('in_person', 'In Person'),
        ('custom', 'Custom Location'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    page = models.ForeignKey(SchedulingPage, on_delete=models.CASCADE, related_name='meeting_types')

    # Basic info
    name = models.CharField(max_length=200)  # e.g., "30 Min Discovery Call"
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    # Duration
    duration_minutes = models.IntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(480)]
    )

    # Location
    location_type = models.CharField(max_length=50, choices=LOCATION_TYPES, default='video_zoom')
    location_details = models.TextField(blank=True)  # Address or custom instructions

    # Scheduling rules
    buffer_before = models.IntegerField(default=0, help_text="Minutes before meeting")
    buffer_after = models.IntegerField(default=0, help_text="Minutes after meeting")
    min_notice_hours = models.IntegerField(default=24, help_text="Minimum hours in advance")
    max_future_days = models.IntegerField(default=60, help_text="Max days in future")

    # Slots per day
    max_per_day = models.IntegerField(null=True, blank=True, help_text="Max bookings per day")

    # Customization
    color = models.CharField(max_length=7, default='#3B82F6')

    # Custom questions for booker
    custom_questions = models.JSONField(default=list, help_text="Questions to ask when booking")

    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)  # Visible on scheduling page

    # Stats
    bookings_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'meeting_types'
        ordering = ['duration_minutes', 'name']
        unique_together = ['page', 'slug']

    def __str__(self):
        return f"{self.name} ({self.duration_minutes} min)"


class Availability(models.Model):
    """User's availability schedule"""

    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    page = models.ForeignKey(SchedulingPage, on_delete=models.CASCADE, related_name='availability')

    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)

    # Time slots (can have multiple per day)
    start_time = models.TimeField()
    end_time = models.TimeField()

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'scheduling_availability'
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.start_time} - {self.end_time}"


class BlockedTime(models.Model):
    """Blocked time slots (vacations, etc.)"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    page = models.ForeignKey(SchedulingPage, on_delete=models.CASCADE, related_name='blocked_times')

    title = models.CharField(max_length=200, blank=True)  # e.g., "Vacation"

    # Can be all-day or specific times
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    all_day = models.BooleanField(default=False)

    # Recurring?
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=200, blank=True)  # RRULE format

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blocked_times'
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.title or 'Blocked'}: {self.start_datetime} - {self.end_datetime}"


class Meeting(models.Model):
    """Booked meetings"""

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    meeting_type = models.ForeignKey(MeetingType, on_delete=models.CASCADE, related_name='bookings')

    # Host
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_meetings')

    # Guest info
    guest_name = models.CharField(max_length=200)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=50, blank=True)
    guest_timezone = models.CharField(max_length=50, default='UTC')

    # Link to CRM contact if exists
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='meetings'
    )

    # Related opportunity
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='meetings'
    )

    # Schedule
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')

    # Location/connection details
    location = models.TextField(blank=True)
    video_link = models.URLField(blank=True)

    # Notes and answers
    notes = models.TextField(blank=True)
    custom_answers = models.JSONField(default=dict)  # Answers to custom questions

    # Tokens for guest actions
    cancel_token = models.CharField(max_length=64, unique=True)
    reschedule_token = models.CharField(max_length=64, unique=True)

    # Reminders
    reminder_sent = models.BooleanField(default=False)
    reminder_24h_sent = models.BooleanField(default=False)
    reminder_1h_sent = models.BooleanField(default=False)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'scheduled_meetings'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['host', 'start_time']),
            models.Index(fields=['guest_email']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.meeting_type.name} with {self.guest_name} - {self.start_time}"

    def save(self, *args, **kwargs):
        if not self.cancel_token:
            self.cancel_token = secrets.token_urlsafe(32)
        if not self.reschedule_token:
            self.reschedule_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    @property
    def duration_minutes(self):
        return (self.end_time - self.start_time).seconds // 60

    @property
    def is_past(self):
        return self.end_time < timezone.now()

    @property
    def is_upcoming(self):
        return self.start_time > timezone.now() and self.status == 'confirmed'


class MeetingReminder(models.Model):
    """Meeting reminder configurations and logs"""

    REMINDER_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('notification', 'Push Notification'),
    ]

    TIMING_CHOICES = [
        (1440, '24 hours before'),
        (60, '1 hour before'),
        (30, '30 minutes before'),
        (15, '15 minutes before'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='reminders')

    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, default='email')
    minutes_before = models.IntegerField(choices=TIMING_CHOICES, default=60)

    # Delivery
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)

    # For guest or host
    for_guest = models.BooleanField(default=True)

    class Meta:
        db_table = 'meeting_reminders'
        ordering = ['scheduled_at']

    def __str__(self):
        return f"Reminder for {self.meeting} - {self.minutes_before}min before"


class CalendarIntegration(models.Model):
    """External calendar integrations"""

    PROVIDER_CHOICES = [
        ('google', 'Google Calendar'),
        ('outlook', 'Outlook Calendar'),
        ('apple', 'Apple Calendar'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendar_integrations')

    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)

    # OAuth tokens (encrypted in production!)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True)

    # Calendar ID
    calendar_id = models.CharField(max_length=200, default='primary')
    calendar_name = models.CharField(max_length=200, blank=True)

    # Settings
    sync_enabled = models.BooleanField(default=True)
    check_conflicts = models.BooleanField(default=True)  # Block time when busy
    create_events = models.BooleanField(default=True)  # Create events for bookings

    # Status
    is_active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendar_integrations'
        unique_together = ['user', 'provider']

    def __str__(self):
        return f"{self.user.username} - {self.get_provider_display()}"


class SchedulingAnalytics(models.Model):
    """Analytics for scheduling pages"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    page = models.ForeignKey(SchedulingPage, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()

    # Views
    page_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)

    # Bookings
    bookings_created = models.IntegerField(default=0)
    bookings_cancelled = models.IntegerField(default=0)
    bookings_rescheduled = models.IntegerField(default=0)
    bookings_completed = models.IntegerField(default=0)
    bookings_no_show = models.IntegerField(default=0)

    # By meeting type
    bookings_by_type = models.JSONField(default=dict)

    # Peak times
    peak_booking_hour = models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scheduling_analytics'
        ordering = ['-date']
        unique_together = ['page', 'date']

    def __str__(self):
        return f"{self.page.name} - {self.date}"
