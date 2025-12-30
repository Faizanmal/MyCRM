"""
AI Sales Assistant - Chatbot URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .chatbot_views import (
    ConversationSessionViewSet, ChatMessageViewSet,
    QuickActionViewSet, PredictiveDealIntelligenceViewSet,
    SmartContentViewSet, AIAssistantDashboardView
)

router = DefaultRouter()
router.register(r'sessions', ConversationSessionViewSet, basename='chat-sessions')
router.register(r'messages', ChatMessageViewSet, basename='chat-messages')
router.register(r'quick-actions', QuickActionViewSet, basename='quick-actions')
router.register(r'deal-intelligence', PredictiveDealIntelligenceViewSet, basename='deal-intelligence')
router.register(r'smart-content', SmartContentViewSet, basename='smart-content')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', AIAssistantDashboardView.as_view(), name='ai-assistant-dashboard'),
]
