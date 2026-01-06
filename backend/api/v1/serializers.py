"""
Unified API V1 Serializers
Comprehensive serializers for all CRM resources
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from contact_management.models import Contact
from lead_management.models import Lead
from opportunity_management.models import Opportunity
from task_management.models import Task

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    """Brief user info for nested representations"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name() if hasattr(obj, 'get_full_name') else f"{obj.first_name} {obj.last_name}"


class LeadListSerializer(serializers.ModelSerializer):
    """Optimized serializer for lead lists"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'company_name',
            'lead_source', 'status', 'priority', 'lead_score', 'estimated_value',
            'assigned_to', 'assigned_to_name', 'owner_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LeadDetailSerializer(serializers.ModelSerializer):
    """Detailed lead serializer with all fields"""
    assigned_to_detail = UserBriefSerializer(source='assigned_to', read_only=True)
    owner_detail = UserBriefSerializer(source='owner', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'company_name', 'job_title', 'lead_source', 'status', 'priority',
            'assigned_to', 'assigned_to_detail', 'owner', 'owner_detail',
            'lead_score', 'estimated_value', 'probability',
            'last_contact_date', 'next_follow_up', 'notes', 'tags',
            'custom_fields', 'created_at', 'updated_at', 'converted_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'converted_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class ContactListSerializer(serializers.ModelSerializer):
    """Optimized serializer for contact lists"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'salutation', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'mobile', 'company_name', 'job_title',
            'contact_type', 'status', 'assigned_to', 'assigned_to_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']


class ContactDetailSerializer(serializers.ModelSerializer):
    """Detailed contact serializer with all fields"""
    assigned_to_detail = UserBriefSerializer(source='assigned_to', read_only=True)
    created_by_detail = UserBriefSerializer(source='created_by', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'salutation', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'mobile', 'company_name', 'job_title', 'department',
            'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country',
            'contact_type', 'source', 'status', 'assigned_to', 'assigned_to_detail',
            'website', 'linkedin', 'twitter', 'notes', 'tags', 'custom_fields',
            'created_at', 'updated_at', 'created_by', 'created_by_detail'
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class OpportunityListSerializer(serializers.ModelSerializer):
    """Optimized serializer for opportunity lists"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    weighted_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id', 'name', 'company_name', 'stage', 'amount', 'currency',
            'probability', 'weighted_amount', 'expected_close_date',
            'contact', 'contact_name', 'assigned_to', 'assigned_to_name',
            'owner_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'weighted_amount', 'created_at', 'updated_at']


class OpportunityDetailSerializer(serializers.ModelSerializer):
    """Detailed opportunity serializer with all fields"""
    assigned_to_detail = UserBriefSerializer(source='assigned_to', read_only=True)
    owner_detail = UserBriefSerializer(source='owner', read_only=True)
    contact_detail = ContactListSerializer(source='contact', read_only=True)
    weighted_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id', 'name', 'description', 'company_name', 'stage', 'probability',
            'amount', 'currency', 'weighted_amount', 'contact', 'contact_detail',
            'assigned_to', 'assigned_to_detail', 'owner', 'owner_detail',
            'expected_close_date', 'actual_close_date', 'last_activity_date',
            'notes', 'tags', 'custom_fields', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'weighted_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Optimized serializer for task lists"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'task_type', 'status', 'priority', 'due_date',
            'assigned_to', 'assigned_to_name', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed task serializer with all fields"""
    assigned_to_detail = UserBriefSerializer(source='assigned_to', read_only=True)
    created_by_detail = UserBriefSerializer(source='created_by', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'task_type', 'status', 'priority',
            'assigned_to', 'assigned_to_detail', 'created_by', 'created_by_detail',
            'due_date', 'completed_at', 'reminder_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


# Bulk operations serializers
class BulkOperationSerializer(serializers.Serializer):
    """Serializer for bulk operations"""
    ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    action = serializers.ChoiceField(choices=['delete', 'update', 'export'], required=True)
    data = serializers.JSONField(required=False)


class ImportMappingSerializer(serializers.Serializer):
    """Serializer for CSV import field mapping"""
    file = serializers.FileField(required=True)
    mapping = serializers.JSONField(required=True)
    update_existing = serializers.BooleanField(default=False)
    skip_errors = serializers.BooleanField(default=True)
