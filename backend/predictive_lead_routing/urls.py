from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EscalationRuleViewSet,
    LeadAssignmentViewSet,
    LeadRoutingViewSet,
    RebalancingViewSet,
    RepSkillAssignmentViewSet,
    RoutingAnalyticsViewSet,
    RoutingRuleViewSet,
    SalesRepProfileViewSet,
    SkillCertificationViewSet,
    TerritoryDefinitionViewSet,
)

router = DefaultRouter()
router.register(r'rep-profiles', SalesRepProfileViewSet, basename='rep-profile')
router.register(r'rules', RoutingRuleViewSet, basename='routing-rule')
router.register(r'assignments', LeadAssignmentViewSet, basename='lead-assignment')
router.register(r'routing', LeadRoutingViewSet, basename='lead-routing')
router.register(r'escalation-rules', EscalationRuleViewSet, basename='escalation-rule')
router.register(r'rebalancing', RebalancingViewSet, basename='rebalancing')
router.register(r'skills', SkillCertificationViewSet, basename='skill')
router.register(r'rep-skills', RepSkillAssignmentViewSet, basename='rep-skill')
router.register(r'territories', TerritoryDefinitionViewSet, basename='territory')
router.register(r'analytics', RoutingAnalyticsViewSet, basename='routing-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
