"""
Conversation Intelligence Models
Gong/Chorus alternative - Record, transcribe, and analyze sales calls
"""

import uuid

from django.conf import settings
from django.db import models


class CallRecording(models.Model):
    """Recorded sales calls"""

    CALL_TYPES = [
        ('discovery', 'Discovery Call'),
        ('demo', 'Demo/Presentation'),
        ('negotiation', 'Negotiation'),
        ('closing', 'Closing Call'),
        ('follow_up', 'Follow-up'),
        ('support', 'Support Call'),
        ('internal', 'Internal Meeting'),
    ]

    PLATFORMS = [
        ('zoom', 'Zoom'),
        ('teams', 'Microsoft Teams'),
        ('meet', 'Google Meet'),
        ('phone', 'Phone Call'),
        ('webex', 'Webex'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('transcribing', 'Transcribing'),
        ('analyzing', 'Analyzing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=300)
    call_type = models.CharField(max_length=20, choices=CALL_TYPES, default='discovery')
    platform = models.CharField(max_length=20, choices=PLATFORMS, default='zoom')

    # Linked CRM objects
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='call_recordings'
    )
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='call_recordings'
    )

    # Recording data
    recording_file = models.FileField(upload_to='calls/recordings/')
    recording_url = models.URLField(blank=True)  # External URL if hosted elsewhere
    duration_seconds = models.IntegerField(default=0)

    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    processing_error = models.TextField(blank=True)

    # Metadata
    recorded_at = models.DateTimeField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='call_recordings'
    )

    # Sharing
    is_shared = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='shared_recordings'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return self.title

    @property
    def duration_formatted(self):
        minutes, seconds = divmod(self.duration_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


class CallTranscript(models.Model):
    """Full transcript of a call"""

    recording = models.OneToOneField(
        CallRecording,
        on_delete=models.CASCADE,
        related_name='transcript'
    )

    full_text = models.TextField()
    word_count = models.IntegerField(default=0)

    # Language detection
    detected_language = models.CharField(max_length=10, default='en')
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transcript for {self.recording.title}"


class TranscriptSegment(models.Model):
    """Individual segments of a transcript with speaker diarization"""

    transcript = models.ForeignKey(
        CallTranscript,
        on_delete=models.CASCADE,
        related_name='segments'
    )

    speaker = models.CharField(max_length=100)  # Speaker name/label
    speaker_type = models.CharField(
        max_length=20,
        choices=[('rep', 'Sales Rep'), ('prospect', 'Prospect'), ('unknown', 'Unknown')],
        default='unknown'
    )

    text = models.TextField()
    start_time = models.DecimalField(max_digits=10, decimal_places=2)  # seconds
    end_time = models.DecimalField(max_digits=10, decimal_places=2)

    # Sentiment for this segment
    sentiment = models.CharField(
        max_length=10,
        choices=[('positive', 'Positive'), ('neutral', 'Neutral'), ('negative', 'Negative')],
        default='neutral'
    )
    sentiment_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.speaker}: {self.text[:50]}..."


class CallAnalysis(models.Model):
    """AI analysis of a call"""

    recording = models.OneToOneField(
        CallRecording,
        on_delete=models.CASCADE,
        related_name='analysis'
    )

    # Talk metrics
    rep_talk_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    prospect_talk_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    longest_rep_monologue = models.IntegerField(default=0)  # seconds
    longest_prospect_monologue = models.IntegerField(default=0)
    question_count = models.IntegerField(default=0)

    # Engagement metrics
    engagement_score = models.IntegerField(default=0)  # 0-100
    energy_level = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )

    # Sentiment
    overall_sentiment = models.CharField(
        max_length=10,
        choices=[('positive', 'Positive'), ('neutral', 'Neutral'), ('negative', 'Negative')],
        default='neutral'
    )
    sentiment_trend = models.CharField(
        max_length=20,
        choices=[('improving', 'Improving'), ('stable', 'Stable'), ('declining', 'Declining')],
        default='stable'
    )

    # AI Summary
    summary = models.TextField(blank=True)
    key_points = models.JSONField(default=list)
    action_items = models.JSONField(default=list)

    # Deal signals
    buying_signals = models.JSONField(default=list)
    objections_raised = models.JSONField(default=list)
    competitor_mentions = models.JSONField(default=list)

    # Next steps
    next_steps_discussed = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)

    # Scoring
    call_score = models.IntegerField(default=0)  # 0-100
    areas_for_improvement = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis for {self.recording.title}"


