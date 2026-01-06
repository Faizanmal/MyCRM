"""
Revenue Intelligence Dashboard URLs
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .dashboard_views import (
    ARRMovementViewSet,
    CohortAnalysisViewSet,
    RevenueAttributionViewSet,
    RevenueForecastViewSet,
    RevenueIntelligenceSnapshotViewSet,
    RevenueLeakageViewSet,
    SalesVelocityViewSet,
    WinLossAnalysisViewSet,
)

router = DefaultRouter()
router.register(r'forecasts', RevenueForecastViewSet, basename='forecasts')
router.register(r'cohorts', CohortAnalysisViewSet, basename='cohorts')
router.register(r'attribution', RevenueAttributionViewSet, basename='attribution')
router.register(r'velocity', SalesVelocityViewSet, basename='velocity')
router.register(r'leakage', RevenueLeakageViewSet, basename='leakage')
router.register(r'win-loss', WinLossAnalysisViewSet, basename='win-loss')
router.register(r'arr-movement', ARRMovementViewSet, basename='arr-movement')
router.register(r'snapshots', RevenueIntelligenceSnapshotViewSet, basename='snapshots')

urlpatterns = [
    path('', include(router.urls)),
]
