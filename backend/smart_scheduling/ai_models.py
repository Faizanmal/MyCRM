"""
AI-Enhanced Scheduling Models
Extends smart_scheduling with AI-powered features
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class AISchedulingPreference(models.Model):
    """AI-learned scheduling preferences for users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_scheduling_prefs')
    
    # Learned preferences
    preferred_meeting_times = models.JSONField(default=dict, help_text="Hour -> preference score mapping")
    preferred_days = models.JSONField(default=dict, help_text="Day of week -> preference score")
    preferred_meeting_duration = models.IntegerField(default=30)
    max_meetings_per_day = models.IntegerField(default=8)
    max_consecutive_meetings = models.IntegerField(default=3)
    
    # Focus time preferences
    focus_time_start = models.TimeField(null=True, blank=True)
    focus_time_end = models.TimeField(null=True, blank=True)
    focus_days = models.JSONField(default=list, help_text="Days to protect focus time")
    
    # Energy levels by time
    high_energy_hours = models.JSONField(default=list)
    low_energy_hours = models.JSONField(default=list)
    
    # Meeting type preferences
    meeting_type_preferences = models.JSONField(default=dict, help_text="Meeting type -> preferred time/day")
    
    # Context switching
    min_gap_between_meetings = models.IntegerField(default=15)
    prefer_batched_meetings = models.BooleanField(default=False)
    batch_meeting_days = models.JSONField(default=list)
    
    # Learning metrics
    data_points_count = models.IntegerField(default=0)
    last_learning_at = models.DateTimeField(null=True, blank=True)
    preference_confidence = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_scheduling_preferences'
    
    def __str__(self):
        return f"AI Preferences for {self.user.username}"


