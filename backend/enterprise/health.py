"""
Enterprise Health Check Endpoints for MyCRM
============================================

Comprehensive health check system including:
- Kubernetes liveness/readiness probes
- Dependency health checks
- Graceful degradation
- Health aggregation
- Prometheus metrics endpoint

Author: MyCRM Enterprise Team
Version: 1.0.0
"""

import asyncio
import logging
import socket
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import threading

from django.conf import settings
from django.db import connection, connections
from django.http import JsonResponse
from django.views import View

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    name: str
    status: HealthStatus
    latency_ms: float
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'status': self.status.value,
            'latency_ms': round(self.latency_ms, 2),
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AggregatedHealth:
    """Aggregated health status."""
    status: HealthStatus
    checks: List[HealthCheckResult]
    total_latency_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'status': self.status.value,
            'total_latency_ms': round(self.total_latency_ms, 2),
            'checks': [c.to_dict() for c in self.checks],
            'timestamp': self.timestamp.isoformat()
        }


class HealthChecker:
    """
    Base class for health checkers.
    """
    
    def __init__(self, name: str, critical: bool = True, timeout: float = 5.0):
        self.name = name
        self.critical = critical  # If critical, unhealthy makes whole system unhealthy
        self.timeout = timeout
    
    def check(self) -> HealthCheckResult:
        """Perform health check."""
        start_time = time.time()
        try:
            result = self._perform_check()
            latency_ms = (time.time() - start_time) * 1000
            result.latency_ms = latency_ms
            return result
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                message=str(e)
            )
    
    def _perform_check(self) -> HealthCheckResult:
        """Override in subclass to perform actual check."""
        raise NotImplementedError


class DatabaseHealthChecker(HealthChecker):
    """Check database connectivity and performance."""
    
    def __init__(self, alias: str = 'default', **kwargs):
        super().__init__(name=f'database_{alias}', **kwargs)
        self.alias = alias
    
    def _perform_check(self) -> HealthCheckResult:
        try:
            start = time.time()
            with connections[self.alias].cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            latency = (time.time() - start) * 1000
            
            # Check connection pool status
            details = {}
            try:
                with connections[self.alias].cursor() as cursor:
                    cursor.execute("""
                        SELECT numbackends, 
                               (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_conn
                        FROM pg_stat_database 
                        WHERE datname = current_database()
                    """)
                    result = cursor.fetchone()
                    if result:
                        details['active_connections'] = result[0]
                        details['max_connections'] = result[1]
                        details['utilization_percent'] = round(
                            (result[0] / result[1]) * 100, 2
                        ) if result[1] else 0
            except Exception:
                pass
            
            status = HealthStatus.HEALTHY
            message = "Database connection successful"
            
            # Check for high latency
            if latency > 100:
                status = HealthStatus.DEGRADED
                message = f"High database latency: {latency:.2f}ms"
            
            # Check connection utilization
            if details.get('utilization_percent', 0) > 80:
                status = HealthStatus.DEGRADED
                message = "High connection pool utilization"
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                latency_ms=latency,
                message=message,
                details=details
            )
            
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"Database connection failed: {str(e)}"
            )


class RedisHealthChecker(HealthChecker):
    """Check Redis connectivity."""
    
    def __init__(self, url: str = None, **kwargs):
        super().__init__(name='redis', **kwargs)
        self.url = url or getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
    
    def _perform_check(self) -> HealthCheckResult:
        try:
            import redis
            
            start = time.time()
            client = redis.from_url(self.url)
            
            # Ping
            client.ping()
            
            # Get info
            info = client.info()
            latency = (time.time() - start) * 1000
            
            details = {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', 'N/A'),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
            
            status = HealthStatus.HEALTHY
            message = "Redis connection successful"
            
            # Check memory usage
            used_memory = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)
            if max_memory > 0 and used_memory / max_memory > 0.8:
                status = HealthStatus.DEGRADED
                message = "High Redis memory usage"
                details['memory_utilization_percent'] = round(
                    (used_memory / max_memory) * 100, 2
                )
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                latency_ms=latency,
                message=message,
                details=details
            )
            
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"Redis connection failed: {str(e)}"
            )


