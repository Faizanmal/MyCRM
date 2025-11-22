from rest_framework import permissions
from .models import OrganizationMember


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the organization.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        organization = getattr(request, 'organization', None)
        if not organization:
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
        
        # Get organization from object
        organization = getattr(obj, 'organization', None)
        if not organization:
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
        
        # Get organization from object
        organization = getattr(obj, 'organization', None)
        if not organization:
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
