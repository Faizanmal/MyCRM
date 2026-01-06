"""
Campaign Management Serializers
"""

from rest_framework import serializers

from .models import Campaign, CampaignClick, CampaignRecipient, CampaignSegment, EmailTemplate


class CampaignSegmentSerializer(serializers.ModelSerializer):
    """Serializer for Campaign Segments"""

    class Meta:
        model = CampaignSegment
        fields = [
            'id', 'name', 'description', 'filters', 'contact_count',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'contact_count', 'created_at', 'updated_at']


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for Campaigns"""

    segment_details = CampaignSegmentSerializer(source='segment', read_only=True)
    open_rate = serializers.FloatField(read_only=True)
    click_rate = serializers.FloatField(read_only=True)
    bounce_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'description', 'campaign_type', 'status',
            'subject', 'content_html', 'content_text',
            'scheduled_at', 'started_at', 'completed_at',
            'segment', 'segment_details',
            'enable_ab_test', 'ab_test_variants',
            'total_recipients', 'sent_count', 'delivered_count',
            'opened_count', 'clicked_count', 'bounced_count', 'unsubscribed_count',
            'open_rate', 'click_rate', 'bounce_rate',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'started_at', 'completed_at',
            'total_recipients', 'sent_count', 'delivered_count',
            'opened_count', 'clicked_count', 'bounced_count', 'unsubscribed_count',
            'created_at', 'updated_at'
        ]

    def validate_scheduled_at(self, value):
        """Ensure scheduled time is in the future"""
        from django.utils import timezone
        if value and value < timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        return value


class CampaignRecipientSerializer(serializers.ModelSerializer):
    """Serializer for Campaign Recipients"""

    class Meta:
        model = CampaignRecipient
        fields = [
            'id', 'campaign', 'contact', 'lead', 'email', 'status', 'variant',
            'sent_at', 'delivered_at', 'opened_at', 'first_clicked_at',
            'bounced_at', 'unsubscribed_at',
            'open_count', 'click_count', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CampaignClickSerializer(serializers.ModelSerializer):
    """Serializer for Campaign Clicks"""

    class Meta:
        model = CampaignClick
        fields = [
            'id', 'recipient', 'url', 'clicked_at',
            'ip_address', 'user_agent'
        ]
        read_only_fields = ['id', 'clicked_at']


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for Email Templates"""

    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'description', 'category',
            'subject', 'content_html', 'content_text',
            'variables', 'thumbnail', 'is_active',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CampaignStatsSerializer(serializers.Serializer):
    """Campaign statistics summary"""

    total_campaigns = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    total_sent = serializers.IntegerField()
    average_open_rate = serializers.FloatField()
    average_click_rate = serializers.FloatField()
    top_performing = CampaignSerializer(many=True)
