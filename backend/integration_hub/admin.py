from django.contrib import admin
from .models import Webhook, WebhookDelivery, ThirdPartyIntegration, IntegrationLog, APIEndpoint


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'status', 'is_active', 'total_deliveries', 'successful_deliveries']
    list_filter = ['status', 'is_active']
    search_fields = ['name', 'url']
    readonly_fields = ['total_deliveries', 'successful_deliveries', 'failed_deliveries', 'last_delivery_at']


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ['webhook', 'event', 'status', 'status_code', 'attempts', 'created_at']
    list_filter = ['status', 'event']
    search_fields = ['webhook__name']
    readonly_fields = ['created_at', 'delivered_at']


@admin.register(ThirdPartyIntegration)
class ThirdPartyIntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'status', 'is_active', 'last_sync_at']
    list_filter = ['provider', 'status', 'is_active']
    search_fields = ['name']


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ['integration', 'action', 'success', 'created_at']
    list_filter = ['action', 'success']
    search_fields = ['integration__name', 'description']


@admin.register(APIEndpoint)
class APIEndpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'method', 'path', 'is_active', 'total_calls', 'successful_calls']
    list_filter = ['method', 'is_active']
    search_fields = ['name', 'path']
