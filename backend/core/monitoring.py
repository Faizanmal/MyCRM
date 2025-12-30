"""
Application Monitoring and Observability

Provides comprehensive monitoring including:
- Health checks
- Metrics collection
- Performance monitoring
- Alert integration
"""

import logging
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from dataclasses import dataclass, field

from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.http import JsonResponse, HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)


@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    message: str = ''
    latency_ms: float = 0
    details: Dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """
    Comprehensive health checker for application dependencies.
    """
    
    @classmethod
    def check_database(cls) -> HealthCheck:
        """Check database connectivity."""
        start = time.time()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            latency = (time.time() - start) * 1000
            
            return HealthCheck(
                name='database',
                status='healthy' if latency < 100 else 'degraded',
                message='Database connection OK',
                latency_ms=round(latency, 2)
            )
        except Exception as e:
            return HealthCheck(
                name='database',
                status='unhealthy',
                message=f'Database error: {str(e)}',
                latency_ms=(time.time() - start) * 1000
            )
    
    @classmethod
    def check_cache(cls) -> HealthCheck:
        """Check cache connectivity (Redis)."""
        start = time.time()
        try:
            test_key = '_health_check_test'
            cache.set(test_key, 'ok', timeout=10)
            result = cache.get(test_key)
            cache.delete(test_key)
            latency = (time.time() - start) * 1000
            
            if result == 'ok':
                return HealthCheck(
                    name='cache',
                    status='healthy' if latency < 50 else 'degraded',
                    message='Cache connection OK',
                    latency_ms=round(latency, 2)
                )
            else:
                return HealthCheck(
                    name='cache',
                    status='degraded',
                    message='Cache read/write mismatch',
                    latency_ms=round(latency, 2)
                )
        except Exception as e:
            return HealthCheck(
                name='cache',
                status='unhealthy',
                message=f'Cache error: {str(e)}',
                latency_ms=(time.time() - start) * 1000
            )
    
    @classmethod
    def check_celery(cls) -> HealthCheck:
        """Check Celery worker connectivity."""
        start = time.time()
        try:
            from celery import current_app
            
            inspect = current_app.control.inspect()
            stats = inspect.stats()
            latency = (time.time() - start) * 1000
            
            if stats:
                worker_count = len(stats)
                return HealthCheck(
                    name='celery',
                    status='healthy',
                    message=f'{worker_count} worker(s) active',
                    latency_ms=round(latency, 2),
                    details={'workers': list(stats.keys())}
                )
            else:
                return HealthCheck(
                    name='celery',
                    status='degraded',
                    message='No Celery workers found',
                    latency_ms=round(latency, 2)
                )
        except Exception as e:
            return HealthCheck(
                name='celery',
                status='unhealthy',
                message=f'Celery error: {str(e)}',
                latency_ms=(time.time() - start) * 1000
            )
    
    @classmethod
    def check_disk_space(cls) -> HealthCheck:
        """Check available disk space."""
        try:
            usage = psutil.disk_usage('/')
            percent_used = usage.percent
            free_gb = usage.free / (1024 ** 3)
            
            if percent_used > 90:
                status = 'unhealthy'
            elif percent_used > 80:
                status = 'degraded'
            else:
                status = 'healthy'
                
            return HealthCheck(
                name='disk',
                status=status,
                message=f'{percent_used}% used, {free_gb:.1f}GB free',
                details={'percent_used': percent_used, 'free_gb': round(free_gb, 2)}
            )
        except Exception as e:
            return HealthCheck(
                name='disk',
                status='unhealthy',
                message=f'Disk check error: {str(e)}'
            )
    
    @classmethod
    def check_memory(cls) -> HealthCheck:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            available_mb = memory.available / (1024 ** 2)
            
            if percent_used > 95:
                status = 'unhealthy'
            elif percent_used > 85:
                status = 'degraded'
            else:
                status = 'healthy'
                
            return HealthCheck(
                name='memory',
                status=status,
                message=f'{percent_used}% used, {available_mb:.0f}MB available',
                details={'percent_used': percent_used, 'available_mb': round(available_mb)}
            )
        except Exception as e:
            return HealthCheck(
                name='memory',
                status='unhealthy',
                message=f'Memory check error: {str(e)}'
            )
    
    @classmethod
    def run_all_checks(cls) -> Dict[str, Any]:
        """Run all health checks."""
        checks = [
            cls.check_database(),
            cls.check_cache(),
            cls.check_celery(),
            cls.check_disk_space(),
            cls.check_memory(),
        ]
        
        # Determine overall status
        statuses = [c.status for c in checks]
        if 'unhealthy' in statuses:
            overall_status = 'unhealthy'
        elif 'degraded' in statuses:
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
            
        return {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'checks': {
                c.name: {
                    'status': c.status,
                    'message': c.message,
                    'latency_ms': c.latency_ms,
                    'details': c.details
                } for c in checks
            }
        }