class CeleryHealthChecker(HealthChecker):
    """Check Celery worker availability."""
    
    def __init__(self, **kwargs):
        super().__init__(name='celery', **kwargs)
    
    def _perform_check(self) -> HealthCheckResult:
        try:
            from celery import current_app
            
            start = time.time()
            
            # Ping workers
            inspect = current_app.control.inspect()
            ping_response = inspect.ping()
            
            latency = (time.time() - start) * 1000
            
            if not ping_response:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=latency,
                    message="No Celery workers available"
                )
            
            # Get worker stats
            active_tasks = inspect.active() or {}
            reserved_tasks = inspect.reserved() or {}
            
            worker_count = len(ping_response)
            total_active = sum(len(tasks) for tasks in active_tasks.values())
            
            details = {
                'worker_count': worker_count,
                'active_tasks': total_active,
                'workers': list(ping_response.keys())
            }
            
            status = HealthStatus.HEALTHY
            message = f"{worker_count} workers available"
            
            # Check if workers are overloaded
            if worker_count > 0 and total_active / worker_count > 10:
                status = HealthStatus.DEGRADED
                message = "Workers may be overloaded"
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                latency_ms=latency,
                message=message,
                details=details
            )
            
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"Celery check failed: {str(e)}"
            )


class ExternalServiceHealthChecker(HealthChecker):
    """Check external service availability."""
    
    def __init__(self, name: str, url: str, expected_status: int = 200, **kwargs):
        super().__init__(name=name, **kwargs)
        self.url = url
        self.expected_status = expected_status
    
    def _perform_check(self) -> HealthCheckResult:
        try:
            import requests
            
            start = time.time()
            response = requests.get(
                self.url,
                timeout=self.timeout,
                headers={'User-Agent': 'MyCRM-HealthCheck/1.0'}
            )
            latency = (time.time() - start) * 1000
            
            if response.status_code == self.expected_status:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency,
                    message=f"Service responded with {response.status_code}",
                    details={'status_code': response.status_code}
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.DEGRADED,
                    latency_ms=latency,
                    message=f"Unexpected status code: {response.status_code}",
                    details={'status_code': response.status_code}
                )
                
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"Service unreachable: {str(e)}"
            )


class DiskHealthChecker(HealthChecker):
    """Check disk space availability."""
    
    def __init__(self, path: str = '/', threshold_percent: float = 90, **kwargs):
        super().__init__(name='disk', **kwargs)
        self.path = path
        self.threshold_percent = threshold_percent
    
    def _perform_check(self) -> HealthCheckResult:
        try:
            import shutil
            
            start = time.time()
            total, used, free = shutil.disk_usage(self.path)
            latency = (time.time() - start) * 1000
            
            used_percent = (used / total) * 100
            
            details = {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'used_percent': round(used_percent, 2)
            }
            
            if used_percent >= self.threshold_percent:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=latency,
                    message=f"Disk usage critical: {used_percent:.1f}%",
                    details=details
                )
            elif used_percent >= self.threshold_percent - 10:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.DEGRADED,
                    latency_ms=latency,
                    message=f"Disk usage high: {used_percent:.1f}%",
                    details=details
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency,
                    message=f"Disk usage normal: {used_percent:.1f}%",
                    details=details
                )
                
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"Disk check failed: {str(e)}"
            )


class MemoryHealthChecker(HealthChecker):
    """Check memory availability."""
    
    def __init__(self, threshold_percent: float = 90, **kwargs):
        super().__init__(name='memory', **kwargs)
        self.threshold_percent = threshold_percent
    
    def _perform_check(self) -> HealthCheckResult:
        try:
            import psutil
            
            start = time.time()
            memory = psutil.virtual_memory()
            latency = (time.time() - start) * 1000
            
            details = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_percent': memory.percent
            }
            
            if memory.percent >= self.threshold_percent:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=latency,
                    message=f"Memory usage critical: {memory.percent}%",
                    details=details
                )
            elif memory.percent >= self.threshold_percent - 10:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.DEGRADED,
                    latency_ms=latency,
                    message=f"Memory usage high: {memory.percent}%",
                    details=details
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency,
                    message=f"Memory usage normal: {memory.percent}%",
                    details=details
                )
                
        except ImportError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                latency_ms=0,
                message="psutil not installed, skipping memory check"
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"Memory check failed: {str(e)}"
            )


