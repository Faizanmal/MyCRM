"""
Email Tracking URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EmailAnalyticsDashboardView,
    EmailSequenceViewSet,
    EmailTemplateViewSet,
    SequenceStepViewSet,
    TrackedEmailViewSet,
    TrackingLinkView,
    TrackingPixelView,
)

router = DefaultRouter()
router.register(r'emails', TrackedEmailViewSet, basename='tracked-emails')
router.register(r'templates', EmailTemplateViewSet, basename='email-templates')
router.register(r'sequences', EmailSequenceViewSet, basename='email-sequences')
router.register(r'sequence-steps', SequenceStepViewSet, basename='sequence-steps')

urlpatterns = [
    path('', include(router.urls)),
    path('pixel/<str:tracking_id>/', TrackingPixelView.as_view(), name='tracking-pixel'),
    path('click/<str:tracking_id>/', TrackingLinkView.as_view(), name='tracking-click'),
    path('analytics/', EmailAnalyticsDashboardView.as_view(), name='email-analytics'),
]
