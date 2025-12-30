"""
RBAC Middleware and Permission Classes
Role-based access control for Django REST Framework
"""

from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.permissions import BasePermission

import logging

logger = logging.getLogger(__name__)


# ==================== Permission Constants ====================

class Permissions:
    """Define all available permissions"""
    
    # Dashboard
    VIEW_DASHBOARD = 'view_dashboard'
    VIEW_ADMIN_DASHBOARD = 'view_admin_dashboard'
    VIEW_ANALYTICS = 'view_analytics'
    
    # Contacts
    VIEW_CONTACTS = 'view_contacts'
    CREATE_CONTACTS = 'create_contacts'
    EDIT_CONTACTS = 'edit_contacts'
    DELETE_CONTACTS = 'delete_contacts'
    EXPORT_CONTACTS = 'export_contacts'
    IMPORT_CONTACTS = 'import_contacts'
    
    # Deals
    VIEW_DEALS = 'view_deals'
    CREATE_DEALS = 'create_deals'
    EDIT_DEALS = 'edit_deals'
    DELETE_DEALS = 'delete_deals'
    CLOSE_DEALS = 'close_deals'
    
    # Tasks
    VIEW_TASKS = 'view_tasks'
    CREATE_TASKS = 'create_tasks'
    EDIT_TASKS = 'edit_tasks'
    DELETE_TASKS = 'delete_tasks'
    ASSIGN_TASKS = 'assign_tasks'
    
    # Team
    VIEW_TEAM = 'view_team'
    MANAGE_TEAM = 'manage_team'
    INVITE_USERS = 'invite_users'
    REMOVE_USERS = 'remove_users'
    ASSIGN_ROLES = 'assign_roles'
    
    # Settings
    VIEW_SETTINGS = 'view_settings'
    MANAGE_SETTINGS = 'manage_settings'
    MANAGE_INTEGRATIONS = 'manage_integrations'
    VIEW_BILLING = 'view_billing'
    MANAGE_BILLING = 'manage_billing'
    
    # Reports
    VIEW_REPORTS = 'view_reports'
    CREATE_REPORTS = 'create_reports'
    EXPORT_REPORTS = 'export_reports'
    
    # Admin
    ACCESS_ADMIN = 'access_admin'
    MANAGE_ORGANIZATION = 'manage_organization'
    VIEW_AUDIT_LOG = 'view_audit_log'


# ==================== Permission Helper Functions ====================

def get_user_permissions(user):
    """
    Get all permissions for a user based on their roles
    Results are cached for performance
    """
    if not user or not user.is_authenticated:
        return set()
    
    # Check cache first
    cache_key = f'user_permissions_{user.id}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Superusers have all permissions
    if user.is_superuser:
        return set([
            getattr(Permissions, attr)
            for attr in dir(Permissions)
            if not attr.startswith('_')
        ])
    
    # Staff users have admin permissions
    if user.is_staff:
        from .settings_models import UserRole
        try:
            admin_role = UserRole.objects.get(name='admin')
            return set(admin_role.permissions)
        except UserRole.DoesNotExist:
            pass
    
    # Get permissions from role assignments
    permissions = set()
    try:
        from .settings_models import UserRoleAssignment
        assignments = UserRoleAssignment.objects.filter(user=user).select_related('role')
        
        for assignment in assignments:
            permissions.update(assignment.role.permissions or [])
    except Exception as e:
        logger.warning(f"Failed to get role assignments: {e}")
    
    # Cache for 5 minutes
    cache.set(cache_key, permissions, 300)
    
    return permissions


def user_has_permission(user, permission):
    """Check if user has a specific permission"""
    permissions = get_user_permissions(user)
    return permission in permissions


def user_has_any_permission(user, permissions):
    """Check if user has any of the given permissions"""
    user_permissions = get_user_permissions(user)
    return bool(user_permissions.intersection(set(permissions)))


def user_has_all_permissions(user, permissions):
    """Check if user has all of the given permissions"""
    user_permissions = get_user_permissions(user)
    return set(permissions).issubset(user_permissions)


def invalidate_user_permissions(user_id):
    """Invalidate cached permissions for a user"""
    cache.delete(f'user_permissions_{user_id}')


# ==================== DRF Permission Classes ====================

class HasPermission(BasePermission):
    """
    Permission class that checks for specific permissions
    
    Usage:
        class MyView(APIView):
            permission_classes = [HasPermission]
            required_permission = 'view_contacts'
    """
    
    def has_permission(self, request, view):
        required = getattr(view, 'required_permission', None)
        if not required:
            return True
        
        return user_has_permission(request.user, required)


class HasAnyPermission(BasePermission):
    """
    Permission class that checks for any of multiple permissions
    
    Usage:
        class MyView(APIView):
            permission_classes = [HasAnyPermission]
            required_permissions = ['view_contacts', 'view_deals']
    """
    
    def has_permission(self, request, view):
        required = getattr(view, 'required_permissions', [])
        if not required:
            return True
        
        return user_has_any_permission(request.user, required)


