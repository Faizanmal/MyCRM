"""
Revenue Intelligence URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RevenueTargetViewSet, DealScoreViewSet, CompetitorViewSet,
    DealCompetitorViewSet, RevenueForecastViewSet, DealRiskAlertViewSet,
    PipelineHealthView, QuotaLeaderboardView
)

router = DefaultRouter()
router.register(r'targets', RevenueTargetViewSet, basename='revenue-targets')
router.register(r'deal-scores', DealScoreViewSet, basename='deal-scores')
router.register(r'competitors', CompetitorViewSet, basename='competitors')
router.register(r'deal-competitors', DealCompetitorViewSet, basename='deal-competitors')
router.register(r'forecasts', RevenueForecastViewSet, basename='forecasts')
router.register(r'risk-alerts', DealRiskAlertViewSet, basename='risk-alerts')

urlpatterns = [
    path('', include(router.urls)),
    path('pipeline-health/', PipelineHealthView.as_view(), name='pipeline-health'),
    path('leaderboard/', QuotaLeaderboardView.as_view(), name='quota-leaderboard'),
]
