"""
Social Inbox Models
Unified inbox for social media interactions across multiple platforms.
"""

import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class SocialAccount(models.Model):
    """Connected social media accounts"""
    
    PLATFORM_CHOICES = [
        ('twitter', 'Twitter/X'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('disconnected', 'Disconnected'),
        ('expired', 'Token Expired'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Platform info
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_id = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    account_handle = models.CharField(max_length=255, blank=True)
    profile_url = models.URLField(blank=True)
    profile_image_url = models.URLField(blank=True)
    
    # OAuth tokens (encrypted in production)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_error = models.TextField(blank=True)
    
    # Settings
    auto_sync_enabled = models.BooleanField(default=True)
    sync_interval_minutes = models.IntegerField(default=15)
    monitor_mentions = models.BooleanField(default=True)
    monitor_messages = models.BooleanField(default=True)
    monitor_comments = models.BooleanField(default=True)
    
    # Organization
    tenant = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='social_accounts'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_inbox_accounts'
        verbose_name = 'Social Account'
        verbose_name_plural = 'Social Accounts'
        unique_together = ['platform', 'account_id', 'tenant']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.platform}: {self.account_name}"

    def is_token_expired(self):
        if self.token_expires_at:
            return timezone.now() > self.token_expires_at
        return False


class SocialConversation(models.Model):
    """A conversation thread from social media"""
    
    TYPE_CHOICES = [
        ('mention', 'Mention'),
        ('direct_message', 'Direct Message'),
        ('comment', 'Comment'),
        ('post', 'Post'),
        ('story_reply', 'Story Reply'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('spam', 'Spam'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source
    social_account = models.ForeignKey(
        SocialAccount,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    conversation_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    external_id = models.CharField(max_length=255)
    external_url = models.URLField(blank=True)
    
    # Participant info
    participant_id = models.CharField(max_length=255)
    participant_name = models.CharField(max_length=255)
    participant_handle = models.CharField(max_length=255, blank=True)
    participant_profile_url = models.URLField(blank=True)
    participant_profile_image = models.URLField(blank=True)
    participant_followers_count = models.IntegerField(null=True, blank=True)
    
    # Linked CRM entities
    linked_contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='social_conversations'
    )
    linked_lead = models.ForeignKey(
        'lead_management.Lead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='social_conversations'
    )
    
    # Status and assignment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_social_conversations'
    )
    
    # Sentiment analysis
    sentiment_score = models.FloatField(null=True, blank=True, help_text="-1 to 1")
    sentiment_label = models.CharField(max_length=20, blank=True)  # positive, negative, neutral
    sentiment_analyzed_at = models.DateTimeField(null=True, blank=True)
    
    # AI suggestions
    suggested_response = models.TextField(blank=True)
    response_tone = models.CharField(max_length=50, blank=True)
    
    # Tags and labels
    tags = models.JSONField(default=list, blank=True)
    labels = models.JSONField(default=list, blank=True)
    
    # Counts
    message_count = models.IntegerField(default=1)
    unread_count = models.IntegerField(default=1)
    
    # Timestamps
    first_message_at = models.DateTimeField()
    last_message_at = models.DateTimeField()
    first_response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_inbox_conversations'
        verbose_name = 'Social Conversation'
        verbose_name_plural = 'Social Conversations'
        unique_together = ['social_account', 'external_id']
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['status', '-last_message_at']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['social_account', '-last_message_at']),
        ]

    def __str__(self):
        return f"{self.conversation_type} from {self.participant_name}"


class SocialMessage(models.Model):
    """Individual message within a conversation"""
    
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    conversation = models.ForeignKey(
        SocialConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    # Message info
    external_id = models.CharField(max_length=255)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    content = models.TextField()
    content_type = models.CharField(max_length=50, default='text')
    
    # Media attachments
    attachments = models.JSONField(default=list, blank=True)
    
    # For outbound messages
    sent_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_social_messages'
    )
    
    # Engagement metrics
    likes_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    platform_created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'social_inbox_messages'
        verbose_name = 'Social Message'
        verbose_name_plural = 'Social Messages'
        ordering = ['platform_created_at']
        indexes = [
            models.Index(fields=['conversation', 'platform_created_at']),
        ]

    def __str__(self):
        return f"{self.direction}: {self.content[:50]}"


class SocialMonitoringRule(models.Model):
    """Rules for monitoring social media mentions and keywords"""
    
    RULE_TYPE_CHOICES = [
        ('keyword', 'Keyword'),
        ('hashtag', 'Hashtag'),
        ('mention', 'Mention'),
        ('competitor', 'Competitor'),
    ]
    
    ACTION_CHOICES = [
        ('notify', 'Send Notification'),
        ('assign', 'Auto-assign'),
        ('tag', 'Add Tag'),
        ('prioritize', 'Set Priority'),
        ('respond', 'Auto-respond'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    
    # Matching criteria
    keywords = models.JSONField(default=list, help_text="List of keywords to match")
    platforms = models.JSONField(default=list, help_text="Platforms to monitor")
    exclude_keywords = models.JSONField(default=list, blank=True)
    
    # Actions
    actions = models.JSONField(default=list, help_text="Actions to take when matched")
    auto_assign_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='social_auto_assigns'
    )
    auto_response_template = models.TextField(blank=True)
    auto_tags = models.JSONField(default=list, blank=True)
    auto_priority = models.CharField(max_length=20, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    matches_count = models.IntegerField(default=0)
    last_matched_at = models.DateTimeField(null=True, blank=True)
    
    # Organization
    tenant = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='social_monitoring_rules'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_inbox_monitoring_rules'
        verbose_name = 'Monitoring Rule'
        verbose_name_plural = 'Monitoring Rules'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SocialPost(models.Model):
    """Scheduled and published social media posts"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('publishing', 'Publishing'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Content
    content = models.TextField()
    media_urls = models.JSONField(default=list, blank=True)
    
    # Targeting
    social_accounts = models.ManyToManyField(
        SocialAccount,
        related_name='posts'
    )
    
    # Scheduling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Results per platform
    publish_results = models.JSONField(default=dict, blank=True)
    
    # Engagement metrics (aggregated)
    total_likes = models.IntegerField(default=0)
    total_shares = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)
    total_reach = models.IntegerField(default=0)
    
    # Organization
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_inbox_posts'
        verbose_name = 'Social Post'
        verbose_name_plural = 'Social Posts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Post: {self.content[:50]}"


class SocialAnalytics(models.Model):
    """Daily analytics for social accounts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    social_account = models.ForeignKey(
        SocialAccount,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    date = models.DateField()
    
    # Follower metrics
    followers_count = models.IntegerField(default=0)
    followers_gained = models.IntegerField(default=0)
    followers_lost = models.IntegerField(default=0)
    
    # Engagement metrics
    impressions = models.IntegerField(default=0)
    reach = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0)
    
    # Content metrics
    posts_count = models.IntegerField(default=0)
    likes_received = models.IntegerField(default=0)
    comments_received = models.IntegerField(default=0)
    shares_received = models.IntegerField(default=0)
    
    # Inbox metrics
    messages_received = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    avg_response_time_minutes = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'social_inbox_analytics'
        verbose_name = 'Social Analytics'
        verbose_name_plural = 'Social Analytics'
        unique_together = ['social_account', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.social_account.account_name} - {self.date}"
