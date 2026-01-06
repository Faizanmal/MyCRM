"""
Unified API V1 URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .analytics import (
    CohortAnalysisView,
    ConversionFunnelView,
    CustomMetricsView,
    DashboardAnalyticsView,
    SalesForecastView,
)
from .audit_dashboard import (
    AuditTrailViewSet,
    DashboardWidgetViewSet,
    FieldHistoryViewSet,
    UserDashboardViewSet,
)
from .custom_fields import CustomFieldValueViewSet, CustomFieldViewSet
from .email_campaigns import EmailCampaignViewSet, EmailTemplateViewSet
from .import_export import CSVExportView, CSVImportView
from .scoring import LeadScoringView
from .timeline import ActivityTimelineView, EntityTimelineView, UserActivityView
from .views import ContactViewSet, LeadViewSet, OpportunityViewSet, TaskViewSet
from .workflows import NotificationTemplateViewSet, WorkflowViewSet

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
    path('analytics/dashboard/', DashboardAnalyticsView.as_view(), name='analytics-dashboard'),

    # Activity timeline endpoints
    path('timeline/', ActivityTimelineView.as_view(), name='activity-timeline'),
    path('timeline/<str:entity_type>/<int:entity_id>/', EntityTimelineView.as_view(), name='entity-timeline'),
    path('timeline/user/', UserActivityView.as_view(), name='user-activity'),
    path('timeline/user/<int:user_id>/', UserActivityView.as_view(), name='user-activity-by-id'),

    # Interactive features (user preferences, onboarding, AI recommendations, search)
    path('interactive/', include('core.interactive_urls')),
]

