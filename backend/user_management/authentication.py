"""
Cookie-Based and Header-Based JWT Authentication
Allows secure, HttpOnly, SameSite=Lax/Strict session authentication
preventing XSS access to tokens while supporting standard Authorization header
and enforcing CSRF protection on mutative cookie-authenticated requests.
"""
from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework import permissions
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieOrHeaderJWTAuthentication(JWTAuthentication):
    """
    Extends SimpleJWT's JWTAuthentication to inspect HttpOnly cookies
    ('access_token' or 'access') when Authorization header is absent.
    Enforces strict CSRF validation on unsafe HTTP methods when authenticating via Cookie.
    """

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for cookie-authenticated mutative requests.
        """
        def dummy_get_response(req):
            return None

        check = CSRFCheck(dummy_get_response)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise PermissionDenied(f"CSRF Failed: {reason}")

    def authenticate(self, request):
        header = self.get_header(request)
        is_cookie_auth = False
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            # Fall back to secure HttpOnly cookie
            raw_token = request.COOKIES.get('access_token') or request.COOKIES.get('access')
            is_cookie_auth = True

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        # Enforce CSRF check for cookie-authenticated requests modifying state
        if is_cookie_auth and request.method not in permissions.SAFE_METHODS:
            if getattr(settings, 'FEATURE_CSRF_COOKIE_ENFORCEMENT', True):
                self.enforce_csrf(request)

        return user, validated_token


def set_auth_cookies(response, access_token: str, refresh_token: str = None, request=None):
    """
    Set secure HttpOnly cookies for access and refresh tokens and ensure CSRF token cookie is set.
    """
    secure = getattr(settings, 'SESSION_COOKIE_SECURE', False)
    samesite = getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')

    # Access Token: HttpOnly, SameSite=Lax, path=/
    access_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
    response.set_cookie(
        key='access_token',
        value=access_token,
        max_age=int(access_lifetime),
        httponly=True,
        secure=secure,
        samesite=samesite,
        path='/'
    )

    # Refresh Token: HttpOnly, SameSite=Lax, path=/api/auth/
    if refresh_token:
        refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            max_age=int(refresh_lifetime),
            httponly=True,
            secure=secure,
            samesite=samesite,
            path='/api/auth/'
        )

    # Ensure CSRF token cookie is generated and returned to client for API requests
    if request:
        get_token(request)


def clear_auth_cookies(response):
    """
    Delete access and refresh cookies across paths.
    """
    samesite = getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')
    response.delete_cookie(key='access_token', path='/', samesite=samesite)
    response.delete_cookie(key='refresh_token', path='/api/auth/', samesite=samesite)
    response.delete_cookie(key='refresh_token', path='/', samesite=samesite)
