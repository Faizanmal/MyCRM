"""
Multi-Tenant Boundary & Context Middleware
==========================================
Enforces strict tenant isolation, async-safe context propagation via contextvars,
JWT pre-authentication for header validation, and fail-closed security.
Eliminates unsafe thread-locals and automatic default fallback in production.
"""
import contextlib
import contextvars
import logging
import os
import uuid
from typing import Optional

from django.http import HttpResponseForbidden, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Organization, OrganizationMember

logger = logging.getLogger('multi_tenant.security')

# Async-safe, task-isolated contextvars for tenant and user context
_current_organization_ctx = contextvars.ContextVar('current_organization', default=None)
_current_user_ctx = contextvars.ContextVar('current_user', default=None)
_current_member_ctx = contextvars.ContextVar('current_member', default=None)


def get_current_organization() -> Optional[Organization]:
    """Get the current organization from async-safe contextvars."""
    return _current_organization_ctx.get()


def get_current_user():
    """Get the current user from async-safe contextvars."""
    return _current_user_ctx.get()


def get_current_member() -> Optional[OrganizationMember]:
    """Get the current organization member from async-safe contextvars."""
    return _current_member_ctx.get()


def set_current_organization(organization: Optional[Organization]):
    """Set the current organization in async-safe contextvars."""
    _current_organization_ctx.set(organization)


def set_current_user(user):
    """Set the current user in async-safe contextvars."""
    _current_user_ctx.set(user)


def set_current_member(member: Optional[OrganizationMember]):
    """Set the current organization member in async-safe contextvars."""
    _current_member_ctx.set(member)


