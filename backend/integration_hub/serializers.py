"""
Integration Hub Serializers
"""

from rest_framework import serializers
from .models import Webhook, WebhookDelivery, ThirdPartyIntegration, IntegrationLog, APIEndpoint


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for Webhooks"""
    
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'description', 'url', 'events', 'secret_key',
            'custom_headers', 'status', 'is_active', 'max_retries', 'retry_delay',
            'total_deliveries', 'successful_deliveries', 'failed_deliveries',
            'last_delivery_at', 'success_rate', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_deliveries', 'successful_deliveries', 'failed_deliveries',
            'last_delivery_at', 'created_at', 'updated_at'
        ]
        extra_kwargs = {'secret_key': {'write_only': True}}
    
    def get_success_rate(self, obj):
        """Calculate webhook success rate"""
        if obj.total_deliveries > 0:
            return round((obj.successful_deliveries / obj.total_deliveries) * 100, 2)
        return 0


class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Serializer for Webhook Deliveries"""
    
    webhook_name = serializers.CharField(source='webhook.name', read_only=True)
    
    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'webhook', 'webhook_name', 'event', 'payload',
            'status', 'status_code', 'response_body', 'error_message',
            'attempts', 'next_retry_at', 'created_at', 'delivered_at', 'duration_ms'
        ]
        read_only_fields = ['id', 'created_at']


class ThirdPartyIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Third Party Integrations"""
    
    is_token_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ThirdPartyIntegration
        fields = [
            'id', 'name', 'provider', 'access_token', 'refresh_token',
            'token_expires_at', 'api_key', 'api_secret', 'config',
            'status', 'is_active', 'last_sync_at', 'error_message',
            'error_count', 'is_token_expired', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_sync_at', 'error_count', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True},
            'api_secret': {'write_only': True}
        }


class IntegrationLogSerializer(serializers.ModelSerializer):
    """Serializer for Integration Logs"""
    
    integration_name = serializers.CharField(source='integration.name', read_only=True)
    
    class Meta:
        model = IntegrationLog
        fields = [
            'id', 'integration', 'integration_name', 'action', 'description',
            'request_data', 'response_data', 'success', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class APIEndpointSerializer(serializers.ModelSerializer):
    """Serializer for API Endpoints"""
    
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = APIEndpoint
        fields = [
            'id', 'name', 'description', 'path', 'method', 'handler_type',
            'handler_url', 'handler_code', 'requires_auth', 'allowed_roles',
            'rate_limit', 'is_active', 'total_calls', 'successful_calls',
            'failed_calls', 'success_rate', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_calls', 'successful_calls', 'failed_calls',
            'created_at', 'updated_at'
        ]
    
    def get_success_rate(self, obj):
        """Calculate endpoint success rate"""
        if obj.total_calls > 0:
            return round((obj.successful_calls / obj.total_calls) * 100, 2)
        return 0