class HealthCheckRegistry:
    """
    Registry for health checks.
    Singleton pattern for global access.
    """
    
    _instance: Optional['HealthCheckRegistry'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._checkers: Dict[str, HealthChecker] = {}
        self._cache: Optional[AggregatedHealth] = None
        self._cache_ttl = timedelta(seconds=5)
        self._cache_time: Optional[datetime] = None
    
    def register(self, checker: HealthChecker):
        """Register a health checker."""
        self._checkers[checker.name] = checker
    
    def unregister(self, name: str):
        """Unregister a health checker."""
        self._checkers.pop(name, None)
    
    def check_all(self, use_cache: bool = True) -> AggregatedHealth:
        """Run all health checks."""
        # Return cached result if valid
        if (
            use_cache and
            self._cache and
            self._cache_time and
            datetime.now() - self._cache_time < self._cache_ttl
        ):
            return self._cache
        
        results = []
        total_latency = 0
        
        # Run checks in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_checker = {
                executor.submit(checker.check): checker
                for checker in self._checkers.values()
            }
            
            for future in as_completed(future_to_checker):
                result = future.result()
                results.append(result)
                total_latency += result.latency_ms
        
        # Determine overall status
        overall_status = HealthStatus.HEALTHY
        
        for result in results:
            checker = self._checkers.get(result.name)
            if result.status == HealthStatus.UNHEALTHY:
                if checker and checker.critical:
                    overall_status = HealthStatus.UNHEALTHY
                    break
                else:
                    overall_status = HealthStatus.DEGRADED
            elif result.status == HealthStatus.DEGRADED:
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
        
        aggregated = AggregatedHealth(
            status=overall_status,
            checks=results,
            total_latency_ms=total_latency
        )
        
        # Cache result
        self._cache = aggregated
        self._cache_time = datetime.now()
        
        return aggregated
    
    def check_single(self, name: str) -> Optional[HealthCheckResult]:
        """Run a single health check by name."""
        checker = self._checkers.get(name)
        if checker:
            return checker.check()
        return None


# Import for parallel execution
from concurrent.futures import ThreadPoolExecutor, as_completed


# =============================================================================
# Default Health Check Setup
# =============================================================================

def setup_default_health_checks():
    """Set up default health checks for the application."""
    registry = HealthCheckRegistry()
    
    # Database health check
    registry.register(DatabaseHealthChecker(alias='default', critical=True))
    
    # Add read replica checks if configured
    replicas = getattr(settings, 'READ_REPLICA_DATABASES', [])
    for replica in replicas:
        registry.register(DatabaseHealthChecker(alias=replica, critical=False))
    
    # Redis health check
    redis_url = getattr(settings, 'REDIS_URL', None)
    if redis_url:
        registry.register(RedisHealthChecker(url=redis_url, critical=True))
    
    # Celery health check
    registry.register(CeleryHealthChecker(critical=False))
    
    # Disk health check
    registry.register(DiskHealthChecker(critical=True))
    
    # Memory health check
    registry.register(MemoryHealthChecker(critical=False))
    
    return registry


# =============================================================================
# Django Views
# =============================================================================