class MetricsCollector:
    """
    Collect and expose application metrics.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._metrics = {}
            cls._instance._counters = {}
            cls._instance._histograms = {}
        return cls._instance
    
    def increment(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter."""
        key = self._get_key(name, labels)
        self._counters[key] = self._counters.get(key, 0) + value
        
    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge value."""
        key = self._get_key(name, labels)
        self._metrics[key] = {
            'type': 'gauge',
            'value': value,
            'timestamp': time.time()
        }
        
    def histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram value."""
        key = self._get_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append({
            'value': value,
            'timestamp': time.time()
        })
        
        # Keep only last 1000 values
        if len(self._histograms[key]) > 1000:
            self._histograms[key] = self._histograms[key][-1000:]
            
    def _get_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Generate metric key with labels."""
        if labels:
            label_str = ','.join(f'{k}="{v}"' for k, v in sorted(labels.items()))
            return f'{name}{{{label_str}}}'
        return name
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        metrics = {}
        
        # Counters
        for key, value in self._counters.items():
            metrics[key] = {'type': 'counter', 'value': value}
            
        # Gauges
        for key, data in self._metrics.items():
            metrics[key] = data
            
        # Histograms (compute percentiles)
        for key, values in self._histograms.items():
            if values:
                sorted_values = sorted(v['value'] for v in values)
                count = len(sorted_values)
                metrics[key] = {
                    'type': 'histogram',
                    'count': count,
                    'sum': sum(sorted_values),
                    'avg': sum(sorted_values) / count,
                    'p50': sorted_values[int(count * 0.5)],
                    'p95': sorted_values[int(count * 0.95)],
                    'p99': sorted_values[int(count * 0.99)] if count > 100 else sorted_values[-1],
                }
                
        return metrics
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        for key, value in self._counters.items():
            lines.append(f'{key} {value}')
            
        for key, data in self._metrics.items():
            lines.append(f'{key} {data["value"]}')
            
        for key, values in self._histograms.items():
            if values:
                sorted_values = sorted(v['value'] for v in values)
                count = len(sorted_values)
                lines.append(f'{key}_count {count}')
                lines.append(f'{key}_sum {sum(sorted_values)}')
                lines.append(f'{key}{{quantile="0.5"}} {sorted_values[int(count * 0.5)]}')
                lines.append(f'{key}{{quantile="0.95"}} {sorted_values[int(count * 0.95)]}')
                lines.append(f'{key}{{quantile="0.99"}} {sorted_values[int(count * 0.99)] if count > 100 else sorted_values[-1]}')
                
        return '\n'.join(lines)


# Global metrics collector
metrics = MetricsCollector()


def track_request_metrics(view_func):
    """Decorator to track request metrics."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        start = time.time()
        
        try:
            response = view_func(request, *args, **kwargs)
            status_code = getattr(response, 'status_code', 200)
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = (time.time() - start) * 1000
            
            labels = {
                'method': request.method,
                'endpoint': request.path[:50],
                'status': str(status_code)
            }
            
            metrics.increment('http_requests_total', labels=labels)
            metrics.histogram('http_request_duration_ms', duration, labels=labels)
            
        return response
    return wrapper


# Health check views
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request: HttpRequest) -> JsonResponse:
    """Detailed health check endpoint."""
    result = HealthChecker.run_all_checks()
    status_code = 200 if result['status'] == 'healthy' else 503
    return JsonResponse(result, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request: HttpRequest) -> JsonResponse:
    """Simple liveness check for Kubernetes."""
    return JsonResponse({'status': 'ok'})


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request: HttpRequest) -> JsonResponse:
    """Readiness check for Kubernetes."""
    db_check = HealthChecker.check_database()
    
    if db_check.status == 'healthy':
        return JsonResponse({'status': 'ready'})
    else:
        return JsonResponse({'status': 'not_ready', 'reason': db_check.message}, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def metrics_endpoint(request: HttpRequest) -> JsonResponse:
    """Expose Prometheus metrics."""
    from django.http import HttpResponse
    
    prometheus_format = request.GET.get('format') == 'prometheus'
    
    if prometheus_format:
        return HttpResponse(
            metrics.export_prometheus(),
            content_type='text/plain; version=0.0.4'
        )
    else:
        return JsonResponse(metrics.get_metrics())
