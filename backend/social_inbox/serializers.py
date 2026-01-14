"""
Social Inbox Serializers
"""

from rest_framework import serializers

from .models import (
    SocialAccount,
    SocialAnalytics,
    SocialConversation,
    SocialMessage,
    SocialMonitoringRule,
    SocialPost,
)


class SocialAccountSerializer(serializers.ModelSerializer):
    """Serializer for social accounts"""
    is_token_expired = serializers.SerializerMethodField()

    class Meta:
        model = SocialAccount
        fields = [
            'id', 'platform', 'account_id', 'account_name', 'account_handle',
            'profile_url', 'profile_image_url', 'status', 'last_sync_at',
            'auto_sync_enabled', 'monitor_mentions', 'monitor_messages',
            'monitor_comments', 'is_token_expired', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'last_sync_at', 'created_at']

    def get_is_token_expired(self, obj):
        return obj.is_token_expired()


class SocialMessageSerializer(serializers.ModelSerializer):
    """Serializer for social messages"""
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = SocialMessage
        fields = [
            'id', 'direction', 'content', 'content_type', 'attachments',
            'sender_name', 'likes_count', 'shares_count', 'replies_count',
            'is_read', 'platform_created_at'
        ]

    def get_sender_name(self, obj):
        if obj.direction == 'outbound' and obj.sent_by:
            return f"{obj.sent_by.first_name} {obj.sent_by.last_name}"
        return obj.conversation.participant_name


class SocialConversationListSerializer(serializers.ModelSerializer):
    """Serializer for listing conversations"""
    platform = serializers.CharField(source='social_account.platform')
    account_name = serializers.CharField(source='social_account.account_name')
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = SocialConversation
        fields = [
            'id', 'platform', 'account_name', 'conversation_type',
            'participant_name', 'participant_handle', 'participant_profile_image',
            'status', 'priority', 'sentiment_label', 'unread_count',
            'last_message', 'last_message_at'
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-platform_created_at').first()
        if last_msg:
            return {
                'content': last_msg.content[:100],
                'direction': last_msg.direction
            }
        return None


class SocialConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for conversation details"""
    messages = SocialMessageSerializer(many=True, read_only=True)
    platform = serializers.CharField(source='social_account.platform')
    account_name = serializers.CharField(source='social_account.account_name')
    assigned_to_name = serializers.SerializerMethodField()
    linked_contact_name = serializers.SerializerMethodField()
    linked_lead_name = serializers.SerializerMethodField()

    class Meta:
        model = SocialConversation
        fields = [
            'id', 'platform', 'account_name', 'conversation_type', 'external_url',
            'participant_id', 'participant_name', 'participant_handle',
            'participant_profile_url', 'participant_profile_image',
            'participant_followers_count', 'linked_contact', 'linked_contact_name',
            'linked_lead', 'linked_lead_name', 'status', 'priority',
            'assigned_to', 'assigned_to_name', 'sentiment_score', 'sentiment_label',
            'suggested_response', 'response_tone', 'tags', 'labels',
            'message_count', 'unread_count', 'messages',
            'first_message_at', 'last_message_at', 'first_response_at', 'resolved_at'
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None

    def get_linked_contact_name(self, obj):
        if obj.linked_contact:
            return obj.linked_contact.full_name
        return None

    def get_linked_lead_name(self, obj):
        if obj.linked_lead:
            return f"{obj.linked_lead.first_name} {obj.linked_lead.last_name}"
        return None


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending a social message"""
    content = serializers.CharField()
    attachments = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=list
    )


class SocialMonitoringRuleSerializer(serializers.ModelSerializer):
    """Serializer for monitoring rules"""

    class Meta:
        model = SocialMonitoringRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'keywords', 'platforms',
            'exclude_keywords', 'actions', 'auto_assign_to', 'auto_response_template',
            'auto_tags', 'auto_priority', 'is_active', 'matches_count',
            'last_matched_at', 'created_at'
        ]
        read_only_fields = ['id', 'matches_count', 'last_matched_at', 'created_at']


class SocialPostSerializer(serializers.ModelSerializer):
    """Serializer for social posts"""
    platform_names = serializers.SerializerMethodField()

    class Meta:
        model = SocialPost
        fields = [
            'id', 'content', 'media_urls', 'social_accounts', 'platform_names',
            'status', 'scheduled_at', 'published_at', 'publish_results',
            'total_likes', 'total_shares', 'total_comments', 'total_reach',
            'created_at'
        ]
        read_only_fields = ['id', 'published_at', 'publish_results', 'created_at']

    def get_platform_names(self, obj):
        return [f"{acc.platform}: {acc.account_name}" for acc in obj.social_accounts.all()]


class SocialAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for social analytics"""

    class Meta:
        model = SocialAnalytics
        fields = [
            'id', 'date', 'followers_count', 'followers_gained', 'followers_lost',
            'impressions', 'reach', 'engagement_rate', 'posts_count',
            'likes_received', 'comments_received', 'shares_received',
            'messages_received', 'messages_sent', 'avg_response_time_minutes'
        ]


class BulkConversationActionSerializer(serializers.Serializer):
    """Serializer for bulk conversation actions"""
    conversation_ids = serializers.ListField(
        child=serializers.UUIDField()
    )
    action = serializers.ChoiceField(choices=[
        ('mark_read', 'Mark as Read'),
        ('mark_unread', 'Mark as Unread'),
        ('resolve', 'Resolve'),
        ('reopen', 'Reopen'),
        ('assign', 'Assign'),
        ('add_tag', 'Add Tag'),
        ('remove_tag', 'Remove Tag'),
        ('mark_spam', 'Mark as Spam'),
    ])
    value = serializers.CharField(required=False, allow_blank=True)
