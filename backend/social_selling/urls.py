"""
Social Selling URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'profiles', views.SocialProfileViewSet, basename='social-profile')
router.register(r'engagements', views.SocialEngagementViewSet, basename='social-engagement')
router.register(r'linkedin', views.LinkedInIntegrationViewSet, basename='linkedin')
router.register(r'sequences', views.SocialSellingSequenceViewSet, basename='social-sequence')
router.register(r'insights', views.SocialInsightViewSet, basename='social-insight')
router.register(r'analytics', views.EngagementAnalyticsViewSet, basename='engagement-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
