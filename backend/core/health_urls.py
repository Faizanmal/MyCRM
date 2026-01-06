"""
Health Check URL Configuration
"""

from django.urls import path

from .health_views import (
    DetailedHealthCheckView,
    HealthCheckView,
    LivenessCheckView,
    MetricsView,
    PingView,
    ReadinessCheckView,
)

urlpatterns = [
    path('healthz/', HealthCheckView.as_view(), name='health-check'),
    path('ping/', PingView.as_view(), name='ping'),
    path('ready/', ReadinessCheckView.as_view(), name='readiness-check'),
    path('live/', LivenessCheckView.as_view(), name='liveness-check'),
    path('health/', DetailedHealthCheckView.as_view(), name='detailed-health'),
    path('metrics/', MetricsView.as_view(), name='metrics'),
]
