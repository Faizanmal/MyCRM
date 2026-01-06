"""
Enhanced Communication Hub Serializers
"""

from rest_framework import serializers

from .enhanced_models import (
    AdvancedEmailTracking,
    CampaignRecipient,
    CampaignStep,
    CommunicationPreference,
    EmailTrackingEvent,
    InboxLabel,
    MultiChannelCampaign,
    UnifiedInboxMessage,
)


class UnifiedInboxMessageSerializer(serializers.ModelSerializer):
    """Serializer for unified inbox messages"""

    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = UnifiedInboxMessage
        fields = [
            'id', 'user', 'channel', 'direction',
            'from_address', 'from_name', 'to_address', 'to_name',
            'subject', 'preview', 'body', 'body_html',
            'attachments', 'attachment_count',
            'thread_id', 'parent_message', 'reply_count',
            'status', 'priority',
            'sentiment', 'ai_summary', 'suggested_reply',
            'contact', 'lead', 'opportunity',
            'labels', 'is_starred', 'snoozed_until',
            'external_id', 'external_thread_id',
            'received_at', 'read_at', 'replied_at', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'reply_count']

    def get_reply_count(self, obj):
        return obj.replies.count()


class UnifiedInboxMessageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for inbox list view"""

    class Meta:
        model = UnifiedInboxMessage
        fields = [
            'id', 'channel', 'direction',
            'from_address', 'from_name',
            'subject', 'preview',
            'status', 'priority', 'sentiment',
            'is_starred', 'attachment_count',
            'received_at', 'labels'
        ]


class InboxLabelSerializer(serializers.ModelSerializer):
    """Serializer for inbox labels"""

    message_count = serializers.SerializerMethodField()

    class Meta:
        model = InboxLabel
        fields = ['id', 'name', 'color', 'icon', 'is_smart', 'rules', 'message_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'message_count']

    def get_message_count(self, obj):
        return UnifiedInboxMessage.objects.filter(
            user=obj.user,
            labels__contains=[obj.name]
        ).count()


class CampaignStepSerializer(serializers.ModelSerializer):
    """Serializer for campaign steps"""

    class Meta:
        model = CampaignStep
        fields = [
            'id', 'campaign', 'step_type', 'name', 'order',
            'config', 'subject', 'body', 'template_id',
            'delay_days', 'delay_hours', 'conditions',
            'on_success_step', 'on_failure_step',
            'sent_count', 'delivered_count', 'opened_count',
            'clicked_count', 'replied_count', 'is_active'
        ]
        read_only_fields = ['id', 'sent_count', 'delivered_count',
                          'opened_count', 'clicked_count', 'replied_count']


class MultiChannelCampaignSerializer(serializers.ModelSerializer):
    """Serializer for multi-channel campaigns"""

    steps = CampaignStepSerializer(many=True, read_only=True)
    recipient_count = serializers.SerializerMethodField()

    class Meta:
        model = MultiChannelCampaign
        fields = [
            'id', 'user', 'name', 'description',
            'target_audience', 'target_count', 'channels',
            'status', 'start_date', 'end_date',
            'goals', 'budget', 'spent',
            'total_sent', 'total_delivered', 'total_opens',
            'total_clicks', 'total_conversions',
            'steps', 'recipient_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'target_count',
            'total_sent', 'total_delivered', 'total_opens',
            'total_clicks', 'total_conversions', 'spent',
            'created_at', 'updated_at'
        ]

    def get_recipient_count(self, obj):
        return obj.recipients.count()


class MultiChannelCampaignListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for campaign list"""

    class Meta:
        model = MultiChannelCampaign
        fields = [
            'id', 'name', 'channels', 'status',
            'target_count', 'total_sent', 'total_opens',
            'start_date', 'created_at'
        ]


class CampaignRecipientSerializer(serializers.ModelSerializer):
    """Serializer for campaign recipients"""

    class Meta:
        model = CampaignRecipient
        fields = [
            'id', 'campaign', 'contact', 'lead', 'email',
            'status', 'current_step',
            'opens', 'clicks', 'replies', 'conversions',
            'entered_at', 'next_step_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'opens', 'clicks', 'replies', 'conversions',
            'entered_at', 'completed_at'
        ]


