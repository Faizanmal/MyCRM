"""
Progressive Web App (PWA) Serializers
"""

from rest_framework import serializers

from .pwa_models import (
    BackgroundSyncJob,
    CacheManifest,
    InstallationAnalytics,
    OfflineAction,
    PushNotification,
    PushSubscription,
)


class PushSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for push subscriptions"""

    class Meta:
        model = PushSubscription
        fields = [
            'id', 'user', 'endpoint', 'auth_key', 'p256dh_key',
            'browser', 'user_agent',
            'is_active', 'notifications_enabled',
            'notify_new_leads', 'notify_task_reminders',
            'notify_deal_updates', 'notify_messages', 'notify_mentions',
            'quiet_start', 'quiet_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PushNotificationSerializer(serializers.ModelSerializer):
    """Serializer for push notifications"""

    class Meta:
        model = PushNotification
        fields = [
            'id', 'subscription', 'notification_type',
            'title', 'body', 'icon', 'badge', 'image',
            'click_action', 'data', 'actions',
            'status', 'error_message',
            'sent_at', 'delivered_at', 'clicked_at',
            'created_at'
        ]
        read_only_fields = [
            'id', 'subscription', 'status', 'error_message',
            'sent_at', 'delivered_at', 'clicked_at', 'created_at'
        ]


class PushNotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for notification list"""

    class Meta:
        model = PushNotification
        fields = [
            'id', 'notification_type', 'title',
            'status', 'sent_at', 'clicked_at'
        ]


class BackgroundSyncJobSerializer(serializers.ModelSerializer):
    """Serializer for background sync jobs"""

    class Meta:
        model = BackgroundSyncJob
        fields = [
            'id', 'user', 'sync_type', 'tag',
            'status', 'payload',
            'synced_count', 'failed_count', 'error_details',
            'requested_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'status',
            'synced_count', 'failed_count', 'error_details',
            'requested_at', 'started_at', 'completed_at'
        ]


class CacheManifestSerializer(serializers.ModelSerializer):
    """Serializer for cache manifests"""

    class Meta:
        model = CacheManifest
        fields = [
            'id', 'url_pattern', 'resource_type',
            'strategy', 'max_age_seconds', 'version',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OfflineActionSerializer(serializers.ModelSerializer):
    """Serializer for offline actions"""

    class Meta:
        model = OfflineAction
        fields = [
            'id', 'user', 'action_type', 'entity_type', 'entity_id',
            'method', 'url', 'payload', 'headers',
            'status', 'retry_count', 'max_retries',
            'response_status', 'response_data', 'error_message',
            'created_offline_at', 'synced_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'retry_count',
            'response_status', 'response_data', 'error_message',
            'synced_at', 'created_at'
        ]


class InstallationAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for installation analytics"""

    class Meta:
        model = InstallationAnalytics
        fields = [
            'id', 'user', 'installed', 'install_source',
            'platform', 'browser',
            'prompt_shown', 'prompt_shown_at',
            'prompt_dismissed', 'prompt_accepted',
            'installed_at', 'uninstalled_at',
            'standalone_launches', 'last_standalone_launch',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'updated_at'
        ]


# Request Serializers

class SubscribePushSerializer(serializers.Serializer):
    """Serializer for push subscription request"""

    endpoint = serializers.CharField()
    auth_key = serializers.CharField()
    p256dh_key = serializers.CharField()
    browser = serializers.CharField(required=False, allow_blank=True)
    user_agent = serializers.CharField(required=False, allow_blank=True)
    preferences = serializers.DictField(required=False)


class UpdatePreferencesSerializer(serializers.Serializer):
    """Serializer for updating notification preferences"""

    notifications_enabled = serializers.BooleanField(required=False)
    notify_new_leads = serializers.BooleanField(required=False)
    notify_task_reminders = serializers.BooleanField(required=False)
    notify_deal_updates = serializers.BooleanField(required=False)
    notify_messages = serializers.BooleanField(required=False)
    notify_mentions = serializers.BooleanField(required=False)
    quiet_start = serializers.TimeField(required=False, allow_null=True)
    quiet_end = serializers.TimeField(required=False, allow_null=True)


class SendNotificationSerializer(serializers.Serializer):
    """Serializer for sending push notification"""

    notification_type = serializers.ChoiceField(choices=[
        'new_lead', 'task_reminder', 'task_assigned',
        'deal_update', 'deal_won', 'deal_lost',
        'new_message', 'mention', 'meeting_reminder',
        'activity', 'system'
    ])
    title = serializers.CharField(max_length=200)
    body = serializers.CharField()
    click_action = serializers.URLField(required=False, allow_blank=True)
    data = serializers.DictField(required=False)
    icon = serializers.URLField(required=False, allow_blank=True)
    actions = serializers.ListField(
        child=serializers.DictField(), required=False
    )


class RequestSyncSerializer(serializers.Serializer):
    """Serializer for requesting background sync"""

    sync_type = serializers.ChoiceField(choices=[
        'contacts', 'leads', 'opportunities',
        'tasks', 'activities', 'messages', 'full'
    ])
    tag = serializers.CharField(max_length=100)
    payload = serializers.DictField(required=False)


class QueueOfflineActionSerializer(serializers.Serializer):
    """Serializer for queueing offline action"""

    action_type = serializers.ChoiceField(choices=[
        'create', 'update', 'delete', 'api_call'
    ])
    entity_type = serializers.CharField(max_length=100)
    entity_id = serializers.CharField(max_length=200, required=False, allow_blank=True)
    method = serializers.CharField(max_length=10, required=False, allow_blank=True)
    url = serializers.CharField(max_length=500, required=False, allow_blank=True)
    payload = serializers.DictField(required=False)
    headers = serializers.DictField(required=False)
    created_offline_at = serializers.DateTimeField(required=False)


class TrackInstallationSerializer(serializers.Serializer):
    """Serializer for tracking PWA installation"""

    platform = serializers.CharField(max_length=50)
    browser = serializers.CharField(max_length=100)
    install_source = serializers.ChoiceField(
        choices=['browser_prompt', 'custom_prompt', 'app_store'],
        required=False
    )
    event = serializers.ChoiceField(choices=[
        'prompt_shown', 'prompt_accepted', 'prompt_dismissed',
        'installed', 'standalone_launch'
    ])
