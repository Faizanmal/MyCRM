"""
Monitoring and Metrics Endpoints for MyCRM
Provides Prometheus metrics, health checks, and observability
"""

from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

try:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

import time

import psutil


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic health check endpoint
    Returns 200 if service is running
    """
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'MyCRM Backend'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness probe for Kubernetes
    Checks if service is ready to accept traffic
    """
    checks = {
        'database': False,
        'redis': False,
        'overall': False
    }

    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks['database'] = True
    except Exception as e:
        checks['database_error'] = str(e)

    try:
        # Check Redis
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        checks['redis'] = cache.get('health_check') == 'ok'
    except Exception as e:
        checks['redis_error'] = str(e)

    checks['overall'] = checks['database'] and checks['redis']

    return Response(
        checks,
        status=status.HTTP_200_OK if checks['overall'] else status.HTTP_503_SERVICE_UNAVAILABLE
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness probe for Kubernetes
    Returns 200 if service is alive (even if not ready)
    """
    return Response({
        'status': 'alive',
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def metrics(request):
    """
    Prometheus metrics endpoint
    Protected - requires admin authentication
    """
    if not PROMETHEUS_AVAILABLE:
        return Response(
            {'error': 'Prometheus client not available'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    metrics_data = generate_latest()
    return HttpResponse(
        metrics_data,
        content_type=CONTENT_TYPE_LATEST
    )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_metrics(request):
    """
    System-level metrics for monitoring
    CPU, Memory, Disk usage
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return Response({
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def service_status(request):
    """
    Detailed service status including all components
    """
    status_data = {
        'service': 'MyCRM',
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'environment': 'production' if not settings.DEBUG else 'development',
        'timestamp': timezone.now().isoformat(),
        'components': {}
    }

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]
            status_data['components']['database'] = {
                'status': 'healthy',
                'type': 'PostgreSQL',
                'version': db_version
            }
    except Exception as e:
        status_data['components']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }

    # Redis check
    try:
        from django.core.cache import cache
        cache_key = f'status_check_{int(time.time())}'
        cache.set(cache_key, 'test', 5)
        redis_ok = cache.get(cache_key) == 'test'
        status_data['components']['redis'] = {
            'status': 'healthy' if redis_ok else 'unhealthy'
        }
    except Exception as e:
        status_data['components']['redis'] = {
            'status': 'unhealthy',
            'error': str(e)
        }

    # Celery check
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        active_workers = inspect.active()
        status_data['components']['celery'] = {
            'status': 'healthy' if active_workers else 'no_workers',
            'workers': list(active_workers.keys()) if active_workers else []
        }
    except Exception as e:
        status_data['components']['celery'] = {
            'status': 'unknown',
            'error': str(e)
        }

    return Response(status_data)
