"""
Integration Hub URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WebhookViewSet, WebhookDeliveryViewSet, ThirdPartyIntegrationViewSet,
    IntegrationLogViewSet, APIEndpointViewSet
)

router = DefaultRouter()
router.register(r'webhooks', WebhookViewSet, basename='webhook')
router.register(r'webhook-deliveries', WebhookDeliveryViewSet, basename='webhook-delivery')
router.register(r'integrations', ThirdPartyIntegrationViewSet, basename='integration')
router.register(r'logs', IntegrationLogViewSet, basename='integration-log')
router.register(r'endpoints', APIEndpointViewSet, basename='api-endpoint')

urlpatterns = [
    path('', include(router.urls)),
]
