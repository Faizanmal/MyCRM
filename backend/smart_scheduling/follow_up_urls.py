"""
Follow-up and Calendar Sync URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .follow_up_views import (
    CalendarIntelligenceViewSet,
    CalendarSyncViewSet,
    FollowUpSequenceViewSet,
    MeetingAnalyticsViewSet,
    MeetingFollowUpViewSet,
    MeetingOutcomeViewSet,
    MultiCalendarViewSet,
    RecurringMeetingPatternViewSet,
)

router = DefaultRouter()

# Follow-up endpoints
router.register(r'follow-ups', MeetingFollowUpViewSet, basename='meeting-follow-ups')
router.register(r'sequences', FollowUpSequenceViewSet, basename='follow-up-sequences')
router.register(r'outcomes', MeetingOutcomeViewSet, basename='meeting-outcomes')
router.register(r'recurring', RecurringMeetingPatternViewSet, basename='recurring-patterns')

# Calendar endpoints
router.register(r'calendar/sync', CalendarSyncViewSet, basename='calendar-sync')
router.register(r'calendar/multi', MultiCalendarViewSet, basename='multi-calendar')
router.register(r'calendar/intelligence', CalendarIntelligenceViewSet, basename='calendar-intelligence')

# Analytics
router.register(r'analytics', MeetingAnalyticsViewSet, basename='meeting-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
