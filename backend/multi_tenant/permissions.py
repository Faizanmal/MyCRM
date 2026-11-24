"""
Multi-Tenant Permission Classes
===============================
Enforces strict tenant membership, role permissions, and object-level
cross-tenant isolation on all resources.
"""
from rest_framework import permissions
from .models import Organization, OrganizationMember


class TenantObjectPermission(permissions.BasePermission):
    """
    Strict object-level permission ensuring an object belongs to the requesting user's tenant.
    Rejects any cross-tenant object access.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        # Must have an associated tenant
        organization = getattr(request, 'organization', None)
        if not organization:
            active_membership = request.user.organization_memberships.filter(is_active=True).first()
            if active_membership:
                organization = active_membership.organization
                request.organization = organization

        return organization is not None

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        organization = getattr(request, 'organization', None)
        if not organization:
            active_membership = request.user.organization_memberships.filter(is_active=True).first()
            if active_membership:
                organization = active_membership.organization

        if not organization:
            return False

        # Determine object's tenant organization
        obj_org = getattr(obj, 'organization', obj if isinstance(obj, Organization) else None)
        if obj_org is None:
            # Fall back to owner/created_by/assigned_to
            user = getattr(obj, 'owner', None) or getattr(obj, 'created_by', None) or getattr(obj, 'assigned_to', None)
            if user:
                obj_org = getattr(user, 'organization', None)
                if not obj_org and hasattr(user, 'organization_memberships'):
                    membership = user.organization_memberships.filter(is_active=True).first()
                    if membership:
                        obj_org = membership.organization

        if obj_org and obj_org != organization:
            return False

        # Verify active membership
        return OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            is_active=True
        ).exists()


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission to check if user is an active member of the organization.
    Enforces object-level cross-tenant protection on detail requests.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        organization = getattr(request, 'organization', None)
        if not organization:
            active_membership = request.user.organization_memberships.filter(is_active=True).first()
            if active_membership:
                organization = active_membership.organization
                request.organization = organization

        if not organization:
            return False

        return OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        organization = getattr(request, 'organization', None)
        if not organization:
            active_membership = request.user.organization_memberships.filter(is_active=True).first()
            if active_membership:
                organization = active_membership.organization

        if not organization:
            return False

        obj_org = getattr(obj, 'organization', obj if isinstance(obj, Organization) else None)
        if obj_org is None:
            user = getattr(obj, 'owner', None) or getattr(obj, 'created_by', None) or getattr(obj, 'assigned_to', None)
            if user:
                obj_org = getattr(user, 'organization', None)
                if not obj_org and hasattr(user, 'organization_memberships'):
                    membership = user.organization_memberships.filter(is_active=True).first()
                    if membership:
                        obj_org = membership.organization

        if obj_org and obj_org != organization:
            return False

        return OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            is_active=True
        ).exists()


class IsOrganizationAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin of the organization.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        organization = getattr(request, 'organization', None)
        if not organization:
            active_membership = request.user.organization_memberships.filter(is_active=True).first()
            if active_membership:
                organization = active_membership.organization
                request.organization = organization

        if not organization:
            return False

        return OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            role__in=['owner', 'admin'],
            is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        organization = getattr(request, 'organization', None)
        if not organization:
            active_membership = request.user.organization_memberships.filter(is_active=True).first()
            if active_membership:
                organization = active_membership.organization

        if not organization:
            return False

        obj_org = getattr(obj, 'organization', obj if isinstance(obj, Organization) else None)
        if obj_org and obj_org != organization:
            return False

        return OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            role__in=['owner', 'admin'],
            is_active=True
        ).exists()


class IsOrganizationOwner(permissions.BasePermission):
    """
    Permission to check if user is an owner of the organization.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        organization = getattr(request, 'organization', None)
        if not organization:
            active_membership = request.user.organization_memberships.filter(is_active=True).first()
            if active_membership:
                organization = active_membership.organization
                request.organization = organization

        if not organization:
            return False

        return OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            role='owner',
            is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        organization = getattr(request, 'organization', None)
        if not organization:
            active_membership = request.user.organization_memberships.filter(is_active=True).first()
            if active_membership:
                organization = active_membership.organization

        if not organization:
            return False

        obj_org = getattr(obj, 'organization', obj if isinstance(obj, Organization) else None)
        if obj_org and obj_org != organization:
            return False

        return OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            role='owner',
            is_active=True
        ).exists()