class HasAllPermissions(BasePermission):
    """
    Permission class that checks for all required permissions
    """
    
    def has_permission(self, request, view):
        required = getattr(view, 'required_permissions', [])
        if not required:
            return True
        
        return user_has_all_permissions(request.user, required)


class HasMinimumRole(BasePermission):
    """
    Permission class that checks for minimum role level
    
    Usage:
        class MyView(APIView):
            permission_classes = [HasMinimumRole]
            minimum_role = 'manager'  # or role level number
    """
    
    role_levels = {
        'guest': 0,
        'viewer': 1,
        'sales_rep': 2,
        'manager': 3,
        'admin': 4,
    }
    
    def has_permission(self, request, view):
        minimum = getattr(view, 'minimum_role', None)
        if not minimum:
            return True
        
        user = request.user
        
        # Superusers always pass
        if user.is_superuser:
            return True
        
        # Get minimum level
        if isinstance(minimum, str):
            required_level = self.role_levels.get(minimum, 0)
        else:
            required_level = minimum
        
        # Staff is treated as admin
        if user.is_staff:
            return required_level <= 4
        
        # Check user's role level
        try:
            from .settings_models import UserRoleAssignment
            assignments = UserRoleAssignment.objects.filter(user=user).select_related('role')
            
            user_level = max([a.role.level for a in assignments]) if assignments else 0
            return user_level >= required_level
        except Exception:
            return False


class IsAdmin(BasePermission):
    """Permission class that only allows admin users"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        return user_has_permission(request.user, Permissions.ACCESS_ADMIN)


class IsManager(BasePermission):
    """Permission class that allows managers and above"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        return user_has_permission(request.user, Permissions.MANAGE_TEAM)


# ==================== Decorators ====================

def require_permission(permission):
    """
    Decorator to require a specific permission
    
    Usage:
        @require_permission('view_contacts')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not user_has_permission(request.user, permission):
                return JsonResponse(
                    {'error': 'Permission denied', 'required': permission},
                    status=403
                )
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def require_any_permission(*permissions):
    """
    Decorator to require any of multiple permissions
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not user_has_any_permission(request.user, permissions):
                return JsonResponse(
                    {'error': 'Permission denied', 'required_any': permissions},
                    status=403
                )
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def require_all_permissions(*permissions):
    """
    Decorator to require all specified permissions
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not user_has_all_permissions(request.user, permissions):
                return JsonResponse(
                    {'error': 'Permission denied', 'required_all': permissions},
                    status=403
                )
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def require_role(role_name):
    """
    Decorator to require a specific role
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            user = request.user
            
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            try:
                from .settings_models import UserRoleAssignment
                has_role = UserRoleAssignment.objects.filter(
                    user=user,
                    role__name=role_name
                ).exists()
                
                if not has_role:
                    return JsonResponse(
                        {'error': 'Permission denied', 'required_role': role_name},
                        status=403
                    )
            except Exception:
                return JsonResponse({'error': 'Permission check failed'}, status=500)
            
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


# ==================== Middleware ====================

class RBACMiddleware:
    """
    Middleware to attach permissions to request object
    
    After this middleware runs, you can access:
        request.permissions - set of user's permissions
        request.has_permission(perm) - check if user has permission
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Attach permissions helper to request
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.permissions = get_user_permissions(request.user)
            request.has_permission = lambda p: p in request.permissions
            request.has_any_permission = lambda ps: bool(request.permissions.intersection(set(ps)))
            request.has_all_permissions = lambda ps: set(ps).issubset(request.permissions)
        else:
            request.permissions = set()
            request.has_permission = lambda p: False
            request.has_any_permission = lambda ps: False
            request.has_all_permissions = lambda ps: False
        
        response = self.get_response(request)
        return response


# ==================== Route Protection Mixin ====================

class PermissionRequiredMixin:
    """
    Mixin for views that require specific permissions
    
    Usage:
        class MyView(PermissionRequiredMixin, APIView):
            required_permission = 'view_contacts'
            # or
            required_permissions = ['view_contacts', 'edit_contacts']
            require_all = True  # default False
    """
    
    required_permission = None
    required_permissions = None
    require_all = False
    
    def check_permissions(self, request):
        super().check_permissions(request)
        
        # Check single permission
        if self.required_permission:
            if not user_has_permission(request.user, self.required_permission):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    f"You don't have the required permission: {self.required_permission}"
                )
        
        # Check multiple permissions
        if self.required_permissions:
            if self.require_all:
                if not user_has_all_permissions(request.user, self.required_permissions):
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied(
                        f"You need all of these permissions: {self.required_permissions}"
                    )
            else:
                if not user_has_any_permission(request.user, self.required_permissions):
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied(
                        f"You need at least one of these permissions: {self.required_permissions}"
                    )
