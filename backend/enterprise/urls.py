"""
Enterprise Security URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AccessPolicyViewSet,
    DataClassificationViewSet,
    DeviceFingerprintViewSet,
    RiskAssessmentView,
    SecurityAuditLogViewSet,
    SecurityDashboardView,
    SecurityIncidentViewSet,
    SecuritySessionViewSet,
    ThreatIndicatorViewSet,
)

app_name = 'enterprise'

router = DefaultRouter()
router.register(r'devices', DeviceFingerprintViewSet, basename='devices')
router.register(r'sessions', SecuritySessionViewSet, basename='sessions')
router.register(r'audit-logs', SecurityAuditLogViewSet, basename='audit-logs')
router.register(r'policies', AccessPolicyViewSet, basename='policies')
router.register(r'threats', ThreatIndicatorViewSet, basename='threats')
router.register(r'incidents', SecurityIncidentViewSet, basename='incidents')
router.register(r'classifications', DataClassificationViewSet, basename='classifications')

urlpatterns = [
    path('dashboard/', SecurityDashboardView.as_view(), name='dashboard'),
    path('risk-assessment/', RiskAssessmentView.as_view(), name='risk-assessment'),
    path('', include(router.urls)),
]
