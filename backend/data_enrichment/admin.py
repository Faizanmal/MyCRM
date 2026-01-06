"""
Data Enrichment Admin Configuration
"""

from django.contrib import admin

from .models import (
    CompanyEnrichment,
    EmailVerification,
    EnrichmentActivity,
    EnrichmentJob,
    EnrichmentProfile,
    EnrichmentProvider,
    EnrichmentRule,
    FinancialData,
    IntentSignal,
    NewsAlert,
    SocialProfile,
    TechnographicData,
)


@admin.register(EnrichmentProvider)
class EnrichmentProviderAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'provider_type', 'is_active', 'is_configured',
        'total_requests', 'successful_requests', 'daily_requests_used'
    ]
    list_filter = ['is_active', 'is_configured', 'provider_type']
    search_fields = ['name']
    readonly_fields = [
        'total_requests', 'successful_requests', 'daily_requests_used',
        'average_response_time'
    ]


@admin.register(EnrichmentProfile)
class EnrichmentProfileAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'full_name', 'title', 'status', 'enrichment_score',
        'last_enriched_at'
    ]
    list_filter = ['status', 'seniority', 'country']
    search_fields = ['email', 'first_name', 'last_name', 'title']
    readonly_fields = [
        'enrichment_score', 'last_enriched_at', 'enrichment_sources',
        'created_at', 'updated_at'
    ]


@admin.register(CompanyEnrichment)
class CompanyEnrichmentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'domain', 'industry', 'employee_range',
        'enrichment_score', 'last_enriched_at'
    ]
    list_filter = ['industry', 'employee_range', 'headquarters_country']
    search_fields = ['name', 'domain']
    readonly_fields = [
        'enrichment_score', 'last_enriched_at', 'enrichment_sources',
        'created_at', 'updated_at'
    ]


@admin.register(TechnographicData)
class TechnographicDataAdmin(admin.ModelAdmin):
    list_display = [
        'company', 'technology_name', 'category', 'confidence_score',
        'first_detected', 'last_detected'
    ]
    list_filter = ['category', 'is_competitor_product']
    search_fields = ['technology_name', 'company__name']


@admin.register(IntentSignal)
class IntentSignalAdmin(admin.ModelAdmin):
    list_display = [
        'topic', 'intent_type', 'strength', 'score', 'company',
        'detected_at', 'was_actioned'
    ]
    list_filter = ['intent_type', 'strength', 'was_actioned']
    search_fields = ['topic', 'company__name']


@admin.register(NewsAlert)
class NewsAlertAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company', 'alert_type', 'sentiment',
        'is_sales_trigger', 'published_at', 'is_read'
    ]
    list_filter = ['alert_type', 'sentiment', 'is_sales_trigger', 'is_read']
    search_fields = ['title', 'company__name']


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'status', 'is_deliverable', 'quality_score',
        'verified_at'
    ]
    list_filter = ['status', 'is_free_email', 'is_role_email', 'is_disposable']
    search_fields = ['email', 'domain']


@admin.register(EnrichmentJob)
class EnrichmentJobAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'job_type', 'status', 'total_records', 'processed_records',
        'successful_records', 'failed_records', 'initiated_by', 'created_at'
    ]
    list_filter = ['job_type', 'status']
    readonly_fields = [
        'processed_records', 'successful_records', 'failed_records',
        'started_at', 'completed_at', 'results_summary', 'error_log'
    ]


@admin.register(EnrichmentRule)
class EnrichmentRuleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'trigger_type', 'is_active', 'times_triggered',
        'last_triggered_at'
    ]
    list_filter = ['trigger_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display = [
        'enrichment_profile', 'platform', 'username',
        'followers_count', 'last_synced_at'
    ]
    list_filter = ['platform']
    search_fields = ['username', 'enrichment_profile__email']


@admin.register(FinancialData)
class FinancialDataAdmin(admin.ModelAdmin):
    list_display = [
        'company', 'annual_revenue', 'total_funding',
        'estimated_valuation', 'last_updated_at'
    ]
    search_fields = ['company__name']


@admin.register(EnrichmentActivity)
class EnrichmentActivityAdmin(admin.ModelAdmin):
    list_display = [
        'activity_type', 'enrichment_profile', 'company',
        'success', 'response_time_ms', 'created_at'
    ]
    list_filter = ['activity_type', 'success']
    search_fields = ['enrichment_profile__email', 'company__name']
    readonly_fields = ['created_at']
