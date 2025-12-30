"""
API Rate Limiting
Throttling classes for API endpoints
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """
    Throttle for burst requests (short-term)
    """
    scope = 'burst'
    rate = '60/minute'


class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle for sustained requests (long-term)
    """
    scope = 'sustained'
    rate = '1000/hour'


class AnonBurstRateThrottle(AnonRateThrottle):
    """
    Throttle for anonymous burst requests
    """
    scope = 'anon_burst'
    rate = '20/minute'


class AnonSustainedRateThrottle(AnonRateThrottle):
    """
    Throttle for anonymous sustained requests
    """
    scope = 'anon_sustained'
    rate = '100/hour'


class ExportRateThrottle(UserRateThrottle):
    """
    Special throttle for export operations (resource-intensive)
    """
    scope = 'export'
    rate = '10/hour'


class SearchRateThrottle(UserRateThrottle):
    """
    Throttle for search operations
    """
    scope = 'search'
    rate = '120/minute'


class AIRateThrottle(UserRateThrottle):
    """
    Throttle for AI operations (computationally expensive)
    """
    scope = 'ai'
    rate = '30/minute'


class BulkOperationThrottle(UserRateThrottle):
    """
    Throttle for bulk operations
    """
    scope = 'bulk'
    rate = '5/hour'


class WebhookThrottle(UserRateThrottle):
    """
    Throttle for webhook endpoints
    """
    scope = 'webhook'
    rate = '1000/minute'


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttle for login attempts (security)
    """
    scope = 'login'
    rate = '5/minute'


class PasswordResetThrottle(AnonRateThrottle):
    """
    Throttle for password reset attempts
    """
    scope = 'password_reset'
    rate = '3/hour'


# Default throttle classes for settings.py
DEFAULT_THROTTLE_CLASSES = [
    'core.throttling.BurstRateThrottle',
    'core.throttling.SustainedRateThrottle',
]

# Throttle rates configuration for settings.py
DEFAULT_THROTTLE_RATES = {
    'burst': '60/minute',
    'sustained': '1000/hour',
    'anon_burst': '20/minute',
    'anon_sustained': '100/hour',
    'export': '10/hour',
    'search': '120/minute',
    'ai': '30/minute',
    'bulk': '5/hour',
    'webhook': '1000/minute',
    'login': '5/minute',
    'password_reset': '3/hour',
}
