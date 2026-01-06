"""
Advanced Workflow Engine URLs
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .workflow_views import (
    WorkflowApprovalViewSet,
    WorkflowDefinitionViewSet,
    WorkflowInstanceViewSet,
    WorkflowNodeViewSet,
    WorkflowTemplateViewSet,
    WorkflowTriggerView,
)

router = DefaultRouter()
router.register(r'definitions', WorkflowDefinitionViewSet, basename='workflow-definitions')
router.register(r'nodes', WorkflowNodeViewSet, basename='workflow-nodes')
router.register(r'instances', WorkflowInstanceViewSet, basename='workflow-instances')
router.register(r'approvals', WorkflowApprovalViewSet, basename='workflow-approvals')
router.register(r'templates', WorkflowTemplateViewSet, basename='workflow-templates')

urlpatterns = [
    path('', include(router.urls)),
    path('trigger/<str:workflow_id>/', WorkflowTriggerView.as_view(), name='workflow-trigger'),
]
