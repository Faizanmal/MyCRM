"""
Voice Intelligence Models
Models for voice recording, transcription, and AI analysis
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class VoiceRecording(models.Model):
    """Voice/audio recording from calls or meetings"""
    
    SOURCE_TYPES = [
        ('phone_call', 'Phone Call'),
        ('video_meeting', 'Video Meeting'),
        ('voice_note', 'Voice Note'),
        ('upload', 'Uploaded Recording'),
        ('live_capture', 'Live Capture'),
    ]
    
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('transcribing', 'Transcribing'),
        ('transcribed', 'Transcribed'),
        ('analyzing', 'Analyzing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recording metadata
    title = models.CharField(max_length=300, blank=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default='phone_call')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    
    # File info
    file_url = models.URLField(blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    file_format = models.CharField(max_length=20, blank=True)  # mp3, wav, m4a, etc.
    
    # Duration
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Audio quality
    sample_rate = models.IntegerField(null=True, blank=True)
    channels = models.IntegerField(default=1)
    bitrate = models.IntegerField(null=True, blank=True)
    
    # Participants
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='voice_recordings'
    )
    participants = models.JSONField(default=list, help_text="List of participants")
    participant_count = models.IntegerField(default=2)
    
    # Related records
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='voice_recordings'
    )
    lead = models.ForeignKey(
        'lead_management.Lead',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='voice_recordings'
    )
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='voice_recordings'
    )
    meeting = models.ForeignKey(
        'smart_scheduling.Meeting',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='voice_recordings'
    )
    
    # Recording timing
    recorded_at = models.DateTimeField(default=timezone.now)
    
    # Processing info
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True)
    
    # Language
    detected_language = models.CharField(max_length=10, default='en')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'voice_recordings'
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.title or 'Recording'} - {self.recorded_at}"
    
    @property
    def duration_formatted(self):
        if not self.duration_seconds:
            return "0:00"
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"


class Transcription(models.Model):
    """Transcription of a voice recording"""
    
    TRANSCRIPTION_PROVIDERS = [
        ('whisper', 'OpenAI Whisper'),
        ('google', 'Google Speech-to-Text'),
        ('aws', 'AWS Transcribe'),
        ('azure', 'Azure Speech'),
        ('deepgram', 'Deepgram'),
        ('assembly', 'AssemblyAI'),
        ('internal', 'Internal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.OneToOneField(
        VoiceRecording,
        on_delete=models.CASCADE,
        related_name='transcription'
    )
    
    # Transcription content
    full_text = models.TextField(blank=True)
    
    # Word-level timing (for playback sync)
    words_with_timing = models.JSONField(default=list, help_text="Words with start/end timestamps")
    
    # Speaker diarization
    has_speaker_labels = models.BooleanField(default=False)
    speaker_segments = models.JSONField(default=list, help_text="Segments by speaker")
    speaker_count = models.IntegerField(null=True, blank=True)
    
    # Speaker identification
    speaker_mapping = models.JSONField(default=dict, help_text="Speaker ID to name mapping")
    
    # Quality metrics
    confidence_score = models.FloatField(null=True, blank=True)
    word_error_rate = models.FloatField(null=True, blank=True)
    
    # Provider info
    provider = models.CharField(max_length=20, choices=TRANSCRIPTION_PROVIDERS, default='whisper')
    provider_job_id = models.CharField(max_length=200, blank=True)
    
    # Language
    detected_language = models.CharField(max_length=10, default='en')
    
    # Processing time
    processing_time_seconds = models.FloatField(null=True, blank=True)
    
    # Edits
    was_edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='edited_transcriptions'
    )
    edited_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transcriptions'
    
    def __str__(self):
        return f"Transcription for {self.recording}"
    
    @property
    def word_count(self):
        return len(self.full_text.split()) if self.full_text else 0


class ConversationSummary(models.Model):
    """AI-generated summary of a conversation"""
    
    SUMMARY_TYPES = [
        ('executive', 'Executive Summary'),
        ('detailed', 'Detailed Summary'),
        ('bullet_points', 'Bullet Points'),
        ('action_items', 'Action Items Only'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.ForeignKey(
        VoiceRecording,
        on_delete=models.CASCADE,
        related_name='summaries'
    )
    
    summary_type = models.CharField(max_length=20, choices=SUMMARY_TYPES, default='executive')
    
    # Summary content
    summary_text = models.TextField(blank=True)
    key_points = models.JSONField(default=list)
    
    # Topics discussed
    topics = models.JSONField(default=list)
    topic_segments = models.JSONField(default=list, help_text="Topics with time ranges")
    
    # Decisions made
    decisions = models.JSONField(default=list)
    
    # Questions raised
    questions_asked = models.JSONField(default=list)
    questions_unanswered = models.JSONField(default=list)
    
    # Next steps mentioned
    next_steps = models.JSONField(default=list)
    
    # Keywords and entities
    keywords = models.JSONField(default=list)
    entities_mentioned = models.JSONField(default=dict, help_text="People, companies, products mentioned")
    
    # AI metadata
    model_used = models.CharField(max_length=100, blank=True)
    generation_prompt = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation_summaries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_summary_type_display()} for {self.recording}"


class ActionItem(models.Model):
    """Action items extracted from conversations"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.ForeignKey(
        VoiceRecording,
        on_delete=models.CASCADE,
        related_name='action_items'
    )
    
    # Action item content
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_action_items'
    )
    assigned_to_name = models.CharField(max_length=200, blank=True, help_text="Name from transcript")
    
    # Timing
    due_date = models.DateField(null=True, blank=True)
    mentioned_at_timestamp = models.IntegerField(null=True, blank=True, help_text="Seconds into recording")
    
    # Context
    context_quote = models.TextField(blank=True, help_text="Relevant quote from transcript")
    speaker = models.CharField(max_length=200, blank=True)
    
    # Status
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Linked task
    linked_task = models.ForeignKey(
        'task_management.Task',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='source_action_items'
    )
    
    # Extraction confidence
    confidence = models.FloatField(default=0.8)
    was_confirmed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'action_items'
        ordering = ['-priority', 'due_date']
    
    def __str__(self):
        return self.title


