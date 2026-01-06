"""
Conversation Intelligence URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'recordings', views.CallRecordingViewSet, basename='call-recording')
router.register(r'playlists', views.CallPlaylistViewSet, basename='call-playlist')
router.register(r'trackers', views.CallTrackerViewSet, basename='call-tracker')
router.register(r'analytics', views.ConversationAnalyticsViewSet, basename='conversation-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
