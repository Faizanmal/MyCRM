from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ChurnPrediction(models.Model):
    """Customer churn prediction results"""
    contact = models.ForeignKey('contact_management.Contact', on_delete=models.CASCADE, related_name='churn_predictions')

    # Prediction results
    churn_probability = models.FloatField(help_text="Probability of churn (0-1)")
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
            ('critical', 'Critical Risk')
        ]
    )

    # Contributing factors
    factors = models.JSONField(default=dict, help_text="Factors contributing to prediction")
    confidence_score = models.FloatField(help_text="Model confidence (0-1)")

    # Recommendations
    recommended_actions = models.JSONField(default=list)

    # Metadata
    model_version = models.CharField(max_length=50)
    predicted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When prediction becomes stale")

    class Meta:
        ordering = ['-predicted_at']
        indexes = [
            models.Index(fields=['contact', '-predicted_at']),
            models.Index(fields=['risk_level', '-predicted_at']),
        ]
        verbose_name = 'Churn Prediction'
        verbose_name_plural = 'Churn Predictions'

    def __str__(self):
        return f"{self.contact} - {self.risk_level} ({self.churn_probability:.2%})"

    def is_expired(self):
        return timezone.now() > self.expires_at


class NextBestAction(models.Model):
    """AI-recommended next best actions"""
    ACTION_TYPES = [
        ('call', 'Schedule Call'),
        ('email', 'Send Email'),
        ('meeting', 'Schedule Meeting'),
        ('follow_up', 'Follow Up'),
        ('proposal', 'Send Proposal'),
        ('discount', 'Offer Discount'),
        ('upsell', 'Upsell Opportunity'),
        ('check_in', 'Customer Check-in'),
    ]

    ENTITY_TYPES = [
        ('lead', 'Lead'),
        ('contact', 'Contact'),
        ('opportunity', 'Opportunity'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommended_actions')
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_id = models.IntegerField()

    # Recommendation
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    reasoning = models.TextField(help_text="Why this action is recommended")

    # Priority and timing
    priority_score = models.FloatField(help_text="Priority score (0-100)")
    expected_impact = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    suggested_timing = models.DateTimeField(blank=True)

    # Action status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('dismissed', 'Dismissed'),
            ('completed', 'Completed'),
        ],
        default='pending'
    )

    # Metadata
    model_version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True)

    class Meta:
        ordering = ['-priority_score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status', '-priority_score']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]
        verbose_name = 'Next Best Action'
        verbose_name_plural = 'Next Best Actions'

    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.title}"


class AIGeneratedContent(models.Model):
    """AI-generated email and messaging content"""
    CONTENT_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('social', 'Social Media'),
        ('proposal', 'Proposal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_content')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)

    # Input context
    prompt = models.TextField(help_text="User's input prompt")
    context_data = models.JSONField(default=dict, help_text="Context used for generation")

    # Generated content
    subject = models.CharField(max_length=500, blank=True)
    body = models.TextField()
    tone = models.CharField(max_length=50, default='professional')
    language = models.CharField(max_length=10, default='en')

    # Quality metrics
    quality_score = models.FloatField(blank=True)
    readability_score = models.FloatField(blank=True)

    # Usage tracking
    was_used = models.BooleanField(default=False)
    was_edited = models.BooleanField(default=False)
    user_rating = models.IntegerField(blank=True, help_text="1-5 star rating")

    # Metadata
    model_used = models.CharField(max_length=100, default='gpt-3.5-turbo')
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['content_type', '-created_at']),
        ]
        verbose_name = 'AI Generated Content'
        verbose_name_plural = 'AI Generated Content'

    def __str__(self):
        return f"{self.content_type} - {self.subject[:50]}"


class SentimentAnalysis(models.Model):
    """Sentiment analysis for communications"""
    ENTITY_TYPES = [
        ('email', 'Email'),
        ('call', 'Call Transcript'),
        ('chat', 'Chat Message'),
        ('note', 'Note'),
    ]

    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_id = models.IntegerField()
    text_content = models.TextField()

    # Analysis results
    sentiment = models.CharField(
        max_length=20,
        choices=[
            ('very_negative', 'Very Negative'),
            ('negative', 'Negative'),
            ('neutral', 'Neutral'),
            ('positive', 'Positive'),
            ('very_positive', 'Very Positive'),
        ]
    )
    sentiment_score = models.FloatField(help_text="Sentiment score (-1 to 1)")
    confidence = models.FloatField(help_text="Analysis confidence (0-1)")

    # Detailed analysis
    emotions = models.JSONField(default=dict, help_text="Emotion breakdown")
    keywords = models.JSONField(default=list, help_text="Key phrases extracted")
    topics = models.JSONField(default=list, help_text="Topics identified")

    # Alerts
    requires_attention = models.BooleanField(default=False)
    alert_reason = models.TextField(blank=True)

    # Metadata
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['sentiment', '-analyzed_at']),
            models.Index(fields=['requires_attention']),
        ]
        verbose_name = 'Sentiment Analysis'
        verbose_name_plural = 'Sentiment Analyses'

    def __str__(self):
        return f"{self.entity_type} - {self.sentiment}"


class AIModelMetrics(models.Model):
    """Track AI model performance metrics"""
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=50)
    metric_type = models.CharField(
        max_length=50,
        choices=[
            ('accuracy', 'Accuracy'),
            ('precision', 'Precision'),
            ('recall', 'Recall'),
            ('f1_score', 'F1 Score'),
            ('auc_roc', 'AUC-ROC'),
        ]
    )

    metric_value = models.FloatField()
    sample_size = models.IntegerField()

    # Metadata
    measured_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-measured_at']
        indexes = [
            models.Index(fields=['model_name', '-measured_at']),
        ]
        verbose_name = 'AI Model Metrics'
        verbose_name_plural = 'AI Model Metrics'

    def __str__(self):
        return f"{self.model_name} - {self.metric_type}: {self.metric_value:.3f}"
