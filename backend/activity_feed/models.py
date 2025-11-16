"""
Activity Feed Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import uuid

User = get_user_model()


class Activity(models.Model):
    """Activity feed for tracking all CRM actions"""
    
    ACTION_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('commented', 'Commented'),
        ('mentioned', 'Mentioned'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('shared', 'Shared'),
        ('uploaded', 'Uploaded'),
        ('status_changed', 'Status Changed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Actor (who performed the action)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    
    # Action type
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    
    # Target object (generic relation)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    target = GenericForeignKey('content_type', 'object_id')
    
    # Activity details
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    # Visibility
    is_public = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'crm_activities'
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['actor', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.actor.username} {self.action} {self.content_type.model}"


class Comment(models.Model):
    """Comments on any CRM entity"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Author
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    
    # Target object (generic relation)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    target = GenericForeignKey('content_type', 'object_id')
    
    # Comment content
    content = models.TextField()
    
    # Parent comment for threading
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Mentions
    mentions = models.ManyToManyField(User, related_name='comment_mentions', blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'crm_comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id', 'created_at']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.content_type.model}"


class Mention(models.Model):
    """User mentions in comments and activities"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User being mentioned
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentions')
    
    # Where the mention occurred (generic relation)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    source = GenericForeignKey('content_type', 'object_id')
    
    # Mention details
    mentioned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentions_created')
    context = models.TextField(help_text="Text snippet where mention occurred")
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_mentions'
        verbose_name = 'Mention'
        verbose_name_plural = 'Mentions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"@{self.user.username} by {self.mentioned_by.username}"
    
    def mark_as_read(self):
        """Mark mention as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class Notification(models.Model):
    """User notifications"""
    
    NOTIFICATION_TYPES = [
        ('mention', 'Mention'),
        ('comment', 'Comment'),
        ('assignment', 'Assignment'),
        ('update', 'Update'),
        ('reminder', 'Reminder'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipient
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_received')
    
    # Notification type
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    
    # Title and message
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related object (generic relation)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')
    
    # Actor (who triggered the notification)
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications_sent'
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Link
    action_url = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_feed_notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class Follow(models.Model):
    """Follow relationships for entities"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Follower
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    
    # Followed object (generic relation)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    target = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_follows'
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        unique_together = ['user', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['user', 'content_type', 'object_id']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} follows {self.content_type.model}"


class NotificationPreference(models.Model):
    """User notification preferences"""
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
        ('sms', 'SMS'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_mentions = models.BooleanField(default=True)
    email_assignments = models.BooleanField(default=True)
    email_comments = models.BooleanField(default=True)
    email_updates = models.BooleanField(default=False)
    email_daily_digest = models.BooleanField(default=False)
    email_weekly_digest = models.BooleanField(default=True)
    
    # Push preferences
    push_enabled = models.BooleanField(default=True)
    push_mentions = models.BooleanField(default=True)
    push_assignments = models.BooleanField(default=True)
    push_comments = models.BooleanField(default=False)
    
    # In-app preferences
    in_app_enabled = models.BooleanField(default=True)
    in_app_mentions = models.BooleanField(default=True)
    in_app_assignments = models.BooleanField(default=True)
    in_app_comments = models.BooleanField(default=True)
    in_app_updates = models.BooleanField(default=True)
    
    # Digest timing
    digest_time = models.TimeField(default='08:00:00', help_text="Time to send daily digest")
    digest_day = models.IntegerField(default=1, help_text="Day of week for weekly digest (0=Monday)")
    
    # Do Not Disturb
    dnd_enabled = models.BooleanField(default=False)
    dnd_start_time = models.TimeField(null=True, blank=True)
    dnd_end_time = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