class AITimeSuggestion(models.Model):
    """AI-generated optimal time suggestions"""
    
    SUGGESTION_TYPE_CHOICES = [
        ('optimal', 'Optimal Time'),
        ('alternative', 'Alternative Time'),
        ('reschedule', 'Reschedule Suggestion'),
        ('batch', 'Batch Meeting'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_time_suggestions')
    meeting_type = models.ForeignKey(
        'smart_scheduling.MeetingType',
        on_delete=models.CASCADE,
        related_name='ai_suggestions'
    )
    
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPE_CHOICES, default='optimal')
    
    # Suggested times
    suggested_start = models.DateTimeField()
    suggested_end = models.DateTimeField()
    
    # Scoring
    overall_score = models.FloatField(default=0.0, help_text="0-100 score")
    preference_score = models.FloatField(default=0.0)
    availability_score = models.FloatField(default=0.0)
    energy_score = models.FloatField(default=0.0)
    context_switch_score = models.FloatField(default=0.0)
    
    # Explanation
    reasoning = models.TextField(blank=True)
    factors = models.JSONField(default=dict)
    
    # Participant context
    participant_email = models.EmailField(blank=True)
    participant_timezone = models.CharField(max_length=50, blank=True)
    mutual_availability = models.JSONField(default=list)
    
    # Status
    was_accepted = models.BooleanField(null=True)
    feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'ai_time_suggestions'
        ordering = ['-overall_score']
    
    def __str__(self):
        return f"AI Suggestion: {self.suggested_start} (Score: {self.overall_score})"


class NoShowPrediction(models.Model):
    """AI predictions for meeting no-shows"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    meeting = models.OneToOneField(
        'smart_scheduling.Meeting',
        on_delete=models.CASCADE,
        related_name='no_show_prediction'
    )
    
    # Prediction
    no_show_probability = models.FloatField(default=0.0, help_text="0-1 probability")
    prediction_confidence = models.FloatField(default=0.0)
    
    # Risk factors
    risk_factors = models.JSONField(default=list)
    risk_score = models.IntegerField(default=0, help_text="0-100 risk score")
    
    # Historical data points used
    guest_meeting_history = models.JSONField(default=dict)
    historical_no_show_rate = models.FloatField(null=True)
    
    # Timing factors
    days_until_meeting = models.IntegerField(null=True)
    meeting_time_of_day = models.CharField(max_length=20, blank=True)
    day_of_week = models.IntegerField(null=True)
    
    # Engagement signals
    email_open_rate = models.FloatField(null=True)
    previous_reschedules = models.IntegerField(default=0)
    confirmation_sent = models.BooleanField(default=False)
    confirmation_opened = models.BooleanField(default=False)
    
    # Recommended actions
    recommended_actions = models.JSONField(default=list)
    extra_reminder_suggested = models.BooleanField(default=False)
    confirmation_call_suggested = models.BooleanField(default=False)
    
    # Outcome tracking
    actual_outcome = models.CharField(max_length=20, blank=True)
    prediction_was_correct = models.BooleanField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'no_show_predictions'
    
    def __str__(self):
        return f"No-Show Risk: {self.risk_score}% for {self.meeting}"


class MeetingPrepAI(models.Model):
    """AI-generated meeting preparation materials"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    meeting = models.OneToOneField(
        'smart_scheduling.Meeting',
        on_delete=models.CASCADE,
        related_name='ai_prep'
    )
    
    # Participant research
    participant_summary = models.TextField(blank=True)
    company_info = models.JSONField(default=dict)
    linkedin_data = models.JSONField(default=dict)
    recent_news = models.JSONField(default=list)
    
    # CRM context
    crm_contact_summary = models.TextField(blank=True)
    previous_interactions = models.JSONField(default=list)
    open_opportunities = models.JSONField(default=list)
    pending_tasks = models.JSONField(default=list)
    
    # Meeting context
    meeting_history_with_contact = models.JSONField(default=list)
    last_meeting_summary = models.TextField(blank=True)
    last_meeting_action_items = models.JSONField(default=list)
    
    # AI-generated content
    suggested_agenda = models.JSONField(default=list)
    talking_points = models.JSONField(default=list)
    questions_to_ask = models.JSONField(default=list)
    potential_objections = models.JSONField(default=list)
    
    # Personalization
    personalization_tips = models.JSONField(default=list)
    ice_breakers = models.JSONField(default=list)
    mutual_connections = models.JSONField(default=list)
    
    # Deal context
    deal_stage = models.CharField(max_length=100, blank=True)
    deal_value = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    win_probability = models.FloatField(null=True)
    recommended_next_steps = models.JSONField(default=list)
    
    # Timing
    prep_generated_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    # User feedback
    was_helpful = models.BooleanField(null=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        db_table = 'meeting_prep_ai'
    
    def __str__(self):
        return f"AI Prep for {self.meeting}"


class SmartReschedule(models.Model):
    """AI-powered automatic rescheduling suggestions"""
    
    TRIGGER_TYPES = [
        ('conflict', 'Calendar Conflict'),
        ('optimization', 'Schedule Optimization'),
        ('no_show_risk', 'High No-Show Risk'),
        ('user_request', 'User Request'),
        ('emergency', 'Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('suggested', 'Suggested to Participants'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    meeting = models.ForeignKey(
        'smart_scheduling.Meeting',
        on_delete=models.CASCADE,
        related_name='reschedule_suggestions'
    )
    
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES)
    trigger_reason = models.TextField(blank=True)
    
    # Original time
    original_start = models.DateTimeField()
    original_end = models.DateTimeField()
    
    # Suggested alternatives
    alternatives = models.JSONField(default=list, help_text="List of alternative time slots")
    
    # Best suggestion
    suggested_start = models.DateTimeField(null=True)
    suggested_end = models.DateTimeField(null=True)
    suggestion_score = models.FloatField(default=0.0)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Communication
    notification_sent = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True)
    host_notified = models.BooleanField(default=False)
    guest_notified = models.BooleanField(default=False)
    
    # Response
    response_by = models.CharField(max_length=20, blank=True)  # 'host' or 'guest'
    selected_alternative = models.JSONField(null=True)
    response_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'smart_reschedule'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reschedule for {self.meeting} - {self.status}"


