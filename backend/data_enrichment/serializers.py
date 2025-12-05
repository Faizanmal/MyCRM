"""
Data Enrichment Serializers
API serializers for data enrichment
"""

from rest_framework import serializers
from .models import (
    EnrichmentProvider, EnrichmentProfile, CompanyEnrichment,
    TechnographicData, IntentSignal, NewsAlert, EmailVerification,
    EnrichmentJob, EnrichmentRule, SocialProfile, FinancialData,
    EnrichmentActivity
)


class EnrichmentProviderSerializer(serializers.ModelSerializer):
    """Serializer for enrichment providers"""
    
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = EnrichmentProvider
        fields = [
            'id', 'name', 'provider_type', 'is_active', 'is_configured',
            'can_enrich_person', 'can_enrich_company', 'can_find_email',
            'can_verify_email', 'can_get_technographics', 'can_get_intent',
            'requests_per_minute', 'requests_per_day', 'daily_requests_used',
            'total_requests', 'successful_requests', 'average_response_time',
            'success_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_requests', 'successful_requests', 'daily_requests_used',
            'average_response_time', 'created_at', 'updated_at'
        ]
    
    def get_success_rate(self, obj):
        if obj.total_requests == 0:
            return 0
        return round(obj.successful_requests / obj.total_requests * 100, 1)


class SocialProfileSerializer(serializers.ModelSerializer):
    """Serializer for social profiles"""
    
    class Meta:
        model = SocialProfile
        fields = [
            'id', 'platform', 'profile_url', 'username', 'display_name',
            'headline', 'bio', 'avatar_url', 'followers_count', 'following_count',
            'connections_count', 'posts_count', 'last_active', 'recent_posts',
            'interests', 'engagement_rate', 'last_synced_at'
        ]


class EnrichmentProfileSerializer(serializers.ModelSerializer):
    """Serializer for enrichment profiles"""
    
    social_profiles = SocialProfileSerializer(many=True, read_only=True)
    
    class Meta:
        model = EnrichmentProfile
        fields = [
            'id', 'contact', 'lead', 'email', 'domain', 'linkedin_url',
            'status', 'enrichment_score', 'first_name', 'last_name', 'full_name',
            'title', 'seniority', 'department', 'phone', 'mobile_phone',
            'work_email', 'personal_email', 'city', 'state', 'country', 'timezone',
            'linkedin_profile', 'twitter_handle', 'github_username',
            'employment_history', 'education', 'skills',
            'last_enriched_at', 'enrichment_sources', 'data_freshness_score',
            'social_profiles', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'enrichment_score', 'last_enriched_at',
            'enrichment_sources', 'data_freshness_score', 'created_at', 'updated_at'
        ]


class TechnographicDataSerializer(serializers.ModelSerializer):
    """Serializer for technographic data"""
    
    class Meta:
        model = TechnographicData
        fields = [
            'id', 'company', 'technology_name', 'category', 'version',
            'first_detected', 'last_detected', 'confidence_score',
            'detection_method', 'is_competitor_product', 'competitor_of'
        ]


class FinancialDataSerializer(serializers.ModelSerializer):
    """Serializer for financial data"""
    
    class Meta:
        model = FinancialData
        fields = [
            'id', 'company', 'annual_revenue', 'revenue_currency', 'revenue_year',
            'revenue_growth_rate', 'total_funding', 'last_funding_round',
            'last_funding_amount', 'last_funding_date', 'investors',
            'estimated_valuation', 'valuation_date', 'market_cap',
            'stock_symbol', 'stock_exchange', 'credit_rating', 'risk_score',
            'last_updated_at', 'data_source'
        ]


class CompanyEnrichmentSerializer(serializers.ModelSerializer):
    """Serializer for company enrichments"""
    
    technographics = TechnographicDataSerializer(many=True, read_only=True)
    financial_data = FinancialDataSerializer(read_only=True)
    
    class Meta:
        model = CompanyEnrichment
        fields = [
            'id', 'domain', 'name', 'legal_name', 'description', 'founded_year',
            'industry', 'sub_industry', 'industry_codes', 'sector',
            'employee_count', 'employee_range', 'annual_revenue', 'revenue_range',
            'funding_total', 'funding_rounds', 'headquarters_address',
            'headquarters_city', 'headquarters_state', 'headquarters_country',
            'headquarters_postal_code', 'office_locations', 'phone', 'email_patterns',
            'website', 'linkedin_url', 'twitter_url', 'facebook_url', 'crunchbase_url',
            'logo_url', 'brand_colors', 'ceo_name', 'key_people',
            'technologies', 'tech_categories', 'alexa_rank', 'monthly_visits',
            'traffic_rank', 'enrichment_score', 'last_enriched_at',
            'enrichment_sources', 'technographics', 'financial_data',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'enrichment_score', 'last_enriched_at', 'enrichment_sources',
            'created_at', 'updated_at'
        ]


