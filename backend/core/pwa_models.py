"""
Progressive Web App (PWA) Backend Support Models
"""

import uuid

from django.conf import settings
from django.db import models


class PushSubscription(models.Model):
    """Web push notification subscriptions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions'
    )

    # Subscription details (from browser Push API)
    endpoint = models.TextField()
    auth_key = models.CharField(max_length=500)
    p256dh_key = models.CharField(max_length=500)

    # Device info
    browser = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)

    # Subscription preferences
    is_active = models.BooleanField(default=True)
    notifications_enabled = models.BooleanField(default=True)

    # Notification preferences
    notify_new_leads = models.BooleanField(default=True)
    notify_task_reminders = models.BooleanField(default=True)
    notify_deal_updates = models.BooleanField(default=True)
    notify_messages = models.BooleanField(default=True)
    notify_mentions = models.BooleanField(default=True)

    # Quiet hours
    quiet_start = models.TimeField(blank=True)
    quiet_end = models.TimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'push_subscriptions'
        unique_together = ['user', 'endpoint']

    def __str__(self):
        return f"Push subscription for {self.user}"


class PushNotification(models.Model):
    """Log of sent push notifications"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('clicked', 'Clicked'),
        ('failed', 'Failed'),
    ]

    NOTIFICATION_TYPES = [
        ('new_lead', 'New Lead'),
        ('task_reminder', 'Task Reminder'),
        ('task_assigned', 'Task Assigned'),
        ('deal_update', 'Deal Update'),
        ('deal_won', 'Deal Won'),
        ('deal_lost', 'Deal Lost'),
        ('new_message', 'New Message'),
        ('mention', 'Mention'),
        ('meeting_reminder', 'Meeting Reminder'),
        ('activity', 'Activity'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    subscription = models.ForeignKey(
        PushSubscription,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)

    # Content
    title = models.CharField(max_length=200)
    body = models.TextField()
    icon = models.URLField(blank=True)
    badge = models.URLField(blank=True)
    image = models.URLField(blank=True)

    # Action
    click_action = models.URLField(blank=True)
    data = models.JSONField(default=dict)

    # Actions (buttons)
    actions = models.JSONField(default=list)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)

    # Tracking
    sent_at = models.DateTimeField(blank=True)
    delivered_at = models.DateTimeField(blank=True)
    clicked_at = models.DateTimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'push_notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type}: {self.title}"


class BackgroundSyncJob(models.Model):
    """Track background sync operations for PWA"""

    SYNC_TYPES = [
        ('contacts', 'Contacts Sync'),
        ('leads', 'Leads Sync'),
        ('opportunities', 'Opportunities Sync'),
        ('tasks', 'Tasks Sync'),
        ('activities', 'Activities Sync'),
        ('messages', 'Messages Sync'),
        ('full', 'Full Sync'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='background_sync_jobs'
    )

    sync_type = models.CharField(max_length=30, choices=SYNC_TYPES)
    tag = models.CharField(max_length=100)  # Service worker sync tag

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Data to sync
    payload = models.JSONField(default=dict)

    # Results
    synced_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    error_details = models.JSONField(default=list)

    # Timing
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True)
    completed_at = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'background_sync_jobs'
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.sync_type} sync - {self.status}"


class CacheManifest(models.Model):
    """Track cached resources for PWA"""

    CACHE_STRATEGIES = [
        ('cache_first', 'Cache First'),
        ('network_first', 'Network First'),
        ('stale_while_revalidate', 'Stale While Revalidate'),
        ('network_only', 'Network Only'),
        ('cache_only', 'Cache Only'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Resource info
    url_pattern = models.CharField(max_length=500)
    resource_type = models.CharField(max_length=50)  # api, static, image, etc.

    # Caching strategy
    strategy = models.CharField(max_length=30, choices=CACHE_STRATEGIES)
    max_age_seconds = models.IntegerField(default=3600)

    # Version control
    version = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cache_manifests'

    def __str__(self):
        return f"{self.url_pattern} ({self.strategy})"


class OfflineAction(models.Model):
    """Queue actions taken offline for later sync"""

    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('api_call', 'API Call'),
    ]

    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('syncing', 'Syncing'),
        ('synced', 'Synced'),
        ('conflict', 'Conflict'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offline_actions'
    )

    # Action details
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=200, blank=True)

    # API call details (for api_call type)
    method = models.CharField(max_length=10, blank=True)  # GET, POST, PUT, DELETE
    url = models.CharField(max_length=500, blank=True)

    # Request data
    payload = models.JSONField(default=dict)
    headers = models.JSONField(default=dict)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')

    # Retry handling
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)

    # Response (after sync)
    response_status = models.IntegerField(blank=True)
    response_data = models.JSONField(blank=True)
    error_message = models.TextField(blank=True)

    # Timestamps
    created_offline_at = models.DateTimeField()  # When action was taken offline
    synced_at = models.DateTimeField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'offline_actions'
        ordering = ['created_offline_at']

    def __str__(self):
        return f"{self.action_type} {self.entity_type} - {self.status}"


class InstallationAnalytics(models.Model):
    """Track PWA installation analytics"""

    INSTALL_SOURCES = [
        ('browser_prompt', 'Browser Prompt'),
        ('custom_prompt', 'Custom Prompt'),
        ('app_store', 'App Store'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        related_name='pwa_installations'
    )

    # Installation info
    installed = models.BooleanField(default=False)
    install_source = models.CharField(max_length=30, choices=INSTALL_SOURCES, blank=True)

    # Device info
    platform = models.CharField(max_length=50)  # windows, macos, ios, android
    browser = models.CharField(max_length=100)

    # Prompt tracking
    prompt_shown = models.BooleanField(default=False)
    prompt_shown_at = models.DateTimeField(blank=True)
    prompt_dismissed = models.BooleanField(default=False)
    prompt_accepted = models.BooleanField(default=False)

    # Installation timestamps
    installed_at = models.DateTimeField(blank=True)
    uninstalled_at = models.DateTimeField(blank=True)

    # Usage tracking
    standalone_launches = models.IntegerField(default=0)
    last_standalone_launch = models.DateTimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pwa_installation_analytics'

    def __str__(self):
        status = "Installed" if self.installed else "Not Installed"
        return f"PWA {status} - {self.platform}/{self.browser}"
