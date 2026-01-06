"""
Enhanced Role-Based Access Control (RBAC) System
Provides granular permission management for enterprise CRM
"""

import logging
from functools import wraps

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.http import JsonResponse

User = get_user_model()
logger = logging.getLogger(__name__)


class PermissionManager:
    """Centralized permission management"""

    # Define granular permissions
    PERMISSIONS = {
        # Contact Management
        'contacts.view': 'View contacts',
        'contacts.create': 'Create contacts',
        'contacts.edit': 'Edit contacts',
        'contacts.delete': 'Delete contacts',
        'contacts.export': 'Export contacts',
        'contacts.import': 'Import contacts',

        # Lead Management
        'leads.view': 'View leads',
        'leads.create': 'Create leads',
        'leads.edit': 'Edit leads',
        'leads.delete': 'Delete leads',
        'leads.assign': 'Assign leads',
        'leads.convert': 'Convert leads',
        'leads.export': 'Export leads',

        # Opportunity Management
        'opportunities.view': 'View opportunities',
        'opportunities.create': 'Create opportunities',
        'opportunities.edit': 'Edit opportunities',
        'opportunities.delete': 'Delete opportunities',
        'opportunities.close': 'Close opportunities',
        'opportunities.forecast': 'View forecasting',

        # Task Management
        'tasks.view': 'View tasks',
        'tasks.create': 'Create tasks',
        'tasks.edit': 'Edit tasks',
        'tasks.delete': 'Delete tasks',
        'tasks.assign': 'Assign tasks',

        # Communication
        'communications.view': 'View communications',
        'communications.send': 'Send communications',
        'communications.templates': 'Manage templates',

        # Reporting
        'reports.view': 'View reports',
        'reports.create': 'Create reports',
        'reports.export': 'Export reports',
        'reports.schedule': 'Schedule reports',

        # User Management
        'users.view': 'View users',
        'users.create': 'Create users',
        'users.edit': 'Edit users',
        'users.delete': 'Delete users',
        'users.manage_roles': 'Manage user roles',

        # System Administration
        'system.settings': 'Manage system settings',
        'system.audit': 'View audit logs',
        'system.integrations': 'Manage integrations',
        'system.security': 'Manage security settings',
        'system.api_keys': 'Manage API keys',

        # Data Management
        'data.import': 'Import data',
        'data.export': 'Export data',
        'data.bulk_operations': 'Perform bulk operations',
        'data.delete_all': 'Delete bulk data',
    }

    # Default role permissions
    ROLE_PERMISSIONS = {
        'admin': list(PERMISSIONS.keys()),  # All permissions

        'manager': [
            'contacts.*', 'leads.*', 'opportunities.*', 'tasks.*',
            'communications.view', 'communications.send', 'communications.templates',
            'reports.*',
            'users.view', 'users.edit',
            'data.import', 'data.export', 'data.bulk_operations',
        ],

        'sales_rep': [
            'contacts.view', 'contacts.create', 'contacts.edit',
            'leads.view', 'leads.create', 'leads.edit', 'leads.convert',
            'opportunities.view', 'opportunities.create', 'opportunities.edit', 'opportunities.close',
            'tasks.view', 'tasks.create', 'tasks.edit',
            'communications.view', 'communications.send',
            'reports.view', 'reports.export',
        ],

        'marketing': [
            'contacts.view', 'contacts.create', 'contacts.export',
            'leads.view', 'leads.create', 'leads.export',
            'communications.*',
            'reports.view', 'reports.create', 'reports.export',
            'data.import', 'data.export',
        ],

        'customer_support': [
            'contacts.view', 'contacts.edit',
            'tasks.view', 'tasks.create', 'tasks.edit',
            'communications.view', 'communications.send',
            'reports.view',
        ],
    }

    @classmethod
    def expand_wildcards(cls, permissions):
        """Expand wildcard permissions like 'contacts.*' to all contact permissions"""
        expanded = set()
        for perm in permissions:
            if perm.endswith('.*'):
                module = perm[:-2]
                expanded.update([p for p in cls.PERMISSIONS if p.startswith(f"{module}.")])
            else:
                expanded.add(perm)
        return list(expanded)

    @classmethod
    def get_role_permissions(cls, role):
        """Get all permissions for a role"""
        base_permissions = cls.ROLE_PERMISSIONS.get(role, [])
        return cls.expand_wildcards(base_permissions)

    @classmethod
    def has_permission(cls, user, permission):
        """Check if user has a specific permission"""
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        # Check cache first
        cache_key = f"user_permissions:{user.id}"
        user_permissions = cache.get(cache_key)

        if user_permissions is None:
            # Get permissions from role
            user_permissions = cls.get_role_permissions(user.role)

            # Get custom permissions from database
            from .models import UserPermission
            custom_perms = UserPermission.objects.filter(
                user=user, is_active=True
            ).values_list('permission', 'is_granted')

            # Apply custom permissions
            for perm, is_granted in custom_perms:
                if is_granted and perm not in user_permissions:
                    user_permissions.append(perm)
                elif not is_granted and perm in user_permissions:
                    user_permissions.remove(perm)

            # Cache for 5 minutes
            cache.set(cache_key, user_permissions, 300)

        return permission in user_permissions

    @classmethod
    def clear_user_permission_cache(cls, user):
        """Clear cached permissions for a user"""
        cache_key = f"user_permissions:{user.id}"
        cache.delete(cache_key)


def require_permission(permission):
    """Decorator to check if user has required permission"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not PermissionManager.has_permission(request.user, permission):
                return JsonResponse({
                    'error': 'Permission denied',
                    'required_permission': permission
                }, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permissions):
    """Decorator to check if user has any of the required permissions"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            has_any = any(
                PermissionManager.has_permission(request.user, perm)
                for perm in permissions
            )
            if not has_any:
                return JsonResponse({
                    'error': 'Permission denied',
                    'required_permissions': permissions
                }, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(*permissions):
    """Decorator to check if user has all required permissions"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            has_all = all(
                PermissionManager.has_permission(request.user, perm)
                for perm in permissions
            )
            if not has_all:
                return JsonResponse({
                    'error': 'Permission denied',
                    'required_permissions': permissions
                }, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class RowLevelPermission:
    """Row-level permission checker for fine-grained access control"""

    @staticmethod
    def can_access_record(user, record, permission_type='view'):
        """
        Check if user can access a specific record

        Args:
            user: User object
            record: Model instance
            permission_type: 'view', 'edit', 'delete'
        """
        if user.is_superuser:
            return True

        # Check if user owns the record
        if hasattr(record, 'owner') and record.owner == user:
            return True

        # Check if user is assigned to the record
        if hasattr(record, 'assigned_to') and record.assigned_to == user:
            return True

        # Check team access
        if hasattr(record, 'team'):
            from .models import TeamMember
            is_team_member = TeamMember.objects.filter(
                team=record.team,
                user=user,
                is_active=True
            ).exists()
            if is_team_member:
                return True

        # Check role-based access
        return user.role in ['admin', 'manager']
