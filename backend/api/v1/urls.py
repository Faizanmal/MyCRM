"""
Unified API V1 URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, ContactViewSet, OpportunityViewSet, TaskViewSet
from .import_export import CSVImportView, CSVExportView
from .scoring import LeadScoringView
from .workflows import WorkflowViewSet, NotificationTemplateViewSet
from .analytics import SalesForecastView, ConversionFunnelView, CohortAnalysisView, CustomMetricsView
from .email_campaigns import EmailTemplateViewSet, EmailCampaignViewSet
from .audit_dashboard import (
    AuditTrailViewSet, FieldHistoryViewSet, 
    DashboardWidgetViewSet, UserDashboardViewSet
)
from .custom_fields import CustomFieldViewSet, CustomFieldValueViewSet
from .timeline import ActivityTimelineView, EntityTimelineView, UserActivityView

router = DefaultRouter()

# Core CRM resources
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'opportunities', OpportunityViewSet, basename='opportunity')
router.register(r'tasks', TaskViewSet, basename='task')

# Automation
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'notification-templates', NotificationTemplateViewSet, basename='notification-template')

# Email campaigns
router.register(r'email-templates', EmailTemplateViewSet, basename='email-template')
router.register(r'email-campaigns', EmailCampaignViewSet, basename='email-campaign')

# Audit & compliance
router.register(r'audit-trail', AuditTrailViewSet, basename='audit-trail')
router.register(r'field-history', FieldHistoryViewSet, basename='field-history')

# Dashboards
router.register(r'widgets', DashboardWidgetViewSet, basename='widget')
router.register(r'dashboards', UserDashboardViewSet, basename='dashboard')

# Custom fields
router.register(r'custom-fields', CustomFieldViewSet, basename='custom-field')
router.register(r'custom-field-values', CustomFieldValueViewSet, basename='custom-field-value')

urlpatterns = [
    path('', include(router.urls)),
    
    # CSV Import/Export endpoints
    path('import/<str:resource_type>/', CSVImportView.as_view(), name='csv-import'),
    path('export/<str:resource_type>/', CSVExportView.as_view(), name='csv-export'),
    
    # Lead scoring endpoint
    path('scoring/', LeadScoringView.as_view(), name='lead-scoring'),
    
    # Analytics endpoints
    path('analytics/forecast/', SalesForecastView.as_view(), name='analytics-forecast'),
    path('analytics/funnel/', ConversionFunnelView.as_view(), name='analytics-funnel'),
    path('analytics/cohort/', CohortAnalysisView.as_view(), name='analytics-cohort'),
    path('analytics/metrics/', CustomMetricsView.as_view(), name='analytics-metrics'),
    
    # Activity timeline endpoints
    path('timeline/', ActivityTimelineView.as_view(), name='activity-timeline'),
    path('timeline/<str:entity_type>/<int:entity_id>/', EntityTimelineView.as_view(), name='entity-timeline'),
    path('timeline/user/', UserActivityView.as_view(), name='user-activity'),
    path('timeline/user/<int:user_id>/', UserActivityView.as_view(), name='user-activity-by-id'),
]
