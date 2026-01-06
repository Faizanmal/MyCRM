from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Lead, LeadActivity, LeadAssignmentRule, LeadConversion

User = get_user_model()


class LeadSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Lead
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'company_name', 'job_title', 'lead_source', 'status', 'priority',
            'assigned_to', 'assigned_to_name', 'owner', 'owner_name',
            'lead_score', 'estimated_value', 'probability', 'last_contact_date',
            'next_follow_up', 'notes', 'tags', 'custom_fields',
            'created_at', 'updated_at', 'converted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'converted_at']


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'company_name',
            'job_title', 'lead_source', 'status', 'priority', 'assigned_to',
            'lead_score', 'estimated_value', 'probability', 'last_contact_date',
            'next_follow_up', 'notes', 'tags', 'custom_fields'
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class LeadActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = LeadActivity
        fields = [
            'id', 'lead', 'activity_type', 'subject', 'description',
            'user', 'user_name', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class LeadAssignmentRuleSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = LeadAssignmentRule
        fields = [
            'id', 'name', 'description', 'criteria', 'assigned_to',
            'assigned_to_name', 'is_active', 'priority', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class LeadConversionSerializer(serializers.ModelSerializer):
    converted_by_name = serializers.CharField(source='converted_by.get_full_name', read_only=True)

    class Meta:
        model = LeadConversion
        fields = [
            'id', 'lead', 'opportunity', 'converted_by', 'converted_by_name',
            'conversion_value', 'conversion_notes', 'converted_at'
        ]
        read_only_fields = ['id', 'converted_by', 'converted_at']


class LeadBulkUpdateSerializer(serializers.Serializer):
    lead_ids = serializers.ListField(child=serializers.IntegerField())
    updates = serializers.DictField()

    def validate_lead_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one lead ID is required.")
        return value
