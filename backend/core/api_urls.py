"""
Core API URL Configuration

URL patterns for core utilities including:
- Export endpoints
- Analytics endpoints
- Bulk operations
- Health checks
"""

from django.urls import path

from .analytics_views import (
    activity_analytics,
    dashboard_metrics,
    lead_source_analytics,
    pipeline_analytics,
    revenue_analytics,
    team_performance,
)
from .bulk_operations import (
    bulk_assign_leads,
    bulk_complete_tasks,
    bulk_delete_leads,
    bulk_update_leads,
    bulk_update_tasks,
)
from .export_utils import (
    export_contacts,
    export_leads,
    export_opportunities,
    export_tasks,
)
from .monitoring import (
    health_check,
    liveness_check,
    metrics_view,
    readiness_check,
)

app_name = 'core'

urlpatterns = [
    # Export endpoints
    path('export/leads/', export_leads, name='export-leads'),
    path('export/contacts/', export_contacts, name='export-contacts'),
    path('export/opportunities/', export_opportunities, name='export-opportunities'),
    path('export/tasks/', export_tasks, name='export-tasks'),

    # Analytics endpoints
    path('analytics/dashboard/', dashboard_metrics, name='analytics-dashboard'),
    path('analytics/revenue/', revenue_analytics, name='analytics-revenue'),
    path('analytics/pipeline/', pipeline_analytics, name='analytics-pipeline'),
    path('analytics/activity/', activity_analytics, name='analytics-activity'),
    path('analytics/team/', team_performance, name='analytics-team'),
    path('analytics/lead-sources/', lead_source_analytics, name='analytics-lead-sources'),

    # Bulk operations
    path('bulk/leads/update/', bulk_update_leads, name='bulk-update-leads'),
    path('bulk/leads/delete/', bulk_delete_leads, name='bulk-delete-leads'),
    path('bulk/leads/assign/', bulk_assign_leads, name='bulk-assign-leads'),
    path('bulk/tasks/update/', bulk_update_tasks, name='bulk-update-tasks'),
    path('bulk/tasks/complete/', bulk_complete_tasks, name='bulk-complete-tasks'),

    # Health check endpoints
    path('health/', health_check, name='health-check'),
    path('healthz/', liveness_check, name='liveness-check'),
    path('ready/', readiness_check, name='readiness-check'),
    path('metrics/', metrics_view, name='metrics'),
]
