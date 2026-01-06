"""
Mobile App Enhancement URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .mobile_views import (
    BusinessCardScanViewSet,
    DeviceRegistrationViewSet,
    LocationCheckInViewSet,
    MobileActivityLogViewSet,
    OfflineSyncViewSet,
    VoiceNoteViewSet,
)

router = DefaultRouter()
router.register(r'devices', DeviceRegistrationViewSet, basename='devices')
router.register(r'sync', OfflineSyncViewSet, basename='offline-sync')
router.register(r'business-cards', BusinessCardScanViewSet, basename='business-cards')
router.register(r'checkins', LocationCheckInViewSet, basename='location-checkins')
router.register(r'voice-notes', VoiceNoteViewSet, basename='voice-notes')
router.register(r'activity-logs', MobileActivityLogViewSet, basename='mobile-activity-logs')


urlpatterns = [
    path('', include(router.urls)),
]
