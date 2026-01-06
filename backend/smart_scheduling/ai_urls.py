"""
Smart Scheduling AI URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .ai_views import (
    AISchedulingPreferenceViewSet,
    AITimeSuggestionViewSet,
    AttendeeIntelligenceViewSet,
    MeetingPrepAIViewSet,
    NoShowPredictionViewSet,
    ScheduleOptimizationViewSet,
    SmartReminderViewSet,
    SmartRescheduleViewSet,
)

router = DefaultRouter()
router.register(r'preferences', AISchedulingPreferenceViewSet, basename='ai-scheduling-preferences')
router.register(r'time-suggestions', AITimeSuggestionViewSet, basename='ai-time-suggestions')
router.register(r'no-show-predictions', NoShowPredictionViewSet, basename='no-show-predictions')
router.register(r'meeting-prep', MeetingPrepAIViewSet, basename='meeting-prep')
router.register(r'reschedule', SmartRescheduleViewSet, basename='smart-reschedule')
router.register(r'reminders', SmartReminderViewSet, basename='smart-reminders')
router.register(r'optimizations', ScheduleOptimizationViewSet, basename='schedule-optimizations')
router.register(r'attendee-intelligence', AttendeeIntelligenceViewSet, basename='attendee-intelligence')

urlpatterns = [
    path('', include(router.urls)),
]
