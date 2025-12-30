"""
Voice & Conversation Intelligence - Advanced Features
Real-time call coaching, sentiment analysis, and automated meeting summaries
"""

from django.db import models
from django.conf import settings
import uuid


class RealTimeCoachingSession(models.Model):
    """Real-time coaching during live calls"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('ended', 'Ended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.OneToOneField(
        'CallRecording',
        on_delete=models.CASCADE,
        related_name='coaching_session'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Session settings
    coaching_enabled = models.BooleanField(default=True)
    audio_enabled = models.BooleanField(default=False)
    suggestions_enabled = models.BooleanField(default=True)
    
    # Metrics during call
    current_talk_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    question_count = models.IntegerField(default=0)
    objection_count = models.IntegerField(default=0)
    
    # AI analysis
    current_sentiment = models.CharField(max_length=20, default='neutral')
    engagement_level = models.CharField(max_length=20, default='medium')
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'realtime_coaching_sessions'
    
    def __str__(self):
        return f"Coaching for {self.recording.title}"


class RealTimeCoachingSuggestion(models.Model):
    """Suggestions provided during live calls"""
    
    SUGGESTION_TYPES = [
        ('question', 'Ask Question'),
        ('objection', 'Handle Objection'),
        ('technique', 'Technique Tip'),
        ('warning', 'Warning'),
        ('praise', 'Good Practice'),
        ('talking_point', 'Talking Point'),
        ('closing', 'Closing Suggestion'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    session = models.ForeignKey(
        RealTimeCoachingSession,
        on_delete=models.CASCADE,
        related_name='suggestions'
    )
    
    suggestion_type = models.CharField(max_length=30, choices=SUGGESTION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    context = models.TextField(blank=True, help_text="What triggered this suggestion")
    
    # Timing
    timestamp_seconds = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tracking
    was_viewed = models.BooleanField(default=False)
    was_applied = models.BooleanField(default=False)
    
    # Feedback
    was_helpful = models.BooleanField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'realtime_coaching_suggestions'
        ordering = ['timestamp_seconds']
    
    def __str__(self):
        return f"{self.get_suggestion_type_display()}: {self.title}"


class SentimentTimeline(models.Model):
    """Track sentiment over time during a call"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.ForeignKey(
        'CallRecording',
        on_delete=models.CASCADE,
        related_name='sentiment_timeline'
    )
    
    # Time point
    timestamp_seconds = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Sentiment data
    sentiment = models.CharField(max_length=20)  # positive, neutral, negative
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=2)  # -1 to 1
    
    # Detected emotions
    emotions = models.JSONField(default=dict)  # {'happy': 0.8, 'confident': 0.6}
    
    # Speaker
    speaker = models.CharField(max_length=100)
    speaker_type = models.CharField(max_length=20)  # rep, prospect
    
    # Context
    text_snippet = models.TextField(blank=True)
    
    class Meta:
        db_table = 'sentiment_timeline'
        ordering = ['timestamp_seconds']
    
    def __str__(self):
        return f"{self.sentiment} at {self.timestamp_seconds}s"


