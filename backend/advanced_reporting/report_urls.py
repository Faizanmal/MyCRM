"""
Custom Report Builder URLs
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .report_views import (
    DataSourceViewSet,
    PublicDashboardView,
    ReportDashboardViewSet,
    ReportFolderViewSet,
    ReportSubscriptionViewSet,
    ReportTemplateViewSet,
    ReportWidgetViewSet,
    SavedReportViewSet,
    ScheduledReportViewSet,
)

router = DefaultRouter()
router.register(r'templates', ReportTemplateViewSet, basename='report-templates')
router.register(r'widgets', ReportWidgetViewSet, basename='report-widgets')
router.register(r'saved', SavedReportViewSet, basename='saved-reports')
router.register(r'schedules', ScheduledReportViewSet, basename='scheduled-reports')
router.register(r'dashboards', ReportDashboardViewSet, basename='dashboards')
router.register(r'data-sources', DataSourceViewSet, basename='data-sources')
router.register(r'folders', ReportFolderViewSet, basename='report-folders')
router.register(r'subscriptions', ReportSubscriptionViewSet, basename='report-subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    path('public/<str:token>/', PublicDashboardView.as_view(), name='public-dashboard'),
]
