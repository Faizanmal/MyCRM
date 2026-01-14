"""
AI Sales Assistant - Conversational Chatbot Models
Persistent AI assistant for pipeline data, insights, and recommendations
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ConversationSession(models.Model):
    """AI chatbot conversation session"""

    SESSION_TYPES = [
        ('general', 'General Chat'),
        ('pipeline', 'Pipeline Analysis'),
        ('deal_help', 'Deal Assistance'),
        ('coaching', 'Sales Coaching'),
        ('insights', 'Insights & Analytics'),
        ('content', 'Content Generation'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('idle', 'Idle'),
        ('closed', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chat_sessions')

    title = models.CharField(max_length=200, default='New Conversation')
    session_type = models.CharField(max_length=50, choices=SESSION_TYPES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Context for the conversation
    context = models.JSONField(default=dict, help_text="Session context data")
    pinned_entities = models.JSONField(default=list, help_text="Pinned contacts/deals for context")

    # Stats
    message_count = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)

    # Bookmarking
    is_starred = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_chat_sessions'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.title} - {self.user.email}"


class ChatMessage(models.Model):
    """Individual chat messages"""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
        ('system', 'System'),
    ]

    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('insight', 'Insight Card'),
        ('chart', 'Chart/Visualization'),
        ('action', 'Action Item'),
        ('suggestion', 'Suggestion'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ConversationSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()

    # Rich content
    metadata = models.JSONField(default=dict, help_text="Charts, actions, entities")
    attachments = models.JSONField(default=list, help_text="Referenced entities")

    # For action items
    action_taken = models.BooleanField(default=False)
    action_result = models.TextField(blank=True)

    # Feedback
    was_helpful = models.BooleanField(null=True)
    feedback = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_chat_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class ChatIntent(models.Model):
    """Recognized intents for routing chat messages"""

    INTENT_CATEGORIES = [
        ('query', 'Data Query'),
        ('action', 'Action Request'),
        ('help', 'Help Request'),
        ('feedback', 'Feedback'),
        ('navigation', 'Navigation'),
        ('generation', 'Content Generation'),
        ('analysis', 'Analysis Request'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=INTENT_CATEGORIES)
    description = models.TextField()

    # Training data
    example_phrases = models.JSONField(default=list)
    keywords = models.JSONField(default=list)

    # Handler
    handler_function = models.CharField(max_length=200)
    requires_entities = models.JSONField(default=list)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'ai_chat_intents'

    def __str__(self):
        return self.name


class QuickAction(models.Model):
    """Quick actions suggested by the AI"""

    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    ACTION_TYPES = [
        ('call', 'Make Call'),
        ('email', 'Send Email'),
        ('task', 'Create Task'),
        ('meeting', 'Schedule Meeting'),
        ('update', 'Update Record'),
        ('follow_up', 'Follow Up'),
        ('review', 'Review Deal'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_quick_actions')

    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Target entity
    entity_type = models.CharField(max_length=50)  # contact, opportunity, lead
    entity_id = models.UUIDField()

    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')

    # Reasoning
    reason = models.TextField()
    expected_impact = models.TextField()

    # Status
    is_dismissed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True)

    # Generated from
    source_insight = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'ai_quick_actions'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.get_action_type_display()}: {self.title}"


class PredictiveDealIntelligence(models.Model):
    """ML-powered deal predictions and risk assessment"""

    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.CASCADE,
        related_name='predictive_intelligence'
    )

    # Win probability
    win_probability = models.DecimalField(max_digits=5, decimal_places=2)
    probability_trend = models.CharField(max_length=20)  # increasing, decreasing, stable
    probability_factors = models.JSONField(default=dict)

    # Deal velocity
    expected_close_date = models.DateField()
    velocity_score = models.DecimalField(max_digits=5, decimal_places=2)
    velocity_comparison = models.JSONField(default=dict)  # vs similar deals
    days_to_close_prediction = models.IntegerField()

    # Risk assessment
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    risk_factors = models.JSONField(default=list)
    risk_mitigation_actions = models.JSONField(default=list)

    # Health score
    deal_health_score = models.IntegerField()  # 0-100
    health_breakdown = models.JSONField(default=dict)

    # Engagement analysis
    engagement_score = models.DecimalField(max_digits=5, decimal_places=2)
    stakeholder_engagement = models.JSONField(default=dict)
    communication_frequency = models.JSONField(default=dict)

    # Next best actions
    recommended_actions = models.JSONField(default=list)

    # Competitive analysis
    competitive_threat_level = models.CharField(max_length=20, blank=True)
    competitor_signals = models.JSONField(default=list)

    # Model metadata
    model_version = models.CharField(max_length=50)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)

    analyzed_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_predictive_deal_intelligence'
        ordering = ['-analyzed_at']
        get_latest_by = 'analyzed_at'

    def __str__(self):
        return f"Intelligence for {self.opportunity}"


class SmartContent(models.Model):
    """AI-generated personalized content"""

    CONTENT_TYPES = [
        ('email', 'Email'),
        ('call_script', 'Call Script'),
        ('objection_response', 'Objection Response'),
        ('social_post', 'Social Media Post'),
        ('linkedin_message', 'LinkedIn Message'),
        ('proposal_section', 'Proposal Section'),
        ('follow_up', 'Follow-up Message'),
        ('sms', 'SMS Message'),
    ]

    TONES = [
        ('professional', 'Professional'),
        ('friendly', 'Friendly'),
        ('casual', 'Casual'),
        ('formal', 'Formal'),
        ('urgent', 'Urgent'),
        ('enthusiastic', 'Enthusiastic'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='smart_content')

    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES)
    tone = models.CharField(max_length=30, choices=TONES, default='professional')

    # Context
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        blank=True
    )
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        blank=True
    )

    # Input
    prompt = models.TextField()
    context_data = models.JSONField(default=dict)

    # Output
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    variations = models.JSONField(default=list)

    # Personalization
    personalization_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    personalization_elements = models.JSONField(default=list)

    # Usage
    was_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True)

    # Feedback
    rating = models.IntegerField(blank=True)
    feedback = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_smart_content'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_content_type_display()}: {self.title or self.content[:50]}"