class SentimentDashboard(models.Model):
    """Aggregated sentiment analytics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sentiment_dashboards'
    )
    
    # Time period
    period = models.CharField(max_length=20)  # daily, weekly, monthly
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Aggregated metrics
    total_calls = models.IntegerField(default=0)
    avg_sentiment_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Sentiment breakdown
    positive_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    neutral_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    negative_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Trends
    sentiment_trend = models.CharField(max_length=20)  # improving, declining, stable
    trend_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Top emotions detected
    top_emotions = models.JSONField(default=list)
    
    # By call type
    sentiment_by_call_type = models.JSONField(default=dict)
    
    # By stage
    sentiment_by_deal_stage = models.JSONField(default=dict)
    
    # Key insights
    insights = models.JSONField(default=list)
    
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sentiment_dashboards'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Sentiment Dashboard {self.period}: {self.start_date}"


class MeetingSummary(models.Model):
    """AI-generated meeting summaries"""
    
    SUMMARY_TYPES = [
        ('full', 'Full Summary'),
        ('executive', 'Executive Summary'),
        ('action_items', 'Action Items Only'),
        ('key_points', 'Key Points'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.OneToOneField(
        'CallRecording',
        on_delete=models.CASCADE,
        related_name='meeting_summary'
    )
    
    # Summary content
    summary_type = models.CharField(max_length=30, choices=SUMMARY_TYPES, default='full')
    
    # Executive summary
    executive_summary = models.TextField()
    
    # Key discussion points
    key_points = models.JSONField(default=list)
    
    # Decisions made
    decisions = models.JSONField(default=list)
    
    # Action items
    action_items = models.JSONField(default=list)
    
    # Follow-up recommendations
    follow_up_recommendations = models.JSONField(default=list)
    
    # Questions raised
    open_questions = models.JSONField(default=list)
    
    # Topics covered
    topics_discussed = models.JSONField(default=list)
    
    # Attendee insights
    attendee_summary = models.JSONField(default=dict)
    
    # Next steps
    next_steps = models.TextField(blank=True)
    suggested_follow_up_date = models.DateField(null=True, blank=True)
    
    # Quality
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Sharing
    is_shared = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='shared_meeting_summaries'
    )
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meeting_summaries'
    
    def __str__(self):
        return f"Summary for {self.recording.title}"


class MeetingActionItem(models.Model):
    """Action items extracted from meetings"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    summary = models.ForeignKey(
        MeetingSummary,
        on_delete=models.CASCADE,
        related_name='extracted_action_items'
    )
    
    # Action details
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='meeting_action_items'
    )
    mentioned_assignee = models.CharField(max_length=200, blank=True)
    
    # Timing
    due_date = models.DateField(null=True, blank=True)
    mentioned_deadline = models.CharField(max_length=200, blank=True)
    
    # Context
    context_quote = models.TextField(blank=True)
    timestamp_seconds = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # Status
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Task integration
    linked_task = models.ForeignKey(
        'task_management.Task',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='from_meeting_action'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'meeting_action_items'
        ordering = ['-priority', 'due_date']
    
    def __str__(self):
        return self.title


class CallCoachingMetrics(models.Model):
    """Aggregated coaching metrics for a user"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coaching_metrics'
    )
    
    # Time period
    period = models.CharField(max_length=20)  # weekly, monthly
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Call metrics
    total_calls = models.IntegerField(default=0)
    total_duration_minutes = models.IntegerField(default=0)
    
    # Talk ratio
    avg_talk_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    talk_ratio_trend = models.CharField(max_length=20, default='stable')
    
    # Questions
    avg_questions_per_call = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    question_quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Objection handling
    objections_handled = models.IntegerField(default=0)
    objection_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Engagement
    avg_engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Call scoring
    avg_call_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    call_score_trend = models.CharField(max_length=20, default='stable')
    
    # Top improvements
    improvement_areas = models.JSONField(default=list)
    
    # Strengths
    strengths = models.JSONField(default=list)
    
    # Coaching recommendations
    recommendations = models.JSONField(default=list)
    
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'call_coaching_metrics'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Coaching Metrics for {self.user.email}: {self.period}"


class KeyMoment(models.Model):
    """Key moments detected during calls"""
    
    MOMENT_TYPES = [
        ('objection', 'Objection Raised'),
        ('buying_signal', 'Buying Signal'),
        ('competitor_mention', 'Competitor Mention'),
        ('pricing_discussion', 'Pricing Discussion'),
        ('decision_maker', 'Decision Maker Reference'),
        ('next_steps', 'Next Steps Discussed'),
        ('pain_point', 'Pain Point Identified'),
        ('value_prop', 'Value Proposition'),
        ('risk_signal', 'Risk Signal'),
        ('positive_feedback', 'Positive Feedback'),
    ]
    
    IMPORTANCE_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.ForeignKey(
        'CallRecording',
        on_delete=models.CASCADE,
        related_name='key_moments'
    )
    
    moment_type = models.CharField(max_length=30, choices=MOMENT_TYPES)
    importance = models.CharField(max_length=20, choices=IMPORTANCE_LEVELS, default='medium')
    
    # Timing
    timestamp_seconds = models.DecimalField(max_digits=10, decimal_places=2)
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Content
    title = models.CharField(max_length=200)
    description = models.TextField()
    quote = models.TextField(blank=True)
    
    # Speaker
    speaker = models.CharField(max_length=100)
    speaker_type = models.CharField(max_length=20)
    
    # Context
    context_before = models.TextField(blank=True)
    context_after = models.TextField(blank=True)
    
    # AI analysis
    sentiment = models.CharField(max_length=20, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Related entities
    related_competitor = models.CharField(max_length=200, blank=True)
    related_product = models.CharField(max_length=200, blank=True)
    
    # Bookmarking
    is_bookmarked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'call_key_moments'
        ordering = ['timestamp_seconds']
    
    def __str__(self):
        return f"{self.get_moment_type_display()} at {self.timestamp_seconds}s"
