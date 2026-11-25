from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Account, Contact, ContactActivity, ContactGroup, ContactImport, MergeAuditLog

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name() or f"{obj.first_name} {obj.last_name}".strip() or obj.username


class AccountSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    contacts_count = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            'id', 'name', 'domain', 'industry', 'company_size', 'annual_revenue',
            'founded_year', 'description', 'logo_url', 'website', 'linkedin_url',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'phone', 'employee_count', 'account_type', 'tier', 'health_score',
            'owner', 'owner_name', 'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'is_active', 'is_merged', 'merged_into', 'custom_fields', 'tags',
            'contacts_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_merged', 'merged_into', 'created_at', 'updated_at', 'created_by']

    def get_contacts_count(self, obj):
        return obj.contacts.filter(is_merged=False).count()


class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'domain', 'industry', 'company_size', 'annual_revenue',
            'founded_year', 'description', 'logo_url', 'website', 'linkedin_url',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'phone', 'employee_count', 'account_type', 'tier', 'health_score',
            'owner', 'assigned_to', 'is_active', 'custom_fields', 'tags'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
            if 'owner' not in validated_data and 'assigned_to' not in validated_data:
                validated_data['owner'] = request.user
                validated_data['assigned_to'] = request.user
            org = getattr(request, 'organization', None)
            if org:
                validated_data['organization'] = org
        return super().create(validated_data)


class ContactActivitySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ContactActivity
        fields = [
            'id', 'contact', 'activity_type', 'content', 'subject', 'duration',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'contact', 'created_by', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class ContactSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    full_name = serializers.ReadOnlyField()
    company = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'salutation', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'mobile',
            'account', 'account_name', 'company', 'company_name', 'job_title', 'department',
            'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country',
            'contact_type', 'lifecycle_stage', 'source', 'assigned_to', 'assigned_to_name',
            'owner', 'owner_name', 'status', 'score', 'is_merged', 'merged_into',
            'website', 'linkedin', 'twitter', 'notes', 'tags', 'custom_fields',
            'created_at', 'updated_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['id', 'is_merged', 'merged_into', 'created_at', 'updated_at', 'created_by']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['company'] = instance.company
        return ret


class ContactCreateSerializer(serializers.ModelSerializer):
    company = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'salutation', 'first_name', 'last_name', 'email', 'phone', 'mobile',
            'account', 'company', 'company_name', 'job_title', 'department',
            'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country',
            'contact_type', 'lifecycle_stage', 'source', 'assigned_to', 'owner',
            'status', 'score', 'website', 'linkedin', 'twitter',
            'notes', 'tags', 'custom_fields'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        company_val = validated_data.pop('company', None)
        if company_val and 'company_name' not in validated_data:
            validated_data['company_name'] = company_val

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
            if 'owner' not in validated_data and 'assigned_to' not in validated_data:
                validated_data['owner'] = request.user
                validated_data['assigned_to'] = request.user
            org = getattr(request, 'organization', None)
            if org:
                validated_data['organization'] = org
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
            'id', 'file_name', 'file_path', 'resource_type', 'status', 'total_records',
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


class MergeEntitySerializer(serializers.Serializer):
    primary_id = serializers.IntegerField(required=True)
    secondary_id = serializers.IntegerField(required=True)
    field_choices = serializers.DictField(required=False, default=dict)

    def validate(self, attrs):
        if attrs['primary_id'] == attrs['secondary_id']:
            raise serializers.ValidationError("primary_id and secondary_id must be different.")
        return attrs


class UnmergeEntitySerializer(serializers.Serializer):
    merge_log_id = serializers.IntegerField(required=False)
    audit_log_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if not attrs.get('merge_log_id') and not attrs.get('audit_log_id'):
            raise serializers.ValidationError("Either merge_log_id or audit_log_id is required.")
        return attrs


class MergeAuditLogSerializer(serializers.ModelSerializer):
    merged_by_name = serializers.CharField(source='merged_by.get_full_name', read_only=True)
    reverted_by_name = serializers.CharField(source='reverted_by.get_full_name', read_only=True)

    class Meta:
        model = MergeAuditLog
        fields = [
            'id', 'entity_type', 'primary_id', 'secondary_id', 'secondary_snapshot',
            'repointed_relations', 'merged_by', 'merged_by_name',
            'is_reverted', 'reverted_by', 'reverted_by_name', 'reverted_at', 'created_at'
        ]
        read_only_fields = fields
