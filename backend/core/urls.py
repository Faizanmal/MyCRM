"""
Core URL patterns for enterprise features
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from campaign_management.views import CampaignViewSet, EmailTemplateViewSet

router = DefaultRouter()
router.register(r'audit-logs', views.AuditLogViewSet)
router.register(r'system-config', views.SystemConfigurationViewSet)
router.register(r'api-keys', views.APIKeyViewSet)
router.register(r'data-backups', views.DataBackupViewSet)
router.register(r'workflows', views.WorkflowViewSet)
router.register(r'workflow-executions', views.WorkflowExecutionViewSet)
router.register(r'integrations', views.IntegrationViewSet)
router.register(r'notification-templates', views.NotificationTemplateViewSet)
router.register(r'system-health', views.SystemHealthViewSet)
router.register(r'security-dashboard', views.SecurityDashboardViewSet, basename='security-dashboard')
router.register(r'advanced-analytics', views.AdvancedAnalyticsViewSet, basename='advanced-analytics')
router.register(r'ai-analytics', views.AIAnalyticsViewSet, basename='ai-analytics')
router.register(r'email-campaigns', CampaignViewSet, basename='email-campaign')
router.register(r'email-templates', EmailTemplateViewSet, basename='email-template')

urlpatterns = [
    path('', include(router.urls)),
    # Analytics endpoints (legacy compatibility)
    path('analytics/ai_insights_dashboard/', views.AIAnalyticsViewSet.as_view({'get': 'ai_insights_dashboard'}), name='ai-insights-dashboard'),
    path('analytics/sales_forecast/', views.AIAnalyticsViewSet.as_view({'get': 'sales_forecast'}), name='sales-forecast'),
    path('analytics/pipeline_analytics/', views.AIAnalyticsViewSet.as_view({'get': 'pipeline_analytics'}), name='pipeline-analytics'),
]