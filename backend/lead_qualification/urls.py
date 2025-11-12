from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ScoringRuleViewSet,
    QualificationCriteriaViewSet,
    LeadScoreViewSet,
    QualificationWorkflowViewSet,
    WorkflowExecutionViewSet,
    LeadEnrichmentDataViewSet
)

router = DefaultRouter()
router.register(r'scoring-rules', ScoringRuleViewSet, basename='scoring-rule')
router.register(r'qualification-criteria', QualificationCriteriaViewSet, basename='qualification-criteria')
router.register(r'lead-scores', LeadScoreViewSet, basename='lead-score')
router.register(r'workflows', QualificationWorkflowViewSet, basename='workflow')
router.register(r'workflow-executions', WorkflowExecutionViewSet, basename='workflow-execution')
router.register(r'enrichment', LeadEnrichmentDataViewSet, basename='enrichment')

urlpatterns = [
    path('', include(router.urls)),
]
