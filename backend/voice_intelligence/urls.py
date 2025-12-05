"""
Voice Intelligence URLs
URL routing for voice intelligence endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VoiceRecordingViewSet, ActionItemViewSet,
    VoiceNoteViewSet, ConversationCategoryViewSet,
    TranscriptionSettingsViewSet
)

app_name = 'voice_intelligence'

router = DefaultRouter()
router.register(r'recordings', VoiceRecordingViewSet, basename='recording')
router.register(r'action-items', ActionItemViewSet, basename='action-item')
router.register(r'voice-notes', VoiceNoteViewSet, basename='voice-note')
router.register(r'categories', ConversationCategoryViewSet, basename='category')
router.register(r'settings', TranscriptionSettingsViewSet, basename='settings')

urlpatterns = [
    path('', include(router.urls)),
]
