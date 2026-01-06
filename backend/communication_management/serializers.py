from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Communication, CommunicationLog, CommunicationRule, EmailCampaign, EmailTemplate

User = get_user_model()


class EmailTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'subject', 'template_type', 'content', 'html_content',
            'variables', 'usage_count', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'usage_count', 'created_at', 'updated_at']


class EmailCampaignSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'name', 'description', 'template', 'template_name', 'scheduled_date',
            'status', 'recipient_list', 'recipient_count', 'sent_count', 'delivered_count',
            'opened_count', 'clicked_count', 'unsubscribed_count', 'bounced_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at', 'sent_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'recipient_count', 'sent_count', 'delivered_count',
            'opened_count', 'clicked_count', 'unsubscribed_count', 'bounced_count',
            'created_at', 'updated_at', 'sent_at'
        ]


class CommunicationRuleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = CommunicationRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'trigger', 'conditions',
            'actions', 'delay_minutes', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class CommunicationLogSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='rule.name', read_only=True)

    class Meta:
        model = CommunicationLog
        fields = [
            'id', 'rule', 'rule_name', 'communication', 'executed_at',
            'status', 'error_message'
        ]
        read_only_fields = ['id', 'executed_at']


class CommunicationSerializer(serializers.ModelSerializer):
    from_user_name = serializers.CharField(source='from_user.get_full_name', read_only=True)
    to_user_name = serializers.CharField(source='to_user.get_full_name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    lead_name = serializers.CharField(source='lead.full_name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = Communication
        fields = [
            'id', 'subject', 'communication_type', 'direction', 'content', 'summary',
            'from_user', 'from_user_name', 'to_user', 'to_user_name',
            'from_email', 'to_email', 'from_phone', 'to_phone',
            'contact', 'contact_name', 'lead', 'lead_name', 'opportunity', 'opportunity_name',
            'task', 'task_title', 'email_id', 'is_read', 'read_at', 'is_replied',
            'replied_at', 'call_duration', 'call_recording_url', 'tags', 'attachments',
            'custom_fields', 'communication_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommunicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Communication
        fields = [
            'subject', 'communication_type', 'direction', 'content', 'summary',
            'from_user', 'to_user', 'from_email', 'to_email', 'from_phone', 'to_phone',
            'contact', 'lead', 'opportunity', 'task', 'email_id', 'call_duration',
            'call_recording_url', 'tags', 'attachments', 'custom_fields', 'communication_date'
        ]

    def create(self, validated_data):
        # Set from_user if not provided
        if not validated_data.get('from_user'):
            validated_data['from_user'] = self.context['request'].user
        return super().create(validated_data)


class CommunicationBulkUpdateSerializer(serializers.Serializer):
    communication_ids = serializers.ListField(child=serializers.IntegerField())
    updates = serializers.DictField()

    def validate_communication_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one communication ID is required.")
        return value