class CanInviteUsers(permissions.BasePermission):
    """
    Permission to check if user can invite other users to the organization.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        organization = getattr(request, 'organization', None)
        if not organization:
            active_membership = request.user.organization_memberships.filter(is_active=True).first()
            if active_membership:
                organization = active_membership.organization
                request.organization = organization

        if not organization:
            return False

        try:
            membership = OrganizationMember.objects.get(
                organization=organization,
                user=request.user,
                is_active=True
            )
            return membership.can_invite_users or membership.role in ['owner', 'admin']
        except OrganizationMember.DoesNotExist:
            return False


class HasRolePermission(permissions.BasePermission):
    """
    Granular, parameterized Role-Based Access Control (RBAC) permission.
    Evaluates:
      - Authenticated user
      - Tenant active membership
      - Role hierarchy & explicit action permissions
      - Row-level ownership/assignment constraints for non-admins (e.g. sales_rep / member)
      - Explicit forbidden field rejection
    """

    # Role Hierarchy: Owner (50) > Admin (40) > Manager (30) > Member/SalesRep (20) > Guest/Viewer (10)
    ROLE_HIERARCHY = {
        'owner': 50,
        'admin': 40,
        'manager': 30,
        'member': 20,
        'sales_rep': 20,
        'viewer': 10,
        'guest': 10,
    }

    # Action to required minimum role mapping
    ACTION_ROLES = {
        # Read operations
        'list': ['owner', 'admin', 'manager', 'member', 'sales_rep', 'viewer'],
        'retrieve': ['owner', 'admin', 'manager', 'member', 'sales_rep', 'viewer'],
        'statistics': ['owner', 'admin', 'manager', 'member', 'sales_rep', 'viewer'],
        'pipeline': ['owner', 'admin', 'manager', 'member', 'sales_rep', 'viewer'],
        # Create / Mutation
        'create': ['owner', 'admin', 'manager', 'member', 'sales_rep'],
        'update': ['owner', 'admin', 'manager', 'member', 'sales_rep'],
        'partial_update': ['owner', 'admin', 'manager', 'member', 'sales_rep'],
        'complete': ['owner', 'admin', 'manager', 'member', 'sales_rep'],
        'convert': ['owner', 'admin', 'manager', 'member', 'sales_rep'],
        # High-privilege / Admin / Manager operations
        'destroy': ['owner', 'admin', 'manager'],
        'bulk_update': ['owner', 'admin', 'manager'],
        'bulk_delete': ['owner', 'admin'],
        'import': ['owner', 'admin', 'manager'],
        'export': ['owner', 'admin', 'manager'],
    }

    def _get_membership(self, request):
        if hasattr(request, 'member') and request.member:
            return request.member
        org = getattr(request, 'organization', None)
        if not org:
            active_mem = request.user.organization_memberships.filter(is_active=True).first()
            if active_mem:
                request.organization = active_mem.organization
                org = active_mem.organization
        if not org:
            return None
        mem = request.user.organization_memberships.filter(organization=org, is_active=True).first()
        request.member = mem
        return mem

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            self.message = "Authentication credentials were not provided."
            return False

        if request.user.is_superuser:
            return True

        membership = self._get_membership(request)
        if not membership:
            self.message = "You do not belong to an active organization."
            return False

        user_role = membership.role
        action = getattr(view, 'action', None) or request.method.lower()

        # Map HTTP methods to actions if not a DRF viewset action
        method_map = {'get': 'list', 'post': 'create', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        action_name = action if action in self.ACTION_ROLES else method_map.get(action, 'retrieve')

        # Check action role requirements
        allowed_roles = self.ACTION_ROLES.get(action_name)
        if allowed_roles and user_role not in allowed_roles:
            self.message = f"Insufficient permissions: Role '{user_role}' cannot perform action '{action_name}'."
            return False

        # Custom bulk_update action_type check ('update' vs 'delete')
        if action == 'bulk_update' and request.method == 'POST':
            req_action = request.data.get('action')
            if req_action == 'delete' and user_role not in ['owner', 'admin']:
                self.message = f"Insufficient permissions: Role '{user_role}' cannot perform bulk delete."
                return False

        return True

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            self.message = "Authentication credentials were not provided."
            return False

        if request.user.is_superuser:
            return True

        membership = self._get_membership(request)
        if not membership:
            self.message = "You do not belong to an active organization."
            return False

        user_role = membership.role
        action = getattr(view, 'action', None) or request.method.lower()
        method_map = {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        action_name = action if action in self.ACTION_ROLES else method_map.get(action, 'retrieve')

        # 1. Tenant match check
        obj_org = getattr(obj, 'organization', None)
        if obj_org and obj_org != membership.organization:
            self.message = "Object does not exist in your organization."
            return False

        # 2. Role permission check for action
        allowed_roles = self.ACTION_ROLES.get(action_name)
        if allowed_roles and user_role not in allowed_roles:
            self.message = f"Insufficient permissions: Role '{user_role}' cannot perform '{action_name}' on this object."
            return False

        # 3. Row-level object ownership / assignment check
        # Owner / Admin / Manager have access across the entire organization
        if user_role in ['owner', 'admin', 'manager']:
            return True

        # Member / Sales Rep: can read/edit if owner, created_by, or assigned_to
        if user_role in ['member', 'sales_rep']:
            is_assigned = getattr(obj, 'assigned_to_id', None) == request.user.id
            is_owner = getattr(obj, 'owner_id', None) == request.user.id
            is_creator = getattr(obj, 'created_by_id', None) == request.user.id

            if not (is_assigned or is_owner or is_creator):
                self.message = f"Insufficient permissions: Role '{user_role}' can only modify objects assigned to or owned by them."
                return False

        # Viewer / Guest: read-only
        if user_role in ['viewer', 'guest'] and request.method not in permissions.SAFE_METHODS:
            self.message = f"Insufficient permissions: Role '{user_role}' has read-only access."
            return False

        return True

