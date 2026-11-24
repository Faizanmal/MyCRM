"""
Cookie-Based and Header-Based JWT Authentication
Allows secure, HttpOnly, SameSite=Lax/Strict session authentication
preventing XSS access to tokens while supporting standard Authorization header.
"""
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieOrHeaderJWTAuthentication(JWTAuthentication):
    """
    Extends SimpleJWT's JWTAuthentication to inspect HttpOnly cookies
    ('access_token' or 'access') when Authorization header is absent.
    """

    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            # Fall back to secure HttpOnly cookie
            raw_token = request.COOKIES.get('access_token') or request.COOKIES.get('access')

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token


def set_auth_cookies(response, access_token: str, refresh_token: str = None):
    """
    Set secure HttpOnly cookies for access and refresh tokens.
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


def clear_auth_cookies(response):
    """
    Delete access and refresh cookies across paths.
    """
    samesite = getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')
    response.delete_cookie(key='access_token', path='/', samesite=samesite)
    response.delete_cookie(key='refresh_token', path='/api/auth/', samesite=samesite)
    response.delete_cookie(key='refresh_token', path='/', samesite=samesite)