def reset_tenant_context():
    """Reset all tenant context variables."""
    _current_organization_ctx.set(None)
    _current_user_ctx.set(None)
    _current_member_ctx.set(None)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware that identifies and strictly validates the tenant/organization for each request.
    Enforces fail-closed multi-tenant boundary security.
    """

    EXCLUDED_PREFIXES = (
        '/admin/',
        '/api/auth/',
        '/api/schema/',
        '/api/docs/',
        '/api/redoc/',
        '/static/',
        '/media/',
        '/api/health/',
        '/health/',
    )

    SYSTEM_SUBDOMAINS = (
        'www',
        'api',
        'admin',
        'app',
        'localhost',
        '127.0.0.1',
    )

    @classmethod
    def is_strict_enforcement(cls) -> bool:
        """Feature flag for strict tenant enforcement."""
        return os.getenv('TENANT_STRICT_ENFORCEMENT', 'True').lower() in ('true', '1', 'yes')

    @classmethod
    def is_auto_default_disabled(cls) -> bool:
        """Feature flag to prevent auto-creating default tenant in production."""
        return os.getenv('TENANT_AUTO_DEFAULT_DISABLED', 'True').lower() in ('true', '1', 'yes')

    def _is_api_request(self, request) -> bool:
        """Determines if the incoming request expects a JSON API response."""
        return (
            request.path.startswith('/api/')
            or request.headers.get('Accept') == 'application/json'
            or request.headers.get('Content-Type') == 'application/json'
        )

    def _preauthenticate_jwt(self, request):
        """
        Extract and authenticate user via JWT before tenant membership validation
        since DRF authentication normally occurs inside view dispatch.
        """
        if not getattr(request, 'user', None) or request.user.is_anonymous:
            try:
                from user_management.authentication import CookieOrHeaderJWTAuthentication
                authenticator = CookieOrHeaderJWTAuthentication()
                auth_result = authenticator.authenticate(request)
                if auth_result:
                    request.user, request.auth = auth_result
            except Exception:
                # Invalid token will be properly handled by DRF permission classes
                pass

    def process_request(self, request):
        # Always reset context at the start of a new request
        reset_tenant_context()

        request.organization = None
        request.organization_member = None

        correlation_id = request.headers.get('X-Correlation-ID') or str(uuid.uuid4())
        request.correlation_id = correlation_id

        # Skip tenant resolution for static, admin, and auth endpoints
        if request.path.startswith(self.EXCLUDED_PREFIXES):
            return None

        # Pre-authenticate JWT to establish request.user for membership checks
        self._preauthenticate_jwt(request)

        organization = None
        membership = None
        requested_explicitly = False

        try:
            # Method 1: Check explicit organization header (X-Organization-Slug or X-Tenant-ID)
            org_slug = request.headers.get('X-Organization-Slug')
            tenant_id = request.headers.get('X-Tenant-ID')

            if org_slug:
                requested_explicitly = True
                with contextlib.suppress(Organization.DoesNotExist):
                    organization = Organization.objects.get(slug=org_slug, status='active')

            elif tenant_id:
                requested_explicitly = True
                with contextlib.suppress(Organization.DoesNotExist, ValueError):
                    organization = Organization.objects.get(id=tenant_id, status='active')

            # Method 2: Check custom domain
            if not organization:
                host = request.get_host().split(':')[0]
                if host not in ('localhost', '127.0.0.1', 'testserver'):
                    with contextlib.suppress(Organization.DoesNotExist):
                        organization = Organization.objects.get(domain=host, status='active')
                        if organization:
                            requested_explicitly = True

            # Method 3: Check subdomain (e.g., acme.mycrm.com)
            if not organization:
                host = request.get_host().split(':')[0]
                parts = host.split('.')
                if len(parts) > 2 and parts[0] not in self.SYSTEM_SUBDOMAINS:
                    subdomain = parts[0]
                    with contextlib.suppress(Organization.DoesNotExist):
                        organization = Organization.objects.get(slug=subdomain, status='active')
                        if organization:
                            requested_explicitly = True

            # Method 4: Session fallback for web interface
            if not organization and request.user.is_authenticated:
                org_id = request.session.get('organization_id') if hasattr(request, 'session') else None
                if org_id:
                    with contextlib.suppress(Organization.DoesNotExist):
                        organization = Organization.objects.get(id=org_id, status='active')

            # Method 5: Auto-resolve user's primary organization if authenticated and no explicit tenant given
            if not organization and request.user.is_authenticated:
                # Check user.organization attribute or active membership
                org = getattr(request.user, 'organization', None)
                if org and org.status == 'active':
                    organization = org
                else:
                    active_membership = request.user.organization_memberships.filter(
                        organization__status='active',
                        is_active=True
                    ).select_related('organization').first()
                    if active_membership:
                        organization = active_membership.organization
                        membership = active_membership

        except Exception as e:
            logger.error(f"[{correlation_id}] Error during tenant resolution: {e}", exc_info=True)

        # -------------------------------------------------------------
        # Membership Authorization & Boundary Security Check
        # -------------------------------------------------------------
        if organization:
            # If user is authenticated and not superuser, verify membership
            if request.user.is_authenticated and not request.user.is_superuser:
                if not membership:
                    membership = OrganizationMember.objects.filter(
                        organization=organization,
                        user=request.user,
                        is_active=True
                    ).first()

                if not membership:
                    # User attempted to access an organization they do not belong to
                    logger.warning(
                        f"[{correlation_id}] SECURITY ALERT: User {request.user.id} ({request.user.username}) "
                        f"attempted unauthorized access to Organization '{organization.slug}' ({organization.id})."
                    )
                    if self._is_api_request(request):
                        return JsonResponse({
                            'error': f"Forbidden: You do not have access to organization '{organization.slug}'.",
                            'code': 'tenant_forbidden',
                            'correlation_id': correlation_id
                        }, status=403)
                    else:
                        return HttpResponseForbidden(f"Forbidden: You are not a member of organization '{organization.slug}'.")

            # Store verified tenant on request and async contextvars
            request.organization = organization
            request.organization_member = membership
            set_current_organization(organization)
            set_current_member(membership)
            set_current_user(request.user)

        else:
            # Ambiguous or unresolvable tenant
            if self.is_strict_enforcement() and request.user.is_authenticated and not request.user.is_superuser:
                # If an explicit organization header was provided but does not exist
                if requested_explicitly:
                    logger.warning(f"[{correlation_id}] Requested organization not found or inactive: {org_slug or tenant_id}")
                    if self._is_api_request(request):
                        return JsonResponse({
                            'error': 'Forbidden: Requested organization not found or inactive.',
                            'code': 'invalid_tenant',
                            'correlation_id': correlation_id
                        }, status=403)
                    else:
                        return HttpResponseForbidden("Forbidden: Requested organization not found.")

        if request.user.is_authenticated:
            set_current_user(request.user)

        return None

    def process_response(self, request, response):
        """Clean up async-safe contextvars to prevent ambient leakage."""
        reset_tenant_context()
        return response
