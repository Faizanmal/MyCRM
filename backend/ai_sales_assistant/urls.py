"""
AI Sales Assistant URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AICoachDashboardView,
    AIEmailDraftViewSet,
    CallScriptViewSet,
    ContactPersonaMatchViewSet,
    DealInsightViewSet,
    ObjectionResponseViewSet,
    PersonaProfileViewSet,
    SalesCoachAdviceViewSet,
)

router = DefaultRouter()
router.register(r'email-drafts', AIEmailDraftViewSet, basename='ai-email-drafts')
router.register(r'coaching', SalesCoachAdviceViewSet, basename='sales-coaching')
router.register(r'objections', ObjectionResponseViewSet, basename='objection-responses')
router.register(r'call-scripts', CallScriptViewSet, basename='call-scripts')
router.register(r'deal-insights', DealInsightViewSet, basename='deal-insights')
router.register(r'personas', PersonaProfileViewSet, basename='personas')
router.register(r'persona-matches', ContactPersonaMatchViewSet, basename='persona-matches')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', AICoachDashboardView.as_view(), name='ai-coach-dashboard'),
]
