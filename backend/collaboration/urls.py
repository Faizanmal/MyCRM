from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ApprovalInstanceViewSet,
    ApprovalWorkflowViewSet,
    ChannelViewSet,
    CollaborativeDocumentViewSet,
    DealRoomViewSet,
    DocumentCommentViewSet,
    MessageViewSet,
)

app_name = 'collaboration'

router = DefaultRouter()
router.register(r'deal-rooms', DealRoomViewSet, basename='dealroom')
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'documents', CollaborativeDocumentViewSet, basename='document')
router.register(r'document-comments', DocumentCommentViewSet, basename='documentcomment')
router.register(r'workflows', ApprovalWorkflowViewSet, basename='workflow')
router.register(r'approval-instances', ApprovalInstanceViewSet, basename='approvalinstance')

urlpatterns = [
    path('', include(router.urls)),
]
