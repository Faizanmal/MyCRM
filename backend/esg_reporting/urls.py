"""
ESG Reporting URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ESGFrameworkViewSet, ESGMetricCategoryViewSet, ESGMetricDefinitionViewSet,
    ESGDataEntryViewSet, ESGTargetViewSet, ESGReportViewSet,
    CarbonFootprintViewSet, SupplierESGAssessmentViewSet, ESGDashboardView
)

app_name = 'esg_reporting'

router = DefaultRouter()
router.register(r'frameworks', ESGFrameworkViewSet, basename='frameworks')
router.register(r'categories', ESGMetricCategoryViewSet, basename='categories')
router.register(r'metrics', ESGMetricDefinitionViewSet, basename='metrics')
router.register(r'data', ESGDataEntryViewSet, basename='data')
router.register(r'targets', ESGTargetViewSet, basename='targets')
router.register(r'reports', ESGReportViewSet, basename='reports')
router.register(r'carbon', CarbonFootprintViewSet, basename='carbon')
router.register(r'suppliers', SupplierESGAssessmentViewSet, basename='suppliers')

urlpatterns = [
    path('dashboard/', ESGDashboardView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]
