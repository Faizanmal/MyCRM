"""
Enhanced Communication Hub URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .enhanced_views import (
    UnifiedInboxViewSet,
    InboxLabelViewSet,
    MultiChannelCampaignViewSet,
    CampaignStepViewSet,
    CampaignRecipientViewSet,
    EmailTrackingViewSet,
    TrackingPixelView,
    CommunicationPreferenceViewSet
)


router = DefaultRouter()
router.register(r'inbox', UnifiedInboxViewSet, basename='unified-inbox')
router.register(r'inbox-labels', InboxLabelViewSet, basename='inbox-labels')
router.register(r'campaigns', MultiChannelCampaignViewSet, basename='multi-channel-campaigns')
router.register(r'campaign-steps', CampaignStepViewSet, basename='campaign-steps')
router.register(r'campaign-recipients', CampaignRecipientViewSet, basename='campaign-recipients')
router.register(r'email-tracking', EmailTrackingViewSet, basename='email-tracking')
router.register(r'preferences', CommunicationPreferenceViewSet, basename='communication-preferences')


# Tracking pixel URLs (public, no auth)
tracking_pixel = TrackingPixelView.as_view({
    'get': 'track_open'
})
tracking_click = TrackingPixelView.as_view({
    'get': 'track_click'
})


urlpatterns = [
    path('', include(router.urls)),
    
    # Public tracking endpoints
    path('track/open/<str:pk>/', tracking_pixel, name='tracking-pixel'),
    path('track/click/<str:pk>/', tracking_click, name='tracking-click'),
]