class SentimentAnalysis(models.Model):
    """Sentiment analysis of a conversation"""
    
    OVERALL_SENTIMENT = [
        ('very_negative', 'Very Negative'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
        ('positive', 'Positive'),
        ('very_positive', 'Very Positive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.OneToOneField(
        VoiceRecording,
        on_delete=models.CASCADE,
        related_name='sentiment_analysis'
    )
    
    # Overall sentiment
    overall_sentiment = models.CharField(max_length=20, choices=OVERALL_SENTIMENT, default='neutral')
    overall_score = models.FloatField(default=0.0, help_text="-1 to 1 scale")
    
    # Sentiment over time
    sentiment_timeline = models.JSONField(default=list, help_text="Sentiment scores at intervals")
    
    # By speaker
    sentiment_by_speaker = models.JSONField(default=dict)
    
    # Emotion detection
    emotions_detected = models.JSONField(default=dict, help_text="Emotion -> confidence mapping")
    dominant_emotion = models.CharField(max_length=50, blank=True)
    
    # Customer sentiment (if applicable)
    customer_sentiment = models.FloatField(null=True, blank=True)
    agent_sentiment = models.FloatField(null=True, blank=True)
    
    # Key moments
    positive_moments = models.JSONField(default=list, help_text="Timestamps of positive moments")
    negative_moments = models.JSONField(default=list, help_text="Timestamps of negative moments")
    
    # Engagement metrics
    engagement_score = models.FloatField(null=True, blank=True)
    talk_ratio = models.JSONField(default=dict, help_text="Talk time by participant")
    
    # Tone analysis
    tone_analysis = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sentiment_analyses'
    
    def __str__(self):
        return f"Sentiment for {self.recording}: {self.overall_sentiment}"


class ConversationCategory(models.Model):
    """Categories for organizing conversations"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6B7280')
    
    # Parent category for hierarchy
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='subcategories'
    )
    
    # Auto-classification keywords
    keywords = models.JSONField(default=list, help_text="Keywords for auto-classification")
    
    # Stats
    recording_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation_categories'
        verbose_name_plural = 'Conversation Categories'
    
    def __str__(self):
        return self.name


class RecordingCategory(models.Model):
    """Many-to-many relationship between recordings and categories"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.ForeignKey(
        VoiceRecording,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    category = models.ForeignKey(
        ConversationCategory,
        on_delete=models.CASCADE,
        related_name='recordings'
    )
    
    # Classification info
    is_auto_classified = models.BooleanField(default=False)
    confidence = models.FloatField(default=1.0)
    
    classified_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recording_categories'
        unique_together = ['recording', 'category']


class KeyMoment(models.Model):
    """Key moments identified in a recording"""
    
    MOMENT_TYPES = [
        ('objection', 'Objection'),
        ('agreement', 'Agreement'),
        ('question', 'Question'),
        ('commitment', 'Commitment'),
        ('concern', 'Concern'),
        ('interest', 'Interest Shown'),
        ('pricing', 'Pricing Discussion'),
        ('competitor', 'Competitor Mention'),
        ('next_step', 'Next Step'),
        ('highlight', 'Highlight'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.ForeignKey(
        VoiceRecording,
        on_delete=models.CASCADE,
        related_name='key_moments'
    )
    
    moment_type = models.CharField(max_length=20, choices=MOMENT_TYPES)
    
    # Timing
    start_timestamp = models.IntegerField(help_text="Seconds from start")
    end_timestamp = models.IntegerField(help_text="Seconds from start")
    
    # Content
    transcript_excerpt = models.TextField()
    speaker = models.CharField(max_length=200, blank=True)
    
    # Analysis
    summary = models.TextField(blank=True)
    importance_score = models.FloatField(default=0.5)
    
    # Was this marked by AI or user?
    is_ai_detected = models.BooleanField(default=True)
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'key_moments'
        ordering = ['recording', 'start_timestamp']
    
    def __str__(self):
        return f"{self.get_moment_type_display()} at {self.start_timestamp}s"


class CallScore(models.Model):
    """Sales call scoring and coaching metrics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    recording = models.OneToOneField(
        VoiceRecording,
        on_delete=models.CASCADE,
        related_name='call_score'
    )
    
    # Overall score
    overall_score = models.IntegerField(default=0, help_text="0-100 score")
    
    # Category scores
    opening_score = models.IntegerField(default=0)
    discovery_score = models.IntegerField(default=0)
    presentation_score = models.IntegerField(default=0)
    objection_handling_score = models.IntegerField(default=0)
    closing_score = models.IntegerField(default=0)
    
    # Talk metrics
    talk_to_listen_ratio = models.FloatField(null=True, blank=True)
    longest_monologue_seconds = models.IntegerField(null=True, blank=True)
    question_count = models.IntegerField(default=0)
    
    # Pace and clarity
    words_per_minute = models.IntegerField(null=True, blank=True)
    filler_word_count = models.IntegerField(default=0)
    filler_words_used = models.JSONField(default=list)
    
    # Engagement
    customer_engagement_score = models.FloatField(null=True, blank=True)
    interruption_count = models.IntegerField(default=0)
    
    # Best practices checklist
    mentioned_value_prop = models.BooleanField(default=False)
    asked_discovery_questions = models.BooleanField(default=False)
    handled_objections = models.BooleanField(default=False)
    established_next_steps = models.BooleanField(default=False)
    personalized_conversation = models.BooleanField(default=False)
    
    # Coaching suggestions
    coaching_tips = models.JSONField(default=list)
    areas_for_improvement = models.JSONField(default=list)
    strengths = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'call_scores'
    
    def __str__(self):
        return f"Score {self.overall_score}/100 for {self.recording}"


class VoiceNote(models.Model):
    """Quick voice notes linked to CRM records"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='voice_notes'
    )
    
    # File info
    audio_url = models.URLField(blank=True)
    audio_path = models.CharField(max_length=500, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Transcription
    transcript = models.TextField(blank=True)
    is_transcribed = models.BooleanField(default=False)
    
    # AI-generated title and summary
    ai_title = models.CharField(max_length=200, blank=True)
    ai_summary = models.TextField(blank=True)
    
    # Related records
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='voice_notes'
    )
    lead = models.ForeignKey(
        'lead_management.Lead',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='voice_notes'
    )
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='voice_notes'
    )
    
    # Extracted action items
    action_items_extracted = models.JSONField(default=list)
    
    # Tags
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'voice_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Voice Note: {self.ai_title or 'Untitled'}"


class TranscriptionSettings(models.Model):
    """User-specific transcription settings"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='transcription_settings'
    )
    
    # Provider preference
    preferred_provider = models.CharField(max_length=20, default='whisper')
    
    # Language settings
    default_language = models.CharField(max_length=10, default='en')
    auto_detect_language = models.BooleanField(default=True)
    
    # Processing preferences
    enable_speaker_diarization = models.BooleanField(default=True)
    enable_punctuation = models.BooleanField(default=True)
    enable_profanity_filter = models.BooleanField(default=False)
    
    # Analysis preferences
    auto_generate_summary = models.BooleanField(default=True)
    auto_extract_action_items = models.BooleanField(default=True)
    auto_analyze_sentiment = models.BooleanField(default=True)
    auto_score_calls = models.BooleanField(default=True)
    
    # Notification preferences
    notify_on_completion = models.BooleanField(default=True)
    notify_on_high_priority_action = models.BooleanField(default=True)
    
    # Custom vocabulary
    custom_vocabulary = models.JSONField(default=list, help_text="Industry-specific terms")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transcription_settings'
    
    def __str__(self):
        return f"Settings for {self.user.username}"
