"""
Core App - Enterprise Features for MyCRM

This module provides:
- User Preferences & Settings
- Notification System
- Role-Based Access Control (RBAC)
- Data Export/Import
- Authentication & Authorization
- Audit Logging
- Health Monitoring
- Background Tasks (Celery)
- WebSocket Real-time Updates
- Email Notifications
- AI Recommendations

Key Components:
- settings_models: User preferences, roles, export jobs
- notification_service: Multi-channel notification delivery
- rbac_middleware: Permission checking and enforcement
- auth_views: JWT authentication endpoints
- health_views: System health monitoring
- export_tasks: Async data export processing
- celery_tasks: Background job processing

Usage:
    from core.notification_service import notification_service
    from core.rbac_middleware import user_has_permission, HasPermission
    from core.settings_models import UserPreference, UserRole
"""

# Models are imported in apps.py ready() method to avoid AppRegistryNotReady errors
default_app_config = 'core.apps.CoreConfig'
