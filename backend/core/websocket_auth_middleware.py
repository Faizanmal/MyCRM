"""
WebSocket Authentication Middleware for Django Channels

Authenticates WebSocket connections using either:
1. Standard Django session cookies (HttpOnly sessionid).
2. JWT Access Tokens passed via query string (?token=<jwt>), cookie (access_token),
   or Sec-WebSocket-Protocol headers.

Resolves tenant context and guarantees fail-closed behavior for inactive or revoked users.
"""

import logging
from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_jwt(token_string: str):
    """Validate JWT access token and return user if active and valid"""
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth import get_user_model
        from multi_tenant.models import OrganizationMember

        User = get_user_model()
        token = AccessToken(token_string)
        user_id = token.get('user_id')
        if not user_id:
            return AnonymousUser(), None

        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            return AnonymousUser(), None

        # Resolve primary active organization membership
        membership = OrganizationMember.objects.filter(
            user=user,
            is_active=True
        ).select_related('organization').first()

        tenant_id = str(membership.organization_id) if membership else None
        return user, tenant_id
    except Exception as e:
        logger.debug("WebSocket JWT validation failed: %s", str(e))
        return AnonymousUser(), None


@database_sync_to_async
def resolve_tenant_for_user(user):
    """Resolve active tenant UUID for a session-authenticated user"""
    if not user or user.is_anonymous or not user.is_active:
        return None
    try:
        from multi_tenant.models import OrganizationMember
        membership = OrganizationMember.objects.filter(
            user=user,
            is_active=True
        ).first()
        return str(membership.organization_id) if membership else None
    except Exception:
        return None


class JWTOrSessionAuthMiddleware(BaseMiddleware):
    """
    ASGI middleware that authenticates WebSocket connections via JWT or Session
    and attaches user + tenant_id to ASGI scope.
    """

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        user = scope.get('user')
        tenant_id = None

        # If user is not yet authenticated via session or is anonymous, check JWT
        if not user or user.is_anonymous:
            token = self._extract_token(scope)
            if token:
                user, tenant_id = await get_user_from_jwt(token)
                scope['user'] = user

        # If user is authenticated (via session or JWT), resolve tenant if missing
        if user and user.is_authenticated and not tenant_id:
            tenant_id = await resolve_tenant_for_user(user)

        scope['tenant_id'] = tenant_id

        return await super().__call__(scope, receive, send)

    def _extract_token(self, scope) -> str | None:
        """Extract JWT token from query string, cookies, or headers"""
        # 1. Query string: ?token=...
        query_string = scope.get('query_string', b'').decode('utf-8')
        if query_string:
            params = parse_qs(query_string)
            if 'token' in params and params['token']:
                return params['token'][0]

        # 2. Cookies: access_token=...
        headers = dict(scope.get('headers', []))
        cookie_header = headers.get(b'cookie', b'').decode('utf-8')
        if cookie_header:
            from http.cookies import SimpleCookie
            cookie = SimpleCookie()
            try:
                cookie.load(cookie_header)
                if 'access_token' in cookie:
                    return cookie['access_token'].value
            except Exception:
                pass

        # 3. Sec-WebSocket-Protocol header: e.g. "token, <jwt>"
        protocol_header = headers.get(b'sec-websocket-protocol', b'').decode('utf-8')
        if protocol_header:
            parts = [p.strip() for p in protocol_header.split(',')]
            if len(parts) >= 2 and parts[0] == 'token':
                return parts[1]

        return None


def JWTOrSessionAuthMiddlewareStack(inner):
    """Combine AuthMiddlewareStack (Session) with JWTOrSessionAuthMiddleware"""
    return AuthMiddlewareStack(JWTOrSessionAuthMiddleware(inner))
