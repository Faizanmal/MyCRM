from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnalyticsViewSet,
    DashboardViewSet,
    DataExportViewSet,
    KPIMetricViewSet,
    ReportScheduleViewSet,
    ReportViewSet,
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
