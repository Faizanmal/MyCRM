"""
Security Middleware for MyCRM
Implements comprehensive security headers and protections
"""

import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add comprehensive security headers to all responses
    """

    def process_response(self, request, response):
        # Content Security Policy
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.sentry.io; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )

        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'

        # X-Frame-Options
        response['X-Frame-Options'] = 'DENY'

        # X-XSS-Protection (for legacy browsers)
        response['X-XSS-Protection'] = '1; mode=block'

        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions Policy (formerly Feature-Policy)
        response['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

        # Strict-Transport-Security (HSTS) - only in production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all requests for security auditing
    """

    def process_request(self, request):
        request._start_time = time.time()

        # Log suspicious requests
        if self._is_suspicious(request):
            logger.warning(
                f"Suspicious request detected: "
                f"IP={self._get_client_ip(request)} "
                f"Path={request.path} "
                f"Method={request.method} "
                f"User-Agent={request.META.get('HTTP_USER_AGENT', 'Unknown')}"
            )

    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time

            # Log slow requests
            if duration > 2.0:  # 2 seconds threshold
                logger.warning(
                    f"Slow request detected: "
                    f"Path={request.path} "
                    f"Duration={duration:.2f}s "
                    f"Status={response.status_code}"
                )

        return response

    def _is_suspicious(self, request):
        """Check for suspicious request patterns"""
        path = request.path.lower()

        # Check for common attack patterns
        suspicious_patterns = [
            '../', '..\\', '<script', 'javascript:',
            'eval(', 'exec(', '__import__',
            'union select', 'drop table', '; drop',
            '/etc/passwd', '/proc/', 'cmd.exe'
        ]

        for pattern in suspicious_patterns:
            if pattern in path:
                return True

            # Check query parameters
            for value in request.GET.values():
                if pattern in str(value).lower():
                    return True

        return False

    def _get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        return ip


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    Restrict admin access to whitelisted IPs
    """

    def process_request(self, request):
        # Only apply to admin paths in production
        if not settings.DEBUG and request.path.startswith('/admin/'):
            ip = self._get_client_ip(request)
            whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])

            # If whitelist is configured and IP not in it
            if whitelist and ip not in whitelist:
                logger.warning(
                    f"Unauthorized admin access attempt from IP: {ip}"
                )
                return HttpResponseForbidden(
                    "Access denied: Your IP address is not authorized to access this resource."
                )

        return None

    def _get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """
    Global rate limiting middleware
    Protects against brute force and DDoS attacks
    """

    def process_request(self, request):
        # Skip rate limiting in debug mode
        if settings.DEBUG:
            return None

        ip = self._get_client_ip(request)

        # Different rate limits for different endpoints
        if request.path.startswith('/api/auth/'):
            max_requests = 20
            window = 300  # 5 minutes
        elif request.path.startswith('/api/'):
            max_requests = 100
            window = 60  # 1 minute
        else:
            return None  # No rate limit for other paths

        cache_key = f"rate_limit:{ip}:{request.path}"
        requests = cache.get(cache_key, 0)

        if requests >= max_requests:
            logger.warning(
                f"Rate limit exceeded: IP={ip} Path={request.path} "
                f"Requests={requests}/{max_requests}"
            )
            return HttpResponseForbidden(
                "Rate limit exceeded. Please try again later."
            )

        # Increment counter
        cache.set(cache_key, requests + 1, window)

        return None

    def _get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
