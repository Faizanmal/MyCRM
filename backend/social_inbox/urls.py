"""
Social Inbox URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    SocialAccountViewSet,
    SocialConversationViewSet,
    SocialMonitoringRuleViewSet,
    SocialPostViewSet,
    UnifiedInboxDashboardView,
)

app_name = 'social_inbox'

router = DefaultRouter()
router.register(r'accounts', SocialAccountViewSet, basename='accounts')
router.register(r'conversations', SocialConversationViewSet, basename='conversations')
router.register(r'monitoring-rules', SocialMonitoringRuleViewSet, basename='monitoring-rules')
router.register(r'posts', SocialPostViewSet, basename='posts')

urlpatterns = [
    path('dashboard/', UnifiedInboxDashboardView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]
