"""
AI Chatbot Models
Conversation history, intents, and AI-powered sales assistance.
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ChatSession(models.Model):
    """A chat session with the AI assistant"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')

    title = models.CharField(max_length=255, default='New Chat')

    # Context
    context_type = models.CharField(max_length=50, blank=True)  # lead, contact, opportunity
    context_id = models.CharField(max_length=100, blank=True)

    # Session data
    is_active = models.BooleanField(default=True)
    message_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'ai_chatbot_sessions'
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(models.Model):
    """Individual message in a chat session"""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('query_result', 'Query Result'),
        ('email_draft', 'Email Draft'),
        ('action_suggestion', 'Action Suggestion'),
        ('data_summary', 'Data Summary'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message_type = models.CharField(max_length=30, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()

    # For structured responses
    structured_data = models.JSONField(default=dict, blank=True)

    # Metadata
    tokens_used = models.IntegerField(default=0)
    model_used = models.CharField(max_length=50, blank=True)
    processing_time_ms = models.IntegerField(default=0)

    # Feedback
    is_helpful = models.BooleanField(blank=True)
    feedback = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_chatbot_messages'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class ChatIntent(models.Model):
    """Recognized intents and their handlers"""

    CATEGORY_CHOICES = [
        ('query', 'Data Query'),
        ('email', 'Email Generation'),
        ('action', 'Action Suggestion'),
        ('report', 'Report Generation'),
        ('help', 'Help/Documentation'),
        ('general', 'General'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)

    # Example phrases for training
    example_phrases = models.JSONField(default=list)

    # Handler configuration
    handler_function = models.CharField(max_length=255)
    required_parameters = models.JSONField(default=list, blank=True)

    # Usage stats
    usage_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_chatbot_intents'
        verbose_name = 'Chat Intent'
        verbose_name_plural = 'Chat Intents'

    def __str__(self):
        return self.name


class QuickAction(models.Model):
    """Pre-defined quick actions for the chatbot"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    # The prompt to send
    prompt_template = models.TextField()

    # Context requirements
    requires_context = models.BooleanField(default=False)
    context_types = models.JSONField(default=list, blank=True)

    # Display
    category = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_chatbot_quick_actions'
        verbose_name = 'Quick Action'
        verbose_name_plural = 'Quick Actions'
        ordering = ['category', 'order']

    def __str__(self):
        return self.name


class EmailTemplate(models.Model):
    """AI-generated email templates"""

    TONE_CHOICES = [
        ('professional', 'Professional'),
        ('friendly', 'Friendly'),
        ('formal', 'Formal'),
        ('casual', 'Casual'),
        ('persuasive', 'Persuasive'),
    ]

    PURPOSE_CHOICES = [
        ('follow_up', 'Follow Up'),
        ('introduction', 'Introduction'),
        ('proposal', 'Proposal'),
        ('thank_you', 'Thank You'),
        ('meeting_request', 'Meeting Request'),
        ('closing', 'Closing'),
        ('nurture', 'Nurture'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    tone = models.CharField(max_length=30, choices=TONE_CHOICES, default='professional')

    # Template content
    subject_template = models.CharField(max_length=255)
    body_template = models.TextField()

    # Variables
    variables = models.JSONField(default=list, blank=True)

    # Usage
    usage_count = models.IntegerField(default=0)
    avg_open_rate = models.FloatField(blank=True)
    avg_response_rate = models.FloatField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='ai_chatbot_email_templates')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_chatbot_email_templates'
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'

    def __str__(self):
        return self.name
