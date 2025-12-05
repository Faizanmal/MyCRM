"""
Data Enrichment URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EnrichmentProviderViewSet,
    EnrichmentProfileViewSet,
    CompanyEnrichmentViewSet,
    IntentSignalViewSet,
    NewsAlertViewSet,
    EmailVerificationViewSet,
    EnrichmentJobViewSet,
    EnrichmentRuleViewSet,
    EnrichmentActivityViewSet,
    EnrichmentDashboardViewSet
)

router = DefaultRouter()
router.register(r'providers', EnrichmentProviderViewSet, basename='enrichment-providers')
router.register(r'profiles', EnrichmentProfileViewSet, basename='enrichment-profiles')
router.register(r'companies', CompanyEnrichmentViewSet, basename='company-enrichments')
router.register(r'intent-signals', IntentSignalViewSet, basename='intent-signals')
router.register(r'news-alerts', NewsAlertViewSet, basename='news-alerts')
router.register(r'email-verification', EmailVerificationViewSet, basename='email-verification')
router.register(r'jobs', EnrichmentJobViewSet, basename='enrichment-jobs')
router.register(r'rules', EnrichmentRuleViewSet, basename='enrichment-rules')
router.register(r'activities', EnrichmentActivityViewSet, basename='enrichment-activities')
router.register(r'dashboard', EnrichmentDashboardViewSet, basename='enrichment-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
