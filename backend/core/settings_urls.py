"""
Settings URL Configuration
URL patterns for user preferences, notifications, export, RBAC, and analytics APIs
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .settings_views import (
    AnalyticsDashboardView,
    ExportJobViewSet,
    NotificationPreferenceViewSet,
    UserPreferenceViewSet,
    UserRoleAssignmentViewSet,
    UserRoleViewSet,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'preferences', UserPreferenceViewSet, basename='preferences')
router.register(r'notifications', NotificationPreferenceViewSet, basename='notifications')
router.register(r'export', ExportJobViewSet, basename='export')
router.register(r'roles', UserRoleViewSet, basename='roles')
router.register(r'role-assignments', UserRoleAssignmentViewSet, basename='role-assignments')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),

    # Analytics dashboard
    path('analytics/dashboard/', AnalyticsDashboardView.as_view(), name='analytics-dashboard'),

    # Convenience shortcuts for preferences
    path('preferences/me/', UserPreferenceViewSet.as_view({'get': 'list', 'patch': 'update_preferences'}), name='my-preferences'),
    path('preferences/layout/', UserPreferenceViewSet.as_view({'patch': 'update_layout'}), name='preferences-layout'),
    path('preferences/shortcuts/', UserPreferenceViewSet.as_view({'patch': 'update_shortcuts'}), name='preferences-shortcuts'),
    path('preferences/reset/', UserPreferenceViewSet.as_view({'post': 'reset_to_defaults'}), name='preferences-reset'),

    # Notification preference shortcuts
    path('notifications/me/', NotificationPreferenceViewSet.as_view({'get': 'list', 'patch': 'update_preferences'}), name='my-notifications'),
    path('notifications/channel/', NotificationPreferenceViewSet.as_view({'patch': 'update_channel'}), name='notifications-channel'),
    path('notifications/type/', NotificationPreferenceViewSet.as_view({'patch': 'update_type_setting'}), name='notifications-type'),
    path('notifications/quiet-hours/', NotificationPreferenceViewSet.as_view({'patch': 'update_quiet_hours'}), name='notifications-quiet-hours'),
    path('notifications/digest/', NotificationPreferenceViewSet.as_view({'patch': 'update_digest'}), name='notifications-digest'),

    # Export shortcuts
    path('export/history/', ExportJobViewSet.as_view({'get': 'history'}), name='export-history'),
    path('export/<int:pk>/status/', ExportJobViewSet.as_view({'get': 'status'}), name='export-status'),
    path('export/<int:pk>/download/', ExportJobViewSet.as_view({'get': 'download'}), name='export-download'),
    path('export/<int:pk>/cancel/', ExportJobViewSet.as_view({'delete': 'cancel'}), name='export-cancel'),

    # RBAC shortcuts
    path('roles/initialize/', UserRoleViewSet.as_view({'post': 'initialize_defaults'}), name='roles-initialize'),
    path('permissions/me/', UserRoleAssignmentViewSet.as_view({'get': 'my_roles'}), name='my-permissions'),
    path('permissions/check/', UserRoleAssignmentViewSet.as_view({'post': 'check_permission'}), name='check-permission'),
]
