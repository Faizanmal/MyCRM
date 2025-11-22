from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    ConsentType, UserConsent, DataExportRequest, DataDeletionRequest,
    DataProcessingActivity, DataBreachIncident, DataAccessLog,
    PrivacyNotice, UserPrivacyPreference
)


class ConsentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentType
        fields = [
            'id', 'name', 'description', 'category', 'is_required',
            'version', 'legal_basis', 'retention_period_days', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserConsentSerializer(serializers.ModelSerializer):
    consent_type_name = serializers.CharField(source='consent_type.name', read_only=True)
    consent_category = serializers.CharField(source='consent_type.category', read_only=True)
    user_name = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = UserConsent
        fields = [
            'id', 'user', 'user_name', 'consent_type', 'consent_type_name',
            'consent_category', 'is_granted', 'consent_date', 'expiry_date',
            'ip_address', 'user_agent', 'consent_method', 'withdrawn_at',
            'withdrawal_reason', 'version', 'metadata', 'is_active'
        ]
        read_only_fields = ['consent_date', 'user']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_is_active(self, obj):
        return obj.is_granted and not obj.withdrawn_at


class UserConsentListSerializer(serializers.ModelSerializer):
    consent_type_name = serializers.CharField(source='consent_type.name', read_only=True)
    
    class Meta:
        model = UserConsent
        fields = ['id', 'consent_type_name', 'is_granted', 'consent_date', 'withdrawn_at']


class DataExportRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DataExportRequest
        fields = [
            'id', 'user', 'user_name', 'status', 'status_display', 'request_type',
            'data_categories', 'format', 'file_url', 'file_size_bytes',
            'expires_at', 'requested_at', 'completed_at', 'error_message', 'notes'
        ]
        read_only_fields = ['user', 'requested_at', 'completed_at', 'file_url', 'file_size_bytes']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class DataDeletionRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = DataDeletionRequest
        fields = [
            'id', 'user', 'user_name', 'status', 'status_display', 'deletion_type',
            'data_categories', 'reason', 'requested_at', 'reviewed_at',
            'reviewed_by', 'reviewed_by_name', 'completed_at', 'rejection_reason',
            'backup_created', 'backup_location', 'notes'
        ]
        read_only_fields = ['user', 'requested_at', 'reviewed_at', 'completed_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}".strip() or obj.reviewed_by.username
        return None


class DataProcessingActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DataProcessingActivity
        fields = [
            'id', 'name', 'description', 'purpose', 'legal_basis',
            'data_categories', 'data_subjects', 'recipients',
            'third_country_transfers', 'third_countries', 'safeguards',
            'retention_period', 'security_measures', 'data_controller',
            'data_processor', 'dpo_contact', 'is_active', 'created_at',
            'updated_at', 'last_reviewed'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DataBreachIncidentSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reported_by_name = serializers.SerializerMethodField()
    days_since_discovery = serializers.SerializerMethodField()

    class Meta:
        model = DataBreachIncident
        fields = [
            'id', 'incident_id', 'title', 'description', 'severity', 'severity_display',
            'breach_type', 'discovered_at', 'reported_at', 'reported_by', 'reported_by_name',
            'affected_users_count', 'data_categories_affected', 'breach_cause',
            'containment_measures', 'remediation_plan', 'status', 'status_display',
            'authority_notified', 'authority_notification_date', 'users_notified',
            'user_notification_date', 'notification_required', 'risk_assessment',
            'lessons_learned', 'closed_at', 'days_since_discovery'
        ]
        read_only_fields = ['reported_at', 'days_since_discovery']

    def get_reported_by_name(self, obj):
        if obj.reported_by:
            return f"{obj.reported_by.first_name} {obj.reported_by.last_name}".strip() or obj.reported_by.username
        return None

    def get_days_since_discovery(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.discovered_at
        return delta.days


class DataBreachIncidentListSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = DataBreachIncident
        fields = [
            'id', 'incident_id', 'title', 'severity', 'severity_display',
            'status', 'status_display', 'discovered_at', 'affected_users_count',
            'authority_notified', 'users_notified'
        ]


class DataAccessLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    accessed_by_name = serializers.SerializerMethodField()
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = DataAccessLog
        fields = [
            'id', 'user', 'user_name', 'accessed_by', 'accessed_by_name',
            'content_type', 'content_type_name', 'object_id', 'access_type',
            'data_fields', 'purpose', 'ip_address', 'user_agent',
            'accessed_at', 'metadata'
        ]
        read_only_fields = ['accessed_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_accessed_by_name(self, obj):
        return f"{obj.accessed_by.first_name} {obj.accessed_by.last_name}".strip() or obj.accessed_by.username


class PrivacyNoticeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PrivacyNotice
        fields = [
            'id', 'title', 'content', 'version', 'language', 'effective_date',
            'notice_type', 'is_current', 'requires_acceptance', 'created_at',
            'created_by', 'created_by_name'
        ]
        read_only_fields = ['created_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None


class UserPrivacyPreferenceSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    accepted_notices = PrivacyNoticeSerializer(source='accepted_privacy_notices', many=True, read_only=True)

    class Meta:
        model = UserPrivacyPreference
        fields = [
            'id', 'user', 'user_name', 'allow_data_processing', 'allow_marketing_emails',
            'allow_analytics', 'allow_third_party_sharing', 'allow_profiling',
            'data_retention_preference', 'contact_preferences', 'accepted_notices',
            'updated_at'
        ]
        read_only_fields = ['user', 'updated_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
