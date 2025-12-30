"""
Integration Marketplace - Serializers
"""

from rest_framework import serializers
from .marketplace_models import (
    MarketplaceApp, AppInstallation, AppReview,
    CustomWebhook, WebhookEvent, WebhookDeliveryLog,
    APIRateLimit, APIUsageLog, APIUsageMetrics
)


class MarketplaceAppListSerializer(serializers.ModelSerializer):
    """List serializer for marketplace apps"""
    
    class Meta:
        model = MarketplaceApp
        fields = [
            'id', 'name', 'slug', 'tagline', 'category', 'tags',
            'developer_name', 'icon', 'pricing_model', 'price_monthly',
            'install_count', 'rating_avg', 'rating_count', 'status'
        ]


class MarketplaceAppDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for marketplace apps"""
    
    is_installed = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketplaceApp
        fields = [
            'id', 'name', 'slug', 'tagline', 'description', 'category',
            'tags', 'developer_name', 'developer_email', 'developer_website',
            'support_url', 'documentation_url', 'icon', 'banner', 'screenshots',
            'pricing_model', 'price_monthly', 'price_yearly',
            'required_permissions', 'data_access', 'version',
            'install_count', 'rating_avg', 'rating_count',
            'is_installed', 'published_at', 'created_at', 'updated_at'
        ]
    
    def get_is_installed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return AppInstallation.objects.filter(
                app=obj, user=request.user, status='active'
            ).exists()
        return False


class MarketplaceAppCreateSerializer(serializers.ModelSerializer):
    """Create serializer for marketplace apps"""
    
    class Meta:
        model = MarketplaceApp
        fields = [
            'name', 'slug', 'tagline', 'description', 'category', 'tags',
            'developer_name', 'developer_email', 'developer_website',
            'support_url', 'documentation_url', 'icon', 'banner', 'screenshots',
            'pricing_model', 'price_monthly', 'price_yearly',
            'oauth_client_id', 'oauth_authorize_url', 'oauth_token_url',
            'oauth_scopes', 'api_base_url', 'webhook_url',
            'required_permissions', 'data_access'
        ]


class AppInstallationSerializer(serializers.ModelSerializer):
    """Serializer for app installations"""
    
    app_name = serializers.CharField(source='app.name', read_only=True)
    app_icon = serializers.ImageField(source='app.icon', read_only=True)
    
    class Meta:
        model = AppInstallation
        fields = [
            'id', 'app', 'app_name', 'app_icon', 'status', 'config',
            'permissions_granted', 'last_used', 'api_calls_count',
            'installed_at', 'uninstalled_at'
        ]
        read_only_fields = ['id', 'installed_at', 'uninstalled_at']


class AppReviewSerializer(serializers.ModelSerializer):
    """Serializer for app reviews"""
    
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AppReview
        fields = [
            'id', 'app', 'user_name', 'rating', 'title', 'review',
            'helpful_count', 'developer_response', 'developer_responded_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email.split('@')[0]


class CreateReviewSerializer(serializers.Serializer):
    """Serializer for creating reviews"""
    
    rating = serializers.IntegerField(min_value=1, max_value=5)
    title = serializers.CharField(max_length=200)
    review = serializers.CharField()


class CustomWebhookSerializer(serializers.ModelSerializer):
    """Serializer for custom webhooks"""
    
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomWebhook
        fields = [
            'id', 'name', 'description', 'url', 'method', 'events',
            'auth_type', 'custom_headers', 'payload_template',
            'include_full_payload', 'conditions', 'rate_limit_per_minute',
            'retry_enabled', 'max_retries', 'retry_delay_seconds',
            'is_active', 'is_verified', 'total_triggers',
            'successful_deliveries', 'failed_deliveries',
            'last_triggered', 'last_success', 'last_failure',
            'success_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_verified', 'total_triggers', 'successful_deliveries',
            'failed_deliveries', 'last_triggered', 'last_success',
            'last_failure', 'created_at', 'updated_at'
        ]
    
    def get_success_rate(self, obj):
        if obj.total_triggers == 0:
            return 100.0
        return round((obj.successful_deliveries / obj.total_triggers) * 100, 1)


class CreateWebhookSerializer(serializers.Serializer):
    """Serializer for creating webhooks"""
    
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, default='')
    url = serializers.URLField()
    method = serializers.ChoiceField(
        choices=['POST', 'GET', 'PUT', 'PATCH'],
        default='POST'
    )
    events = serializers.ListField(
        child=serializers.CharField(),
        min_length=1
    )
    auth_type = serializers.ChoiceField(
        choices=['none', 'basic', 'bearer', 'api_key', 'hmac'],
        default='none'
    )
    auth_config = serializers.DictField(required=False, default=dict)
    custom_headers = serializers.DictField(required=False, default=dict)
    payload_template = serializers.CharField(required=False, default='')
    conditions = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    retry_enabled = serializers.BooleanField(default=True)


class WebhookEventSerializer(serializers.ModelSerializer):
    """Serializer for webhook events"""
    
    class Meta:
        model = WebhookEvent
        fields = [
            'name', 'display_name', 'description', 'entity_type',
            'action', 'payload_schema', 'example_payload', 'is_active'
        ]


class WebhookDeliveryLogSerializer(serializers.ModelSerializer):
    """Serializer for webhook delivery logs"""
    
    webhook_name = serializers.CharField(source='webhook.name', read_only=True)
    
    class Meta:
        model = WebhookDeliveryLog
        fields = [
            'id', 'webhook', 'webhook_name', 'event', 'request_url',
            'request_method', 'request_headers', 'request_body',
            'response_status', 'response_headers', 'response_body',
            'status', 'error_message', 'attempt_number', 'duration_ms',
            'created_at'
        ]


class APIRateLimitSerializer(serializers.ModelSerializer):
    """Serializer for API rate limits"""
    
    usage_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = APIRateLimit
        fields = [
            'id', 'endpoint_pattern', 'requests_limit', 'period',
            'burst_limit', 'current_count', 'period_start', 'is_active',
            'is_exceeded', 'usage_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_count', 'period_start', 'is_exceeded', 'created_at', 'updated_at']
    
    def get_usage_percentage(self, obj):
        if obj.requests_limit == 0:
            return 0
        return round((obj.current_count / obj.requests_limit) * 100, 1)


class CreateRateLimitSerializer(serializers.Serializer):
    """Serializer for creating rate limits"""
    
    user_id = serializers.IntegerField(required=False)
    api_key = serializers.CharField(required=False)
    endpoint_pattern = serializers.CharField(default='*')
    requests_limit = serializers.IntegerField(min_value=1, default=1000)
    period = serializers.ChoiceField(
        choices=['second', 'minute', 'hour', 'day'],
        default='hour'
    )
    burst_limit = serializers.IntegerField(min_value=1, default=50)


class APIUsageLogSerializer(serializers.ModelSerializer):
    """Serializer for API usage logs"""
    
    class Meta:
        model = APIUsageLog
        fields = [
            'id', 'endpoint', 'method', 'status_code', 'response_time_ms',
            'ip_address', 'user_agent', 'rate_limit_remaining',
            'was_rate_limited', 'created_at'
        ]


class APIUsageMetricsSerializer(serializers.ModelSerializer):
    """Serializer for API usage metrics"""
    
    class Meta:
        model = APIUsageMetrics
        fields = [
            'id', 'period', 'period_start', 'period_end', 'total_requests',
            'successful_requests', 'failed_requests', 'rate_limited_requests',
            'avg_response_time_ms', 'max_response_time_ms', 'min_response_time_ms',
            'endpoint_breakdown', 'status_code_breakdown', 'calculated_at'
        ]
