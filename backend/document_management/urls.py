"""
Document Management URLs
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DocumentApprovalViewSet,
    DocumentCommentViewSet,
    DocumentShareViewSet,
    DocumentTemplateViewSet,
    DocumentViewSet,
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'templates', DocumentTemplateViewSet, basename='template')
router.register(r'shares', DocumentShareViewSet, basename='share')
router.register(r'comments', DocumentCommentViewSet, basename='comment')
router.register(r'approvals', DocumentApprovalViewSet, basename='approval')

urlpatterns = [
    path('', include(router.urls)),
]
