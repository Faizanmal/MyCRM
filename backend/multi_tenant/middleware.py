from threading import local
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from .models import Organization, OrganizationMember

_thread_locals = local()


def get_current_organization():
    """Get the current organization from thread-local storage."""
    return getattr(_thread_locals, 'organization', None)


def get_current_user():
    """Get the current user from thread-local storage."""
    return getattr(_thread_locals, 'user', None)


def set_current_organization(organization):
    """Set the current organization in thread-local storage."""
    _thread_locals.organization = organization


def set_current_user(user):
    """Set the current user in thread-local storage."""
    _thread_locals.user = user


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware that identifies the tenant/organization for each request.
    Supports multiple methods of tenant identification:
    1. Subdomain (e.g., acme.mycrm.com)
    2. Custom domain (e.g., crm.acme.com)
    3. Header (X-Organization-Slug)
    4. URL path (/org/acme/...)
    """

    def process_request(self, request):
        organization = None
        
        # Skip for admin, auth, and static URLs
        if request.path.startswith(('/admin/', '/api/auth/', '/static/', '/media/')):
            return None
        
        # Method 1: Check for organization in header (API requests)
        org_slug = request.headers.get('X-Organization-Slug')
        if org_slug:
            try:
                organization = Organization.objects.get(slug=org_slug, status='active')
            except Organization.DoesNotExist:
                pass
        
        # Method 2: Check for custom domain
        if not organization:
            host = request.get_host().split(':')[0]  # Remove port
            try:
                organization = Organization.objects.get(domain=host, status='active')
            except Organization.DoesNotExist:
                pass
        
        # Method 3: Check for subdomain
        if not organization:
            host = request.get_host().split(':')[0]
            parts = host.split('.')
            if len(parts) > 2:  # Has subdomain
                subdomain = parts[0]
                if subdomain not in ['www', 'api', 'admin']:
                    try:
                        organization = Organization.objects.get(slug=subdomain, status='active')
                    except Organization.DoesNotExist:
                        pass
        
        # Method 4: Check session (fallback for web interface)
        if not organization and request.user.is_authenticated:
            org_id = request.session.get('organization_id')
            if org_id:
                try:
                    organization = Organization.objects.get(id=org_id, status='active')
                except Organization.DoesNotExist:
                    pass
        
        # Set organization in thread-local storage
        if organization:
            set_current_organization(organization)
            request.organization = organization
            
            # Verify user has access to this organization
            if request.user.is_authenticated and not request.user.is_superuser:
                try:
                    membership = OrganizationMember.objects.get(
                        organization=organization,
                        user=request.user,
                        is_active=True
                    )
                    request.organization_member = membership
                except OrganizationMember.DoesNotExist:
                    # User doesn't have access to this organization
                    return redirect('unauthorized')
        
        # Set user in thread-local storage
        if request.user.is_authenticated:
            set_current_user(request.user)
        
        return None

    def process_response(self, request, response):
        # Clean up thread-local storage
        if hasattr(_thread_locals, 'organization'):
            del _thread_locals.organization
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        return response
