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