class TopicMention(models.Model):
    """Track specific topics mentioned in calls"""

    TOPIC_TYPES = [
        ('product', 'Product/Feature'),
        ('pricing', 'Pricing'),
        ('competitor', 'Competitor'),
        ('objection', 'Objection'),
        ('pain_point', 'Pain Point'),
        ('next_step', 'Next Step'),
        ('decision_maker', 'Decision Maker'),
        ('timeline', 'Timeline'),
        ('budget', 'Budget'),
        ('custom', 'Custom Topic'),
    ]

    recording = models.ForeignKey(
        CallRecording,
        on_delete=models.CASCADE,
        related_name='topic_mentions'
    )

    topic_type = models.CharField(max_length=20, choices=TOPIC_TYPES)
    topic_name = models.CharField(max_length=200)
    context = models.TextField()  # Surrounding text
    timestamp = models.DecimalField(max_digits=10, decimal_places=2)  # seconds

    sentiment = models.CharField(
        max_length=10,
        choices=[('positive', 'Positive'), ('neutral', 'Neutral'), ('negative', 'Negative')],
        default='neutral'
    )

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.topic_name} at {self.timestamp}s"


class CallCoaching(models.Model):
    """Coaching notes and feedback on calls"""

    recording = models.ForeignKey(
        CallRecording,
        on_delete=models.CASCADE,
        related_name='coaching_notes'
    )
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coaching_given'
    )

    # Timestamped feedback
    timestamp = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    feedback = models.TextField()
    feedback_type = models.CharField(
        max_length=20,
        choices=[
            ('praise', 'Praise'),
            ('suggestion', 'Suggestion'),
            ('correction', 'Correction'),
            ('question', 'Question'),
        ],
        default='suggestion'
    )

    # If feedback is AI-generated
    is_ai_generated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp', 'created_at']

    def __str__(self):
        return f"Coaching on {self.recording.title}"


class CallPlaylist(models.Model):
    """Curated playlists of call clips for training"""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='call_playlists'
    )

    is_public = models.BooleanField(default=False)

    # Categories
    category = models.CharField(
        max_length=30,
        choices=[
            ('best_practices', 'Best Practices'),
            ('objection_handling', 'Objection Handling'),
            ('discovery', 'Discovery Techniques'),
            ('closing', 'Closing Techniques'),
            ('product_demo', 'Product Demo'),
            ('onboarding', 'New Rep Onboarding'),
            ('custom', 'Custom'),
        ],
        default='custom'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PlaylistClip(models.Model):
    """Clips added to playlists"""

    playlist = models.ForeignKey(
        CallPlaylist,
        on_delete=models.CASCADE,
        related_name='clips'
    )
    recording = models.ForeignKey(
        CallRecording,
        on_delete=models.CASCADE,
        related_name='playlist_clips'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DecimalField(max_digits=10, decimal_places=2)
    end_time = models.DecimalField(max_digits=10, decimal_places=2)

    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['playlist', 'order']

    def __str__(self):
        return f"{self.title} ({self.playlist.name})"


class CallTracker(models.Model):
    """Track keywords/phrases across all calls"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    keywords = models.JSONField(default=list)  # List of keywords/phrases to track

    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='call_trackers'
    )
    is_shared = models.BooleanField(default=True)

    # Stats
    total_mentions = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_mentions']

    def __str__(self):
        return self.name


class ConversationAnalytics(models.Model):
    """Aggregated analytics for conversation intelligence"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversation_analytics'
    )
    date = models.DateField()

    # Volume
    calls_recorded = models.IntegerField(default=0)
    total_duration_minutes = models.IntegerField(default=0)

    # Performance
    avg_talk_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_question_count = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_call_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Outcomes
    positive_sentiment_calls = models.IntegerField(default=0)
    calls_with_action_items = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date}"
