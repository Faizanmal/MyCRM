"""
Integration Hub URLs
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .inbound_views import InboundWebhookReceiverView
from .views import (
    APIEndpointViewSet,
    IntegrationLogViewSet,
    ThirdPartyIntegrationViewSet,
    WebhookDeliveryViewSet,
    WebhookViewSet,
)

router = DefaultRouter()
router.register(r'webhooks', WebhookViewSet, basename='webhook')
router.register(r'webhook-deliveries', WebhookDeliveryViewSet, basename='webhook-delivery')
router.register(r'integrations', ThirdPartyIntegrationViewSet, basename='integration')
router.register(r'logs', IntegrationLogViewSet, basename='integration-log')
router.register(r'endpoints', APIEndpointViewSet, basename='api-endpoint')

urlpatterns = [
    path('webhooks/inbound/<uuid:endpoint_id>/', InboundWebhookReceiverView.as_view(), name='inbound-webhook-receiver'),
    path('', include(router.urls)),
]