class EmailTrackingEventSerializer(serializers.ModelSerializer):
    """Serializer for email tracking events"""

    class Meta:
        model = EmailTrackingEvent
        fields = [
            'id', 'tracking', 'event_type', 'url',
            'device_type', 'browser', 'os', 'user_agent',
            'ip_address', 'country', 'city', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AdvancedEmailTrackingSerializer(serializers.ModelSerializer):
    """Serializer for advanced email tracking"""

    events = EmailTrackingEventSerializer(many=True, read_only=True)

    class Meta:
        model = AdvancedEmailTracking
        fields = [
            'id', 'user', 'tracking_id', 'email_id',
            'recipient_email', 'contact', 'subject', 'sent_at',
            'delivered', 'delivered_at',
            'opened', 'open_count', 'first_opened_at', 'last_opened_at',
            'clicked', 'click_count', 'clicked_urls', 'first_clicked_at', 'last_clicked_at',
            'replied', 'replied_at',
            'bounced', 'bounce_type', 'bounced_at',
            'unsubscribed', 'unsubscribed_at',
            'complained', 'complained_at',
            'engagement_score', 'time_to_open_seconds', 'read_duration_seconds',
            'unsubscribe_risk', 'reply_likelihood',
            'devices', 'locations', 'events'
        ]
        read_only_fields = [
            'id', 'user', 'tracking_id',
            'delivered', 'delivered_at', 'opened', 'open_count',
            'first_opened_at', 'last_opened_at',
            'clicked', 'click_count', 'clicked_urls',
            'first_clicked_at', 'last_clicked_at',
            'replied', 'replied_at', 'bounced', 'bounced_at',
            'unsubscribed', 'unsubscribed_at', 'complained', 'complained_at',
            'engagement_score', 'time_to_open_seconds', 'read_duration_seconds',
            'devices', 'locations'
        ]


class AdvancedEmailTrackingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for tracking list"""

    class Meta:
        model = AdvancedEmailTracking
        fields = [
            'id', 'tracking_id', 'recipient_email', 'subject',
            'sent_at', 'opened', 'clicked', 'replied',
            'engagement_score', 'unsubscribe_risk'
        ]


class CommunicationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for communication preferences"""

    class Meta:
        model = CommunicationPreference
        fields = [
            'id', 'contact',
            'email_enabled', 'sms_enabled', 'phone_enabled', 'social_enabled',
            'email_frequency', 'preferred_email_time',
            'opted_in_topics', 'opted_out_topics',
            'best_contact_times', 'timezone',
            'avg_response_time_hours', 'most_engaged_channel',
            'global_unsubscribe', 'unsubscribed_at', 'unsubscribe_reason',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'avg_response_time_hours', 'most_engaged_channel',
            'updated_at'
        ]


# Request/Response Serializers

class InboxSearchSerializer(serializers.Serializer):
    """Serializer for inbox search request"""

    query = serializers.CharField(required=False, allow_blank=True)
    channels = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    status = serializers.CharField(required=False)
    priority = serializers.CharField(required=False)
    labels = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    contact_id = serializers.UUIDField(required=False)
    from_date = serializers.DateTimeField(required=False)
    to_date = serializers.DateTimeField(required=False)
    starred_only = serializers.BooleanField(default=False)
    limit = serializers.IntegerField(default=50, max_value=200)


class BulkUpdateStatusSerializer(serializers.Serializer):
    """Serializer for bulk status update"""

    message_ids = serializers.ListField(
        child=serializers.UUIDField()
    )
    status = serializers.ChoiceField(choices=['read', 'unread', 'archived', 'snoozed'])


class ApplyLabelSerializer(serializers.Serializer):
    """Serializer for applying labels"""

    message_ids = serializers.ListField(
        child=serializers.UUIDField()
    )
    label = serializers.CharField()
    remove = serializers.BooleanField(default=False)


class SnoozeMessageSerializer(serializers.Serializer):
    """Serializer for snoozing a message"""

    snooze_until = serializers.DateTimeField()


class GenerateAIReplySerializer(serializers.Serializer):
    """Serializer for AI reply generation request"""

    pass  # No input needed, uses message_id from URL


class CreateCampaignSerializer(serializers.Serializer):
    """Serializer for creating a campaign"""

    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    channels = serializers.ListField(
        child=serializers.CharField()
    )
    target_audience = serializers.DictField()
    goals = serializers.DictField(required=False)
    budget = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )


class AddCampaignStepSerializer(serializers.Serializer):
    """Serializer for adding a campaign step"""

    step_type = serializers.ChoiceField(choices=[
        'email', 'sms', 'linkedin_message', 'linkedin_connect',
        'twitter_dm', 'call_task', 'delay', 'condition', 'ab_test'
    ])
    name = serializers.CharField(max_length=200)
    order = serializers.IntegerField()
    config = serializers.DictField(required=False)
    subject = serializers.CharField(max_length=500, required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)
    delay_days = serializers.IntegerField(default=0)
    delay_hours = serializers.IntegerField(default=0)
    conditions = serializers.ListField(required=False)


class ABTestSerializer(serializers.Serializer):
    """Serializer for A/B test configuration"""

    variants = serializers.ListField(
        child=serializers.DictField()
    )


class CreateTrackingSerializer(serializers.Serializer):
    """Serializer for creating email tracking"""

    recipient_email = serializers.EmailField()
    subject = serializers.CharField(max_length=500)
    contact_id = serializers.UUIDField(required=False)


class RecordEventSerializer(serializers.Serializer):
    """Serializer for recording tracking events"""

    event_type = serializers.ChoiceField(choices=[
        'delivered', 'opened', 'clicked', 'replied',
        'bounced', 'unsubscribed', 'complained'
    ])
    url = serializers.URLField(required=False)
    device_info = serializers.DictField(required=False)
    location_info = serializers.DictField(required=False)


class UnsubscribeSerializer(serializers.Serializer):
    """Serializer for unsubscribe request"""

    contact_id = serializers.UUIDField()
    reason = serializers.CharField(required=False, allow_blank=True)
    topics = serializers.ListField(
        child=serializers.CharField(), required=False
    )
