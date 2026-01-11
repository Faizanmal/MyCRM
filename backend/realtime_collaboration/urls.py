"""
Real-Time Collaboration URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CollaborativeDocumentViewSet, DocumentTemplateViewSet,
    SharedDocumentView, MyCollaborationsView
)

app_name = 'realtime_collaboration'

router = DefaultRouter()
router.register(r'documents', CollaborativeDocumentViewSet, basename='documents')
router.register(r'templates', DocumentTemplateViewSet, basename='templates')

urlpatterns = [
    path('shared/<str:token>/', SharedDocumentView.as_view(), name='shared-document'),
    path('my-collaborations/', MyCollaborationsView.as_view(), name='my-collaborations'),
    path('', include(router.urls)),
]
