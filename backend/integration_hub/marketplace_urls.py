"""
Integration Marketplace - URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .marketplace_views import (
    MarketplaceAppViewSet, AppInstallationViewSet,
    CustomWebhookViewSet, APIRateLimitViewSet,
    APIUsageViewSet, IntegrationMarketplaceDashboardView
)

router = DefaultRouter()
router.register(r'apps', MarketplaceAppViewSet, basename='marketplace-apps')
router.register(r'installations', AppInstallationViewSet, basename='app-installations')
router.register(r'webhooks', CustomWebhookViewSet, basename='custom-webhooks')
router.register(r'rate-limits', APIRateLimitViewSet, basename='api-rate-limits')
router.register(r'usage', APIUsageViewSet, basename='api-usage')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', IntegrationMarketplaceDashboardView.as_view(), name='marketplace-dashboard'),
]
