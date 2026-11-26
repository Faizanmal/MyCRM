"""
Rate Limiting & Brute Force Protection Throttles
Protects unauthenticated endpoints (login, 2FA verification, registration)
against brute-force attacks and credential stuffing.
"""
from django.conf import settings
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttles login, 2FA token verification, and registration attempts by client IP.
    Default: 10/minute (overrideable via settings.LOGIN_RATE_THROTTLE_RATE).
    """
    scope = 'login'
    rate = getattr(settings, 'LOGIN_RATE_THROTTLE_RATE', '10/minute')

    def allow_request(self, request, view):
        if not getattr(settings, 'FEATURE_LOGIN_RATE_LIMIT', True):
            return True
        return super().allow_request(request, view)
