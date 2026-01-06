"""
Enhanced Security Middleware and Utilities

Provides comprehensive security features including:
- Security headers
- Request validation
- Anomaly detection
- Security event logging
"""

import json
import logging
import time
from functools import wraps
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy
        if not settings.DEBUG:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' wss: https:; "
                "frame-ancestors 'none';"
            )
            response['Content-Security-Policy'] = csp

        # HSTS header for production
        if not settings.DEBUG and request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        # Permissions Policy
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), gyroscope=(), '
            'magnetometer=(), microphone=(), payment=(), usb=()'
        )

        return response


class RequestValidationMiddleware:
    """
    Validate incoming requests for potential security issues.
    """

    SUSPICIOUS_PATTERNS = [
        '../', '..\\',  # Path traversal
        '<script', '</script>',  # XSS
        'javascript:',  # XSS via javascript protocol
        'data:text/html',  # XSS via data URI
        'SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ', 'DROP ',  # SQL injection
        'UNION SELECT',  # SQL injection
        '; --', '/*', '*/',  # SQL comments
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Check for suspicious patterns in request
        if self._is_suspicious_request(request):
            logger.warning(
                f'Suspicious request detected from {self._get_client_ip(request)}: '
                f'{request.method} {request.path}'
            )
            # Log security event
            SecurityEventLogger.log_event(
                event_type='suspicious_request',
                request=request,
                details={'method': request.method, 'path': request.path}
            )

            # Block obviously malicious requests
            if self._is_malicious_request(request):
                return JsonResponse({'error': 'Request blocked'}, status=400)

        return self.get_response(request)

    def _is_suspicious_request(self, request: HttpRequest) -> bool:
        """Check if request contains suspicious patterns."""
        # Check URL path
        path = request.path.lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.lower() in path:
                return True

        # Check query parameters
        query_string = request.META.get('QUERY_STRING', '').lower()
        return any(pattern.lower() in query_string for pattern in self.SUSPICIOUS_PATTERNS)

    def _is_malicious_request(self, request: HttpRequest) -> bool:
        """Check if request is clearly malicious."""
        path = request.path.lower()

        # Path traversal attempts
        if '../' in path or '..\\' in path:
            return True

        # Common exploit paths
        exploit_paths = ['/wp-admin', '/phpmyadmin', '/.env', '/config.php']
        return any(exploit_path in path for exploit_path in exploit_paths)

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class RateLimitMiddleware:
    """
    Enhanced rate limiting with per-endpoint and per-user limits.
    """

    # Rate limits: (requests, window_seconds)
    DEFAULT_LIMITS = {
        'default': (100, 3600),  # 100 requests per hour
        'auth': (10, 60),  # 10 auth attempts per minute
        'api': (1000, 3600),  # 1000 API calls per hour
        'export': (10, 3600),  # 10 exports per hour
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Skip rate limiting for certain paths
        if self._should_skip(request):
            return self.get_response(request)

        # Determine rate limit category
        category = self._get_category(request)
        limit, window = self.DEFAULT_LIMITS.get(category, self.DEFAULT_LIMITS['default'])

        # Get rate limit key
        key = self._get_rate_limit_key(request, category)

        # Check and update rate limit
        is_limited, remaining, reset_time = self._check_rate_limit(key, limit, window)

        if is_limited:
            logger.warning(f'Rate limit exceeded for {key}')
            SecurityEventLogger.log_event(
                event_type='rate_limit_exceeded',
                request=request,
                details={'category': category, 'key': key}
            )

            response = JsonResponse(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=429
            )
            response['Retry-After'] = str(reset_time)
            response['X-RateLimit-Limit'] = str(limit)
            response['X-RateLimit-Remaining'] = '0'
            response['X-RateLimit-Reset'] = str(reset_time)
            return response

        # Process request and add rate limit headers
        response = self.get_response(request)
        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(reset_time)

        return response

    def _should_skip(self, request: HttpRequest) -> bool:
        """Check if rate limiting should be skipped."""
        skip_paths = ['/api/v1/healthz/', '/api/v1/ping/', '/static/', '/media/']
        return any(request.path.startswith(path) for path in skip_paths)

    def _get_category(self, request: HttpRequest) -> str:
        """Determine rate limit category based on request."""
        path = request.path.lower()

        if '/auth/' in path or '/login/' in path or '/register/' in path:
            return 'auth'
        elif '/export/' in path or '/download/' in path:
            return 'export'
        elif '/api/' in path:
            return 'api'
        return 'default'

    def _get_rate_limit_key(self, request: HttpRequest, category: str) -> str:
        """Generate rate limit key."""
        user_id = request.user.id if request.user.is_authenticated else 'anon'
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown'))
        if ',' in ip:
            ip = ip.split(',')[0].strip()

        return f'ratelimit:{category}:{user_id}:{ip}'

    def _check_rate_limit(self, key: str, limit: int, window: int) -> tuple:
        """Check and update rate limit counter."""
        now = int(time.time())
        window_start = now - (now % window)
        cache_key = f'{key}:{window_start}'

        try:
            current = cache.get(cache_key, 0)

            if current >= limit:
                reset_time = window_start + window - now
                return True, 0, reset_time

            cache.set(cache_key, current + 1, timeout=window)
            remaining = limit - current - 1
            reset_time = window_start + window - now

            return False, remaining, reset_time
        except Exception:
            # If cache is unavailable, allow request
            return False, limit, window


class SecurityEventLogger:
    """
    Log security events for monitoring and alerting.
    """

    EVENT_TYPES = [
        'login_success', 'login_failure', 'logout',
        'password_change', 'password_reset',
        'suspicious_request', 'rate_limit_exceeded',
        'permission_denied', 'data_access',
        'admin_action', 'api_key_usage'
    ]

    @classmethod
    def log_event(
        cls,
        event_type: str,
        request: HttpRequest | None = None,
        user=None,
        details: dict[str, Any] | None = None
    ) -> None:
        """Log a security event."""
        if event_type not in cls.EVENT_TYPES:
            logger.warning(f'Unknown security event type: {event_type}')

        event_data = {
            'type': event_type,
            'timestamp': timezone.now().isoformat(),
            'details': details or {},
        }

        if request:
            event_data.update({
                'ip': cls._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown')[:256],
                'path': request.path,
                'method': request.method,
            })

        if user:
            event_data['user_id'] = user.id if hasattr(user, 'id') else str(user)
        elif request and hasattr(request, 'user') and request.user.is_authenticated:
            event_data['user_id'] = request.user.id

        # Log to standard logger
        logger.info(f'SECURITY_EVENT: {json.dumps(event_data)}')

        # Store in cache for real-time monitoring
        cls._store_event(event_data)

    @classmethod
    def _get_client_ip(cls, request: HttpRequest) -> str:
        """Get client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

    @classmethod
    def _store_event(cls, event_data: dict[str, Any]) -> None:
        """Store event in cache for real-time access."""
        try:
            events_key = 'security_events'
            events = cache.get(events_key, [])
            events.append(event_data)

            # Keep only last 1000 events
            if len(events) > 1000:
                events = events[-1000:]

            cache.set(events_key, events, timeout=86400)  # 24 hours
        except Exception:
            pass  # Silently fail

    @classmethod
    def get_recent_events(
        cls,
        event_type: str | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get recent security events."""
        try:
            events = cache.get('security_events', [])

            if event_type:
                events = [e for e in events if e.get('type') == event_type]

            return events[-limit:]
        except Exception:
            return []


def require_https(view_func):
    """Decorator to require HTTPS for a view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.is_secure() and not settings.DEBUG:
            return JsonResponse(
                {'error': 'HTTPS required'},
                status=403
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def log_security_event(event_type: str):
    """Decorator to log security events for a view."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)

            SecurityEventLogger.log_event(
                event_type=event_type,
                request=request,
                details={'status_code': getattr(response, 'status_code', None)}
            )

            return response
        return wrapper
    return decorator


def validate_content_type(allowed_types: list[str]):
    """Decorator to validate request content type."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            content_type = request.content_type

            if request.method in ['POST', 'PUT', 'PATCH'] and content_type:
                if not any(allowed in content_type for allowed in allowed_types):
                    return JsonResponse(
                        {'error': f'Content-Type must be one of: {", ".join(allowed_types)}'},
                        status=415
                    )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
