"""
Social Selling Serializers
"""

from rest_framework import serializers

from .models import (
    EngagementAnalytics,
    LinkedInIntegration,
    ProspectInSequence,
    SocialEngagement,
    SocialInsight,
    SocialPost,
    SocialProfile,
    SocialSellingSequence,
    SocialSellingStep,
)


class SocialProfileSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model = SocialProfile
        fields = '__all__'
        read_only_fields = ['last_synced']


class SocialPostSerializer(serializers.ModelSerializer):
    profile_name = serializers.CharField(source='profile.contact.full_name', read_only=True)

    class Meta:
        model = SocialPost
        fields = '__all__'


class SocialEngagementSerializer(serializers.ModelSerializer):
    engagement_type_display = serializers.CharField(source='get_engagement_type_display', read_only=True)
    profile_name = serializers.CharField(source='profile.contact.full_name', read_only=True)

    class Meta:
        model = SocialEngagement
        fields = '__all__'
        read_only_fields = ['user', 'completed_at']


class LinkedInIntegrationSerializer(serializers.ModelSerializer):
    is_connected = serializers.SerializerMethodField()

    class Meta:
        model = LinkedInIntegration
        fields = [
            'id', 'linkedin_id', 'profile_url', 'auto_sync_connections',
            'daily_engagement_limit', 'engagement_hours_start', 'engagement_hours_end',
            'is_active', 'is_connected', 'created_at'
        ]
        read_only_fields = ['linkedin_id', 'profile_url']

    def get_is_connected(self, obj):
        return obj.is_token_valid()


class SocialSellingStepSerializer(serializers.ModelSerializer):
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)

    class Meta:
        model = SocialSellingStep
        fields = '__all__'


class SocialSellingSequenceSerializer(serializers.ModelSerializer):
    steps = SocialSellingStepSerializer(many=True, read_only=True)
    prospects_count = serializers.IntegerField(source='prospects.count', read_only=True)
    active_prospects_count = serializers.SerializerMethodField()

    class Meta:
        model = SocialSellingSequence
        fields = '__all__'
        read_only_fields = ['user']

    def get_active_prospects_count(self, obj):
        return obj.prospects.filter(status='active').count()


class ProspectInSequenceSerializer(serializers.ModelSerializer):
    sequence_name = serializers.CharField(source='sequence.name', read_only=True)
    contact_name = serializers.CharField(source='profile.contact.full_name', read_only=True)

    class Meta:
        model = ProspectInSequence
        fields = '__all__'


class SocialInsightSerializer(serializers.ModelSerializer):
    insight_type_display = serializers.CharField(source='get_insight_type_display', read_only=True)
    contact_name = serializers.CharField(source='profile.contact.full_name', read_only=True)

    class Meta:
        model = SocialInsight
        fields = '__all__'


class EngagementAnalyticsSerializer(serializers.ModelSerializer):
    response_rate = serializers.SerializerMethodField()
    connection_rate = serializers.SerializerMethodField()

    class Meta:
        model = EngagementAnalytics
        fields = '__all__'

    def get_response_rate(self, obj):
        if obj.messages_sent > 0:
            return round((obj.messages_replied / obj.messages_sent) * 100, 1)
        return 0

    def get_connection_rate(self, obj):
        if obj.connections_sent > 0:
            return round((obj.connections_accepted / obj.connections_sent) * 100, 1)
        return 0


# Create/Update Serializers
class CreateSocialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialProfile
        fields = ['contact', 'platform', 'profile_url', 'username']


class BulkEngagementSerializer(serializers.Serializer):
    """Bulk schedule engagements"""
    profile_ids = serializers.ListField(child=serializers.IntegerField())
    engagement_type = serializers.ChoiceField(choices=SocialEngagement.ENGAGEMENT_TYPES)
    content = serializers.CharField(required=False, allow_blank=True)
    use_ai_personalization = serializers.BooleanField(default=True)
    scheduled_for = serializers.DateTimeField(required=False)


class EnrollInSequenceSerializer(serializers.Serializer):
    """Enroll prospects in sequence"""
    profile_ids = serializers.ListField(child=serializers.IntegerField())
    sequence_id = serializers.IntegerField()
