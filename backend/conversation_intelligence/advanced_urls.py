"""
Voice & Conversation Intelligence - Advanced URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .advanced_views import (
    RealTimeCoachingViewSet, CoachingSuggestionViewSet,
    SentimentAnalysisViewSet, MeetingSummaryViewSet,
    MeetingActionItemViewSet, KeyMomentViewSet,
    CallCoachingMetricsViewSet, ConversationIntelligenceDashboardView
)

router = DefaultRouter()
router.register(r'coaching-sessions', RealTimeCoachingViewSet, basename='coaching-sessions')
router.register(r'coaching-suggestions', CoachingSuggestionViewSet, basename='coaching-suggestions')
router.register(r'sentiment', SentimentAnalysisViewSet, basename='sentiment')
router.register(r'meeting-summaries', MeetingSummaryViewSet, basename='meeting-summaries')
router.register(r'action-items', MeetingActionItemViewSet, basename='action-items')
router.register(r'key-moments', KeyMomentViewSet, basename='key-moments')
router.register(r'coaching-metrics', CallCoachingMetricsViewSet, basename='coaching-metrics')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', ConversationIntelligenceDashboardView.as_view(), name='conversation-intelligence-dashboard'),
]
