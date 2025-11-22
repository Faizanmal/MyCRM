from django.contrib import admin
from .models import (
    ConsentType, UserConsent, DataExportRequest, DataDeletionRequest,
    DataProcessingActivity, DataBreachIncident, DataAccessLog,
    PrivacyNotice, UserPrivacyPreference
)


@admin.register(ConsentType)
class ConsentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_required', 'legal_basis', 'version', 'is_active']
    list_filter = ['category', 'is_required', 'legal_basis', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ['user', 'consent_type', 'is_granted', 'consent_date', 'withdrawn_at']
    list_filter = ['is_granted', 'consent_type__category', 'consent_method', 'consent_date']
    search_fields = ['user__username', 'user__email', 'consent_type__name']
    autocomplete_fields = ['user', 'consent_type']
    readonly_fields = ['consent_date']
    date_hierarchy = 'consent_date'


@admin.register(DataExportRequest)
class DataExportRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'request_type', 'format', 'requested_at', 'completed_at']
    list_filter = ['status', 'request_type', 'format', 'requested_at']
    search_fields = ['user__username', 'user__email']
    autocomplete_fields = ['user']
    readonly_fields = ['requested_at', 'completed_at']
    date_hierarchy = 'requested_at'


@admin.register(DataDeletionRequest)
class DataDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'deletion_type', 'requested_at', 'reviewed_by', 'completed_at']
    list_filter = ['status', 'deletion_type', 'requested_at', 'backup_created']
    search_fields = ['user__username', 'user__email', 'reason']
    autocomplete_fields = ['user', 'reviewed_by']
    readonly_fields = ['requested_at', 'reviewed_at', 'completed_at']
    date_hierarchy = 'requested_at'


@admin.register(DataProcessingActivity)
class DataProcessingActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'legal_basis', 'third_country_transfers', 'is_active', 'last_reviewed']
    list_filter = ['legal_basis', 'third_country_transfers', 'is_active']
    search_fields = ['name', 'description', 'purpose']
    ordering = ['name']


@admin.register(DataBreachIncident)
class DataBreachIncidentAdmin(admin.ModelAdmin):
    list_display = [
        'incident_id', 'title', 'severity', 'status', 'discovered_at',
        'affected_users_count', 'authority_notified', 'users_notified'
    ]
    list_filter = [
        'severity', 'status', 'breach_type', 'authority_notified',
        'users_notified', 'notification_required', 'discovered_at'
    ]
    search_fields = ['incident_id', 'title', 'description']
    autocomplete_fields = ['reported_by', 'affected_users']
    readonly_fields = ['reported_at']
    date_hierarchy = 'discovered_at'
    filter_horizontal = ['affected_users']


@admin.register(DataAccessLog)
class DataAccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'accessed_by', 'content_type', 'object_id', 'access_type', 'accessed_at']
    list_filter = ['access_type', 'accessed_at', 'content_type']
    search_fields = ['user__username', 'accessed_by__username', 'purpose']
    autocomplete_fields = ['user', 'accessed_by']
    readonly_fields = ['accessed_at']
    date_hierarchy = 'accessed_at'


@admin.register(PrivacyNotice)
class PrivacyNoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'version', 'notice_type', 'language', 'effective_date', 'is_current']
    list_filter = ['notice_type', 'language', 'is_current', 'requires_acceptance']
    search_fields = ['title', 'content']
    autocomplete_fields = ['created_by']
    readonly_fields = ['created_at']
    date_hierarchy = 'effective_date'


@admin.register(UserPrivacyPreference)
class UserPrivacyPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'allow_data_processing', 'allow_marketing_emails',
        'allow_analytics', 'allow_third_party_sharing', 'updated_at'
    ]
    list_filter = [
        'allow_data_processing', 'allow_marketing_emails', 'allow_analytics',
        'allow_third_party_sharing', 'allow_profiling', 'data_retention_preference'
    ]
    search_fields = ['user__username', 'user__email']
    autocomplete_fields = ['user']
    readonly_fields = ['updated_at']
    filter_horizontal = ['accepted_privacy_notices']
