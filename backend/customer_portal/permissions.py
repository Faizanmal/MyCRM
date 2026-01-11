"""
Customer Portal Permissions
"""

from rest_framework.permissions import BasePermission


class IsCustomerAuthenticated(BasePermission):
    """
    Permission class for customer portal authentication.
    Checks if the request has a valid customer attached.
    """
    
    def has_permission(self, request, view):
        return hasattr(request, 'customer') and request.customer is not None


class IsCustomerVerified(BasePermission):
    """
    Permission class requiring verified customer account.
    """
    
    def has_permission(self, request, view):
        return (
            hasattr(request, 'customer') and 
            request.customer is not None and
            request.customer.is_verified
        )


class IsPortalEnabled(BasePermission):
    """
    Permission class checking if portal access is enabled for customer.
    """
    
    def has_permission(self, request, view):
        return (
            hasattr(request, 'customer') and 
            request.customer is not None and
            request.customer.portal_access_enabled
        )
