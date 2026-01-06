from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Contact, ContactGroup, ContactImport

User = get_user_model()


class ContactSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Contact
        fields = [
            'id', 'salutation', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'mobile',
            'company_name', 'job_title', 'department', 'address_line_1', 'address_line_2',
            'city', 'state', 'postal_code', 'country', 'contact_type', 'source',
            'assigned_to', 'assigned_to_name', 'status', 'website', 'linkedin', 'twitter',
            'notes', 'tags', 'custom_fields', 'created_at', 'updated_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'salutation', 'first_name', 'last_name', 'email', 'phone', 'mobile',
            'company_name', 'job_title', 'department', 'address_line_1', 'address_line_2',
            'city', 'state', 'postal_code', 'country', 'contact_type', 'source',
            'assigned_to', 'status', 'website', 'linkedin', 'twitter',
            'notes', 'tags', 'custom_fields'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ContactGroupSerializer(serializers.ModelSerializer):
    contact_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ContactGroup
        fields = [
            'id', 'name', 'description', 'contacts', 'contact_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_contact_count(self, obj):
        return obj.contacts.count()


class ContactImportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ContactImport
        fields = [
            'id', 'file_name', 'file_path', 'status', 'total_records',
            'processed_records', 'failed_records', 'error_log',
            'created_by', 'created_by_name', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'completed_at']


class ContactBulkUpdateSerializer(serializers.Serializer):
    contact_ids = serializers.ListField(child=serializers.IntegerField())
    updates = serializers.DictField()

    def validate_contact_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one contact ID is required.")
        return value


class ContactExportSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=['csv', 'excel', 'pdf'], default='csv')
    fields = serializers.ListField(child=serializers.CharField(), required=False)
    filters = serializers.DictField(required=False)
    group_id = serializers.IntegerField(required=False)
