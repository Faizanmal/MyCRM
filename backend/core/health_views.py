"""
Health Check Views
API endpoints for monitoring application health
"""

import time

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    Basic health check endpoint
    Returns 200 if the service is running
    """
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request):
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'service': 'MyCRM API',
        })


class PingView(APIView):
    """
    Simple ping endpoint for load balancers
    """
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request):
        return Response('pong', status=status.HTTP_200_OK)


class ReadinessCheckView(APIView):
    """
    Readiness check for Kubernetes/container orchestration
    Checks if all dependencies are ready
    """
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request):
        checks = {
            'database': self._check_database(),
            'cache': self._check_cache(),
        }

        all_healthy = all(check['status'] == 'healthy' for check in checks.values())

        return Response({
            'status': 'ready' if all_healthy else 'not_ready',
            'checks': checks,
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE)

    def _check_database(self):
        """Check database connectivity"""
        try:
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            latency = (time.time() - start) * 1000

            return {
                'status': 'healthy',
                'latency_ms': round(latency, 2),
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }

    def _check_cache(self):
        """Check cache connectivity"""
        try:
            start = time.time()
            test_key = 'health_check_test'
            cache.set(test_key, 'test', 10)
            result = cache.get(test_key)
            cache.delete(test_key)
            latency = (time.time() - start) * 1000

            if result == 'test':
                return {
                    'status': 'healthy',
                    'latency_ms': round(latency, 2),
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Cache read/write failed',
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }


class LivenessCheckView(APIView):
    """
    Liveness check for Kubernetes/container orchestration
    Basic check that the application is alive
    """
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request):
        return Response({
            'status': 'alive',
            'timestamp': timezone.now().isoformat(),
        })


class DetailedHealthCheckView(APIView):
    """
    Detailed health check with all dependencies
    Protected endpoint for admin use
    """
    permission_classes = [AllowAny]  # Can change to IsAdminUser
    throttle_classes = []

    def get(self, request):
        start_time = time.time()

        checks = {
            'database': self._check_database(),
            'cache': self._check_cache(),
            'celery': self._check_celery(),
            'storage': self._check_storage(),
            'email': self._check_email(),
        }

        total_time = (time.time() - start_time) * 1000

        healthy_count = sum(1 for check in checks.values() if check['status'] == 'healthy')
        total_count = len(checks)

        overall_status = 'healthy' if healthy_count == total_count else (
            'degraded' if healthy_count > 0 else 'unhealthy'
        )

        return Response({
            'status': overall_status,
            'checks': checks,
            'summary': {
                'healthy': healthy_count,
                'total': total_count,
                'percentage': round((healthy_count / total_count) * 100, 1),
            },
            'response_time_ms': round(total_time, 2),
            'timestamp': timezone.now().isoformat(),
            'version': getattr(settings, 'VERSION', '1.0.0'),
            'environment': getattr(settings, 'ENVIRONMENT', 'development'),
        })

    def _check_database(self):
        """Check database connectivity and query performance"""
        try:
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            latency = (time.time() - start) * 1000

            # Get database info
            db_settings = settings.DATABASES.get('default', {})

            return {
                'status': 'healthy',
                'latency_ms': round(latency, 2),
                'engine': db_settings.get('ENGINE', 'unknown').split('.')[-1],
                'host': db_settings.get('HOST', 'localhost'),
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }

    def _check_cache(self):
        """Check cache connectivity"""
        try:
            start = time.time()
            test_key = 'health_check_detailed'
            cache.set(test_key, {'timestamp': timezone.now().isoformat()}, 10)
            result = cache.get(test_key)
            cache.delete(test_key)
            latency = (time.time() - start) * 1000

            # Get cache backend info
            cache_backend = getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', 'unknown')

            return {
                'status': 'healthy' if result else 'unhealthy',
                'latency_ms': round(latency, 2),
                'backend': cache_backend.split('.')[-1],
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }

    def _check_celery(self):
        """Check Celery worker connectivity"""
        try:
            from config.celery import app

            start = time.time()
            result = app.control.ping(timeout=5)
            latency = (time.time() - start) * 1000

            if result:
                return {
                    'status': 'healthy',
                    'latency_ms': round(latency, 2),
                    'workers': len(result),
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'No workers responded',
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }

    def _check_storage(self):
        """Check file storage accessibility"""
        try:
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage

            start = time.time()

            # Try to write and read a test file
            test_file = 'health_check_test.txt'
            default_storage.save(test_file, ContentFile(b'test'))
            exists = default_storage.exists(test_file)
            default_storage.delete(test_file)

            latency = (time.time() - start) * 1000

            return {
                'status': 'healthy' if exists else 'unhealthy',
                'latency_ms': round(latency, 2),
                'backend': default_storage.__class__.__name__,
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }

    def _check_email(self):
        """Check email configuration"""
        try:
            email_backend = getattr(settings, 'EMAIL_BACKEND', 'unknown')
            email_host = getattr(settings, 'EMAIL_HOST', 'not_configured')

            # We don't actually send an email, just check configuration
            is_configured = email_host != 'not_configured' and email_host != ''

            return {
                'status': 'healthy' if is_configured else 'warning',
                'backend': email_backend.split('.')[-1],
                'host': email_host[:20] + '...' if len(email_host) > 20 else email_host,
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }


class MetricsView(APIView):
    """
    Prometheus-compatible metrics endpoint
    """
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request):
        from django.contrib.auth import get_user_model

        from .models import Notification
        from .settings_models import ExportJob

        User = get_user_model()

        metrics = []

        # User metrics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        metrics.append(f'crm_users_total {total_users}')
        metrics.append(f'crm_users_active {active_users}')

        # Notification metrics
        try:
            total_notifications = Notification.objects.count()
            unread_notifications = Notification.objects.filter(is_read=False).count()
            metrics.append(f'crm_notifications_total {total_notifications}')
            metrics.append(f'crm_notifications_unread {unread_notifications}')
        except:
            pass

        # Export metrics
        try:
            pending_exports = ExportJob.objects.filter(status='pending').count()
            processing_exports = ExportJob.objects.filter(status='processing').count()
            metrics.append(f'crm_exports_pending {pending_exports}')
            metrics.append(f'crm_exports_processing {processing_exports}')
        except:
            pass

        # System metrics
        metrics.append('crm_health_status 1')  # 1 = healthy
        metrics.append(f'crm_uptime_seconds {self._get_uptime()}')

        return Response('\n'.join(metrics), content_type='text/plain')

    def _get_uptime(self):
        """Get application uptime in seconds"""
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            uptime = time.time() - process.create_time()
            return int(uptime)
        except:
            return 0