class SmartReminder(models.Model):
    """AI-optimized smart reminders based on behavior"""
    
    REMINDER_CHANNEL = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('slack', 'Slack'),
        ('teams', 'MS Teams'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    meeting = models.ForeignKey(
        'smart_scheduling.Meeting',
        on_delete=models.CASCADE,
        related_name='smart_reminders'
    )
    
    # Timing (AI-optimized)
    scheduled_at = models.DateTimeField()
    minutes_before = models.IntegerField()
    
    # AI optimization
    is_ai_optimized = models.BooleanField(default=False)
    optimization_reason = models.TextField(blank=True)
    optimal_channel = models.CharField(max_length=20, choices=REMINDER_CHANNEL, default='email')
    
    # Channel engagement history
    channel_preference_score = models.JSONField(default=dict)
    
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    include_prep_material = models.BooleanField(default=False)
    include_agenda = models.BooleanField(default=False)
    
    # Delivery
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True)
    delivery_status = models.CharField(max_length=50, blank=True)
    
    # Engagement
    opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True)
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True)
    
    # For guest or host
    recipient_type = models.CharField(max_length=20, default='guest')  # 'host' or 'guest'
    recipient_email = models.EmailField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'smart_reminders'
        ordering = ['scheduled_at']
    
    def __str__(self):
        return f"Smart Reminder for {self.meeting} at {self.scheduled_at}"


class ScheduleOptimization(models.Model):
    """AI-driven schedule optimization suggestions"""
    
    OPTIMIZATION_TYPE = [
        ('batch_meetings', 'Batch Similar Meetings'),
        ('create_focus_time', 'Create Focus Time'),
        ('reduce_context_switch', 'Reduce Context Switching'),
        ('energy_alignment', 'Align with Energy Levels'),
        ('travel_optimization', 'Optimize for Travel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_optimizations')
    
    optimization_type = models.CharField(max_length=30, choices=OPTIMIZATION_TYPE)
    
    # Analysis period
    analysis_start = models.DateField()
    analysis_end = models.DateField()
    
    # Current state
    current_schedule = models.JSONField(default=list)
    current_metrics = models.JSONField(default=dict)
    
    # Suggested state
    optimized_schedule = models.JSONField(default=list)
    optimized_metrics = models.JSONField(default=dict)
    
    # Impact analysis
    meetings_affected = models.IntegerField(default=0)
    time_saved_minutes = models.IntegerField(default=0)
    focus_time_gained_minutes = models.IntegerField(default=0)
    context_switches_reduced = models.IntegerField(default=0)
    
    # Score improvement
    current_score = models.FloatField(default=0.0)
    optimized_score = models.FloatField(default=0.0)
    improvement_percentage = models.FloatField(default=0.0)
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    explanation = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, default='pending')
    applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'schedule_optimizations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.optimization_type} for {self.user.username}"


class AttendeeIntelligence(models.Model):
    """AI intelligence about meeting attendees"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    
    # Scheduling patterns
    preferred_meeting_times = models.JSONField(default=list)
    response_time_average = models.DurationField(null=True)
    typical_response_days = models.JSONField(default=list)
    
    # Reliability metrics
    total_meetings_scheduled = models.IntegerField(default=0)
    meetings_attended = models.IntegerField(default=0)
    meetings_no_show = models.IntegerField(default=0)
    meetings_cancelled = models.IntegerField(default=0)
    meetings_rescheduled = models.IntegerField(default=0)
    
    # Engagement patterns
    average_meeting_duration = models.IntegerField(null=True)
    prefers_video = models.BooleanField(null=True)
    prefers_phone = models.BooleanField(null=True)
    
    # Timezone intelligence
    detected_timezone = models.CharField(max_length=50, blank=True)
    timezone_confidence = models.FloatField(default=0.0)
    
    # Communication preferences
    reminder_response_rate = models.FloatField(null=True)
    best_reminder_timing = models.IntegerField(null=True, help_text="Minutes before")
    best_communication_channel = models.CharField(max_length=20, blank=True)
    
    # Scores
    reliability_score = models.FloatField(default=0.5)
    engagement_score = models.FloatField(default=0.5)
    
    # Last activity
    last_meeting_at = models.DateTimeField(null=True)
    last_interaction_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendee_intelligence'
    
    def __str__(self):
        return f"Intelligence for {self.email}"
    
    @property
    def no_show_rate(self):
        if self.total_meetings_scheduled == 0:
            return 0
        return self.meetings_no_show / self.total_meetings_scheduled
    
    @property
    def attendance_rate(self):
        if self.total_meetings_scheduled == 0:
            return 0
        return self.meetings_attended / self.total_meetings_scheduled
