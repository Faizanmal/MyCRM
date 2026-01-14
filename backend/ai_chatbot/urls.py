"""
AI Chatbot URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ChatSessionViewSet,
    ChatView,
    EmailTemplateViewSet,
    GenerateEmailView,
    MessageFeedbackView,
    QueryDataView,
    QuickActionViewSet,
    SuggestNextActionsView,
)

app_name = 'ai_chatbot'

router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='sessions')
router.register(r'quick-actions', QuickActionViewSet, basename='quick-actions')
router.register(r'email-templates', EmailTemplateViewSet, basename='email-templates')

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('generate-email/', GenerateEmailView.as_view(), name='generate-email'),
    path('query/', QueryDataView.as_view(), name='query'),
    path('suggest-actions/', SuggestNextActionsView.as_view(), name='suggest-actions'),
    path('messages/<uuid:message_id>/feedback/', MessageFeedbackView.as_view(), name='message-feedback'),
    path('', include(router.urls)),
]
