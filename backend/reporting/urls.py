from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardViewSet, ReportViewSet, ReportScheduleViewSet,
    AnalyticsViewSet, KPIMetricViewSet, DataExportViewSet
)

router = DefaultRouter()
router.register(r'dashboards', DashboardViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'report-schedules', ReportScheduleViewSet)
router.register(r'analytics', AnalyticsViewSet)
router.register(r'kpi-metrics', KPIMetricViewSet)
router.register(r'data-exports', DataExportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
