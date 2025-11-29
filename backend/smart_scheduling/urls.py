"""
Smart Scheduling URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchedulingPageViewSet, MeetingTypeViewSet, AvailabilityViewSet,
    BlockedTimeViewSet, MeetingViewSet, CalendarIntegrationViewSet,
    PublicSchedulingPageView, AvailableSlotsView, BookMeetingView,
    GuestMeetingActionsView, SchedulingDashboardView
)

router = DefaultRouter()
router.register(r'pages', SchedulingPageViewSet, basename='scheduling-pages')
router.register(r'meeting-types', MeetingTypeViewSet, basename='meeting-types')
router.register(r'availability', AvailabilityViewSet, basename='availability')
router.register(r'blocked-times', BlockedTimeViewSet, basename='blocked-times')
router.register(r'meetings', MeetingViewSet, basename='meetings')
router.register(r'calendar-integrations', CalendarIntegrationViewSet, basename='calendar-integrations')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', SchedulingDashboardView.as_view(), name='scheduling-dashboard'),
    
    # Public endpoints (no auth required)
    path('public/<slug:slug>/', PublicSchedulingPageView.as_view(), name='public-page'),
    path('public/<slug:slug>/<slug:meeting_type_slug>/slots/', AvailableSlotsView.as_view(), name='available-slots'),
    path('public/<slug:slug>/book/', BookMeetingView.as_view(), name='book-meeting'),
    path('guest/<str:token>/', GuestMeetingActionsView.as_view(), name='guest-actions'),
]
