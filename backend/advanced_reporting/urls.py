from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardViewSet,
    DashboardWidgetViewSet,
    KPIValueViewSet,
    KPIViewSet,
    ReportExecutionViewSet,
    ReportScheduleViewSet,
    ReportViewSet,
)

router = DefaultRouter()
router.register(r'dashboards', DashboardViewSet, basename='dashboard')
router.register(r'widgets', DashboardWidgetViewSet, basename='widget')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'schedules', ReportScheduleViewSet, basename='schedule')
router.register(r'executions', ReportExecutionViewSet, basename='execution')
router.register(r'kpis', KPIViewSet, basename='kpi')
router.register(r'kpi-values', KPIValueViewSet, basename='kpi-value')

urlpatterns = [
    path('', include(router.urls)),
]