class LivenessView(View):
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if the application is running.
    """
    
    def get(self, request):
        return JsonResponse({
            'status': 'alive',
            'timestamp': datetime.now().isoformat()
        })


class ReadinessView(View):
    """
    Kubernetes readiness probe endpoint.
    Returns 200 if the application can serve traffic.
    """
    
    def get(self, request):
        registry = HealthCheckRegistry()
        
        # Check critical services only for readiness
        db_check = registry.check_single('database_default')
        
        if db_check and db_check.status == HealthStatus.UNHEALTHY:
            return JsonResponse(
                {
                    'status': 'not_ready',
                    'reason': db_check.message,
                    'timestamp': datetime.now().isoformat()
                },
                status=503
            )
        
        return JsonResponse({
            'status': 'ready',
            'timestamp': datetime.now().isoformat()
        })


class StartupView(View):
    """
    Kubernetes startup probe endpoint.
    Returns 200 once the application has finished initializing.
    """
    
    _startup_complete = False
    _startup_time: Optional[datetime] = None
    
    @classmethod
    def mark_startup_complete(cls):
        """Mark the application as having completed startup."""
        cls._startup_complete = True
        cls._startup_time = datetime.now()
    
    def get(self, request):
        if self._startup_complete:
            return JsonResponse({
                'status': 'started',
                'startup_time': self._startup_time.isoformat() if self._startup_time else None,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return JsonResponse(
                {
                    'status': 'starting',
                    'timestamp': datetime.now().isoformat()
                },
                status=503
            )


class HealthView(View):
    """
    Comprehensive health check endpoint.
    Returns detailed health status of all components.
    """
    
    def get(self, request):
        registry = HealthCheckRegistry()
        
        # Check for specific component
        component = request.GET.get('component')
        if component:
            result = registry.check_single(component)
            if result:
                status_code = 200 if result.status != HealthStatus.UNHEALTHY else 503
                return JsonResponse(result.to_dict(), status=status_code)
            else:
                return JsonResponse(
                    {'error': f'Unknown component: {component}'},
                    status=404
                )
        
        # Full health check
        use_cache = request.GET.get('fresh', '').lower() != 'true'
        health = registry.check_all(use_cache=use_cache)
        
        status_code = 200
        if health.status == HealthStatus.UNHEALTHY:
            status_code = 503
        elif health.status == HealthStatus.DEGRADED:
            status_code = 200  # Still serve traffic but indicate degradation
        
        response_data = health.to_dict()
        response_data['hostname'] = socket.gethostname()
        
        return JsonResponse(response_data, status=status_code)


class MetricsView(View):
    """
    Prometheus metrics endpoint.
    Exports health check metrics in Prometheus format.
    """
    
    def get(self, request):
        registry = HealthCheckRegistry()
        health = registry.check_all(use_cache=True)
        
        lines = []
        
        # Overall health metric
        lines.append('# HELP mycrm_health_status Overall health status (1=healthy, 0.5=degraded, 0=unhealthy)')
        lines.append('# TYPE mycrm_health_status gauge')
        status_value = {
            HealthStatus.HEALTHY: 1,
            HealthStatus.DEGRADED: 0.5,
            HealthStatus.UNHEALTHY: 0
        }[health.status]
        lines.append(f'mycrm_health_status {status_value}')
        
        # Individual check metrics
        lines.append('')
        lines.append('# HELP mycrm_health_check_status Individual health check status')
        lines.append('# TYPE mycrm_health_check_status gauge')
        
        for check in health.checks:
            value = status_value = {
                HealthStatus.HEALTHY: 1,
                HealthStatus.DEGRADED: 0.5,
                HealthStatus.UNHEALTHY: 0
            }[check.status]
            lines.append(f'mycrm_health_check_status{{check="{check.name}"}} {value}')
        
        # Latency metrics
        lines.append('')
        lines.append('# HELP mycrm_health_check_latency_ms Health check latency in milliseconds')
        lines.append('# TYPE mycrm_health_check_latency_ms gauge')
        
        for check in health.checks:
            lines.append(f'mycrm_health_check_latency_ms{{check="{check.name}"}} {check.latency_ms}')
        
        # Total latency
        lines.append('')
        lines.append('# HELP mycrm_health_total_latency_ms Total health check latency')
        lines.append('# TYPE mycrm_health_total_latency_ms gauge')
        lines.append(f'mycrm_health_total_latency_ms {health.total_latency_ms}')
        
        from django.http import HttpResponse
        return HttpResponse(
            '\n'.join(lines),
            content_type='text/plain; charset=utf-8'
        )


# =============================================================================
# URL Configuration Helper
# =============================================================================

def get_health_urls():
    """
    Get URL patterns for health check endpoints.
    
    Usage in urls.py:
        from enterprise.health import get_health_urls
        
        urlpatterns = [
            ...
        ] + get_health_urls()
    """
    from django.urls import path
    
    return [
        path('health/', HealthView.as_view(), name='health'),
        path('health/live/', LivenessView.as_view(), name='health-live'),
        path('health/ready/', ReadinessView.as_view(), name='health-ready'),
        path('health/startup/', StartupView.as_view(), name='health-startup'),
        path('metrics/', MetricsView.as_view(), name='metrics'),
    ]