class IntentSignalSerializer(serializers.ModelSerializer):
    """Serializer for intent signals"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = IntentSignal
        fields = [
            'id', 'company', 'company_name', 'enrichment_profile',
            'intent_type', 'topic', 'topic_category', 'strength', 'score',
            'description', 'source', 'source_url', 'detected_at', 'expires_at',
            'was_actioned', 'actioned_by', 'actioned_at'
        ]
        read_only_fields = ['id', 'detected_at']


class NewsAlertSerializer(serializers.ModelSerializer):
    """Serializer for news alerts"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = NewsAlert
        fields = [
            'id', 'company', 'company_name', 'alert_type', 'title', 'summary',
            'full_content', 'source_name', 'source_url', 'published_at',
            'sentiment', 'relevance_score', 'people_mentioned', 'companies_mentioned',
            'amounts_mentioned', 'is_sales_trigger', 'trigger_reason',
            'recommended_action', 'is_read', 'read_by', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmailVerificationSerializer(serializers.ModelSerializer):
    """Serializer for email verifications"""
    
    class Meta:
        model = EmailVerification
        fields = [
            'id', 'email', 'status', 'is_deliverable', 'is_smtp_valid',
            'is_free_email', 'is_role_email', 'is_disposable', 'is_catch_all',
            'domain', 'mx_records', 'has_mx_records', 'quality_score',
            'verified_at', 'verification_provider'
        ]


class EnrichmentJobSerializer(serializers.ModelSerializer):
    """Serializer for enrichment jobs"""
    
    initiated_by_name = serializers.CharField(source='initiated_by.get_full_name', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = EnrichmentJob
        fields = [
            'id', 'job_type', 'status', 'total_records', 'processed_records',
            'successful_records', 'failed_records', 'progress_percentage',
            'started_at', 'completed_at', 'initiated_by', 'initiated_by_name',
            'enrichment_types', 'providers_used', 'results_summary', 'error_log',
            'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'processed_records', 'successful_records',
            'failed_records', 'started_at', 'completed_at', 'results_summary',
            'error_log', 'created_at'
        ]
    
    def get_progress_percentage(self, obj):
        if obj.total_records == 0:
            return 0
        return round(obj.processed_records / obj.total_records * 100, 1)


class EnrichmentRuleSerializer(serializers.ModelSerializer):
    """Serializer for enrichment rules"""
    
    class Meta:
        model = EnrichmentRule
        fields = [
            'id', 'name', 'description', 'trigger_type', 'conditions',
            'enrich_person', 'enrich_company', 'verify_email',
            'get_technographics', 'get_intent', 'get_news',
            'preferred_providers', 'is_active', 'times_triggered',
            'last_triggered_at', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'times_triggered', 'last_triggered_at', 'created_at', 'updated_at'
        ]


class EnrichmentActivitySerializer(serializers.ModelSerializer):
    """Serializer for enrichment activities"""
    
    profile_email = serializers.CharField(source='enrichment_profile.email', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = EnrichmentActivity
        fields = [
            'id', 'activity_type', 'enrichment_profile', 'profile_email',
            'company', 'company_name', 'provider', 'success', 'error_message',
            'fields_enriched', 'data_returned', 'response_time_ms',
            'api_credits_used', 'created_at'
        ]


# Request/Response Serializers

class EnrichContactRequestSerializer(serializers.Serializer):
    """Request serializer for enriching a contact"""
    
    email = serializers.EmailField()
    contact_id = serializers.UUIDField(required=False)
    lead_id = serializers.UUIDField(required=False)
    enrich_company = serializers.BooleanField(default=True)
    verify_email = serializers.BooleanField(default=True)
    get_social = serializers.BooleanField(default=True)


class EnrichCompanyRequestSerializer(serializers.Serializer):
    """Request serializer for enriching a company"""
    
    domain = serializers.CharField(max_length=255)
    get_technographics = serializers.BooleanField(default=True)
    get_financials = serializers.BooleanField(default=False)
    get_news = serializers.BooleanField(default=True)


class BulkEnrichRequestSerializer(serializers.Serializer):
    """Request serializer for bulk enrichment"""
    
    emails = serializers.ListField(
        child=serializers.EmailField(),
        max_length=1000
    )
    enrichment_types = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'person', 'company', 'email_verify', 'technographics', 'intent'
        ]),
        default=['person', 'company', 'email_verify']
    )


class VerifyEmailRequestSerializer(serializers.Serializer):
    """Request serializer for email verification"""
    
    email = serializers.EmailField()


class FetchNewsRequestSerializer(serializers.Serializer):
    """Request serializer for fetching company news"""
    
    domain = serializers.CharField(max_length=255)
    days_back = serializers.IntegerField(default=30, min_value=1, max_value=365)


class GetIntentSignalsRequestSerializer(serializers.Serializer):
    """Request serializer for getting intent signals"""
    
    domain = serializers.CharField(max_length=255)
    topics = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False
    )


class EnrichmentStatsResponseSerializer(serializers.Serializer):
    """Response serializer for enrichment stats"""
    
    total_profiles = serializers.IntegerField()
    enriched_profiles = serializers.IntegerField()
    enrichment_rate = serializers.FloatField()
    total_companies = serializers.IntegerField()
    verified_emails = serializers.IntegerField()
    recent_intent_signals = serializers.IntegerField()
    recent_sales_triggers = serializers.IntegerField()


class ProviderStatsSerializer(serializers.Serializer):
    """Response serializer for provider stats"""
    
    provider = serializers.CharField()
    provider_type = serializers.CharField()
    total_requests = serializers.IntegerField()
    successful_requests = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_response_time = serializers.FloatField()
    daily_usage = serializers.IntegerField()
    daily_limit = serializers.IntegerField()
