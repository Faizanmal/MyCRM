"""
Progressive Web App (PWA) URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .pwa_views import (
    BackgroundSyncViewSet,
    CacheManifestViewSet,
    OfflineActionViewSet,
    PushNotificationViewSet,
    PushSubscriptionViewSet,
    PWAAnalyticsViewSet,
    ServiceWorkerConfigView,
)

router = DefaultRouter()
router.register(r'push/subscriptions', PushSubscriptionViewSet, basename='push-subscriptions')
router.register(r'push/notifications', PushNotificationViewSet, basename='push-notifications')
router.register(r'sync', BackgroundSyncViewSet, basename='background-sync')
router.register(r'offline-actions', OfflineActionViewSet, basename='offline-actions')
router.register(r'analytics', PWAAnalyticsViewSet, basename='pwa-analytics')
router.register(r'cache', CacheManifestViewSet, basename='cache-manifest')


# Service worker config endpoint
sw_config = ServiceWorkerConfigView.as_view({'get': 'config'})


urlpatterns = [
    path('', include(router.urls)),
    path('sw-config/', sw_config, name='sw-config'),
]
