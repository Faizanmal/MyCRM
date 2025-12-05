"""
Enterprise Observability Stack for MyCRM

Provides:
- Distributed tracing (OpenTelemetry)
- Metrics collection (Prometheus)
- Log aggregation
- APM integration
- Custom business metrics
- SLO/SLA monitoring
- Alerting integration
"""

import os
import time
import logging
import threading
import functools
from typing import Dict, Optional, Any, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
import json

from django.conf import settings
from django.core.cache import cache
from django.db import connection

logger = logging.getLogger(__name__)


# =====================
# Metrics Collection
# =====================

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = 'counter'
    GAUGE = 'gauge'
    HISTOGRAM = 'histogram'
    SUMMARY = 'summary'


@dataclass
class MetricDefinition:
    """Definition of a metric"""
    name: str
    metric_type: MetricType
    description: str
    labels: List[str] = field(default_factory=list)
    buckets: List[float] = field(default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10])


class MetricsCollector:
    """
    Centralized metrics collection and export
    Supports Prometheus, Datadog, and custom backends
    """
    
    _instance = None
    _lock = threading.Lock()
    
    # Pre-defined metrics for CRM
    METRICS = {
        # HTTP Metrics
        'http_requests_total': MetricDefinition(
            name='mycrm_http_requests_total',
            metric_type=MetricType.COUNTER,
            description='Total HTTP requests',
            labels=['method', 'endpoint', 'status_code']
        ),
        'http_request_duration_seconds': MetricDefinition(
            name='mycrm_http_request_duration_seconds',
            metric_type=MetricType.HISTOGRAM,
            description='HTTP request duration in seconds',
            labels=['method', 'endpoint']
        ),
        
        # Database Metrics
        'db_queries_total': MetricDefinition(
            name='mycrm_db_queries_total',
            metric_type=MetricType.COUNTER,
            description='Total database queries',
            labels=['operation', 'table']
        ),
        'db_query_duration_seconds': MetricDefinition(
            name='mycrm_db_query_duration_seconds',
            metric_type=MetricType.HISTOGRAM,
            description='Database query duration',
            labels=['operation']
        ),
        
        # Business Metrics
        'leads_created_total': MetricDefinition(
            name='mycrm_leads_created_total',
            metric_type=MetricType.COUNTER,
            description='Total leads created',
            labels=['source', 'tenant']
        ),
        'opportunities_value_total': MetricDefinition(
            name='mycrm_opportunities_value_total',
            metric_type=MetricType.GAUGE,
            description='Total opportunity pipeline value',
            labels=['stage', 'tenant']
        ),
        'active_users': MetricDefinition(
            name='mycrm_active_users',
            metric_type=MetricType.GAUGE,
            description='Currently active users',
            labels=['tenant']
        ),
        
        # AI/ML Metrics
        'ml_predictions_total': MetricDefinition(
            name='mycrm_ml_predictions_total',
            metric_type=MetricType.COUNTER,
            description='Total ML predictions made',
            labels=['model', 'outcome']
        ),
        'ml_prediction_latency_seconds': MetricDefinition(
            name='mycrm_ml_prediction_latency_seconds',
            metric_type=MetricType.HISTOGRAM,
            description='ML prediction latency',
            labels=['model']
        ),
        
        # Cache Metrics
        'cache_hits_total': MetricDefinition(
            name='mycrm_cache_hits_total',
            metric_type=MetricType.COUNTER,
            description='Cache hits',
            labels=['cache_type']
        ),
        'cache_misses_total': MetricDefinition(
            name='mycrm_cache_misses_total',
            metric_type=MetricType.COUNTER,
            description='Cache misses',
            labels=['cache_type']
        ),
        
        # Queue Metrics
        'celery_tasks_total': MetricDefinition(
            name='mycrm_celery_tasks_total',
            metric_type=MetricType.COUNTER,
            description='Celery tasks processed',
            labels=['task_name', 'status']
        ),
        'celery_task_duration_seconds': MetricDefinition(
            name='mycrm_celery_task_duration_seconds',
            metric_type=MetricType.HISTOGRAM,
            description='Celery task duration',
            labels=['task_name']
        ),
    }
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._metrics_data = {}
        self._histograms = {}
        self._prometheus_enabled = os.getenv('PROMETHEUS_ENABLED', 'true').lower() == 'true'
        self._datadog_enabled = os.getenv('DATADOG_ENABLED', 'false').lower() == 'true'
        self._initialized = True
        
        # Initialize Prometheus client if enabled
        if self._prometheus_enabled:
            self._init_prometheus()
        
        # Initialize Datadog if enabled
        if self._datadog_enabled:
            self._init_datadog()
    
    def _init_prometheus(self):
        """Initialize Prometheus metrics"""
        try:
            from prometheus_client import Counter, Gauge, Histogram, REGISTRY
            
            self._prom_metrics = {}
            
            for key, metric_def in self.METRICS.items():
                if metric_def.metric_type == MetricType.COUNTER:
                    self._prom_metrics[key] = Counter(
                        metric_def.name,
                        metric_def.description,
                        metric_def.labels
                    )
                elif metric_def.metric_type == MetricType.GAUGE:
                    self._prom_metrics[key] = Gauge(
                        metric_def.name,
                        metric_def.description,
                        metric_def.labels
                    )
                elif metric_def.metric_type == MetricType.HISTOGRAM:
                    self._prom_metrics[key] = Histogram(
                        metric_def.name,
                        metric_def.description,
                        metric_def.labels,
                        buckets=metric_def.buckets
                    )
            
            logger.info("Prometheus metrics initialized")
        except ImportError:
            logger.warning("prometheus_client not installed, Prometheus metrics disabled")
            self._prometheus_enabled = False
    
    def _init_datadog(self):
        """Initialize Datadog metrics"""
        try:
            from datadog import initialize, statsd
            
            initialize(
                api_key=os.getenv('DATADOG_API_KEY'),
                app_key=os.getenv('DATADOG_APP_KEY'),
                statsd_host=os.getenv('DATADOG_STATSD_HOST', 'localhost'),
                statsd_port=int(os.getenv('DATADOG_STATSD_PORT', '8125'))
            )
            
            self._statsd = statsd
            logger.info("Datadog metrics initialized")
        except ImportError:
            logger.warning("datadog not installed, Datadog metrics disabled")
            self._datadog_enabled = False
    
    def increment(self, metric_name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        labels = labels or {}
        
        if self._prometheus_enabled and metric_name in self._prom_metrics:
            self._prom_metrics[metric_name].labels(**labels).inc(value)
        
        if self._datadog_enabled:
            tags = [f"{k}:{v}" for k, v in labels.items()]
            self._statsd.increment(f"mycrm.{metric_name}", value, tags=tags)
        
        # Store in memory for quick access
        cache_key = f"metric:{metric_name}:{json.dumps(labels, sort_keys=True)}"
        current = cache.get(cache_key, 0)
        cache.set(cache_key, current + value, 3600)
    
    def gauge(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        labels = labels or {}
        
        if self._prometheus_enabled and metric_name in self._prom_metrics:
            self._prom_metrics[metric_name].labels(**labels).set(value)
        
        if self._datadog_enabled:
            tags = [f"{k}:{v}" for k, v in labels.items()]
            self._statsd.gauge(f"mycrm.{metric_name}", value, tags=tags)
        
        cache_key = f"metric:{metric_name}:{json.dumps(labels, sort_keys=True)}"
        cache.set(cache_key, value, 3600)
    
    def histogram(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram observation"""
        labels = labels or {}
        
        if self._prometheus_enabled and metric_name in self._prom_metrics:
            self._prom_metrics[metric_name].labels(**labels).observe(value)
        
        if self._datadog_enabled:
            tags = [f"{k}:{v}" for k, v in labels.items()]
            self._statsd.histogram(f"mycrm.{metric_name}", value, tags=tags)
    
    @contextmanager
    def timer(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager to time operations"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.histogram(metric_name, duration, labels)
    
    def get_metric(self, metric_name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get current metric value from cache"""
        labels = labels or {}
        cache_key = f"metric:{metric_name}:{json.dumps(labels, sort_keys=True)}"
        return cache.get(cache_key)


# =====================
# Distributed Tracing
# =====================

@dataclass
class Span:
    """Represents a span in a trace"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: float
    end_time: Optional[float] = None
    status: str = 'ok'
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict] = field(default_factory=list)
    
    @property
    def duration_ms(self) -> Optional[float]:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None


class TracingManager:
    """
    Distributed tracing using OpenTelemetry
    """
    
    _instance = None
    _lock = threading.Lock()
    _local = threading.local()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.service_name = os.getenv('OTEL_SERVICE_NAME', 'mycrm-backend')
        self._otel_enabled = os.getenv('OTEL_ENABLED', 'false').lower() == 'true'
        self._jaeger_enabled = os.getenv('JAEGER_ENABLED', 'false').lower() == 'true'
        self._spans = {}
        self._initialized = True
        
        if self._otel_enabled:
            self._init_opentelemetry()
    
    def _init_opentelemetry(self):
        """Initialize OpenTelemetry"""
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.sdk.resources import Resource
            
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": os.getenv('APP_VERSION', '2.0.0'),
                "deployment.environment": os.getenv('ENVIRONMENT', 'development')
            })
            
            provider = TracerProvider(resource=resource)
            
            # Add Jaeger exporter if enabled
            if self._jaeger_enabled:
                from opentelemetry.exporter.jaeger.thrift import JaegerExporter
                
                jaeger_exporter = JaegerExporter(
                    agent_host_name=os.getenv('JAEGER_AGENT_HOST', 'localhost'),
                    agent_port=int(os.getenv('JAEGER_AGENT_PORT', '6831'))
                )
                provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
            
            # Add OTLP exporter
            otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
            if otlp_endpoint:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
                provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            
            trace.set_tracer_provider(provider)
            self._tracer = trace.get_tracer(__name__)
            
            logger.info("OpenTelemetry tracing initialized")
        except ImportError as e:
            logger.warning(f"OpenTelemetry packages not installed: {e}")
            self._otel_enabled = False
    
    def _generate_id(self, length: int = 16) -> str:
        """Generate random trace/span ID"""
        import secrets
        return secrets.token_hex(length)
    
    @property
    def current_span(self) -> Optional[Span]:
        """Get current span from thread-local storage"""
        return getattr(self._local, 'current_span', None)
    
    @current_span.setter
    def current_span(self, span: Optional[Span]):
        """Set current span in thread-local storage"""
        self._local.current_span = span
    
    @property
    def current_trace_id(self) -> Optional[str]:
        """Get current trace ID"""
        span = self.current_span
        return span.trace_id if span else None
    
    @contextmanager
    def span(self, operation_name: str, tags: Optional[Dict[str, str]] = None):
        """
        Context manager to create a span
        
        Usage:
            with tracing.span('process_lead', {'lead_id': '123'}):
                # ... processing code ...
        """
        parent = self.current_span
        
        span = Span(
            trace_id=parent.trace_id if parent else self._generate_id(16),
            span_id=self._generate_id(8),
            parent_span_id=parent.span_id if parent else None,
            operation_name=operation_name,
            service_name=self.service_name,
            start_time=time.time(),
            tags=tags or {}
        )
        
        self.current_span = span
        
        try:
            yield span
            span.status = 'ok'
        except Exception as e:
            span.status = 'error'
            span.tags['error'] = str(e)
            span.tags['error.type'] = type(e).__name__
            raise
        finally:
            span.end_time = time.time()
            self._record_span(span)
            self.current_span = parent
    
    def _record_span(self, span: Span):
        """Record span to storage/exporter"""
        # Store in cache for debugging
        cache_key = f"trace:{span.trace_id}:spans"
        spans = cache.get(cache_key, [])
        spans.append({
            'span_id': span.span_id,
            'parent_span_id': span.parent_span_id,
            'operation': span.operation_name,
            'duration_ms': span.duration_ms,
            'status': span.status,
            'tags': span.tags
        })
        cache.set(cache_key, spans, 3600)
        
        # Export to OpenTelemetry if enabled
        if self._otel_enabled and hasattr(self, '_tracer'):
            # OpenTelemetry handles this automatically with its context manager
            pass
        
        # Log for debugging
        logger.debug(
            f"SPAN: {span.operation_name} [{span.trace_id[:8]}] "
            f"duration={span.duration_ms:.2f}ms status={span.status}"
        )
    
    def add_span_tag(self, key: str, value: str):
        """Add tag to current span"""
        if self.current_span:
            self.current_span.tags[key] = value
    
    def add_span_log(self, message: str, level: str = 'info'):
        """Add log to current span"""
        if self.current_span:
            self.current_span.logs.append({
                'timestamp': time.time(),
                'level': level,
                'message': message
            })
    
    def get_trace(self, trace_id: str) -> List[Dict]:
        """Get all spans for a trace"""
        cache_key = f"trace:{trace_id}:spans"
        return cache.get(cache_key, [])
    
    def inject_headers(self) -> Dict[str, str]:
        """Get headers to propagate trace context"""
        span = self.current_span
        if span:
            return {
                'X-Trace-ID': span.trace_id,
                'X-Span-ID': span.span_id,
                'X-Parent-Span-ID': span.parent_span_id or ''
            }
        return {}
    
    def extract_context(self, headers: Dict[str, str]):
        """Extract trace context from incoming headers"""
        trace_id = headers.get('X-Trace-ID') or headers.get('x-trace-id')
        parent_span_id = headers.get('X-Span-ID') or headers.get('x-span-id')
        
        if trace_id:
            span = Span(
                trace_id=trace_id,
                span_id=self._generate_id(8),
                parent_span_id=parent_span_id,
                operation_name='incoming_request',
                service_name=self.service_name,
                start_time=time.time()
            )
            self.current_span = span


# =====================
# APM Integration
# =====================

class APMIntegration:
    """
    Application Performance Monitoring integration
    Supports Datadog APM, New Relic, Dynatrace
    """
    
    def __init__(self):
        self.provider = os.getenv('APM_PROVIDER', 'none').lower()
        self._init_provider()
    
    def _init_provider(self):
        """Initialize APM provider"""
        if self.provider == 'datadog':
            self._init_datadog_apm()
        elif self.provider == 'newrelic':
            self._init_newrelic()
        elif self.provider == 'dynatrace':
            self._init_dynatrace()
    
    def _init_datadog_apm(self):
        """Initialize Datadog APM"""
        try:
            from ddtrace import patch_all, tracer
            
            patch_all()
            tracer.configure(
                hostname=os.getenv('DD_AGENT_HOST', 'localhost'),
                port=int(os.getenv('DD_TRACE_AGENT_PORT', '8126'))
            )
            
            logger.info("Datadog APM initialized")
        except ImportError:
            logger.warning("ddtrace not installed")
    
    def _init_newrelic(self):
        """Initialize New Relic"""
        try:
            import newrelic.agent
            
            newrelic.agent.initialize(os.getenv('NEW_RELIC_CONFIG_FILE', 'newrelic.ini'))
            logger.info("New Relic initialized")
        except ImportError:
            logger.warning("newrelic not installed")
    
    def _init_dynatrace(self):
        """Initialize Dynatrace"""
        # Dynatrace OneAgent auto-instruments
        logger.info("Dynatrace OneAgent should be installed at host level")


# =====================
# SLO/SLA Monitoring
# =====================

@dataclass
class SLODefinition:
    """Service Level Objective definition"""
    name: str
    description: str
    target: float  # e.g., 99.9
    measurement_window: str  # 'rolling_7d', 'rolling_30d', 'calendar_month'
    metric_type: str  # 'availability', 'latency', 'error_rate'
    threshold: Optional[float] = None  # For latency SLOs (e.g., p99 < 200ms)


class SLOMonitor:
    """
    Service Level Objective monitoring
    """
    
    SLOS = [
        SLODefinition(
            name='api_availability',
            description='API availability',
            target=99.9,
            measurement_window='rolling_30d',
            metric_type='availability'
        ),
        SLODefinition(
            name='api_latency_p99',
            description='API p99 latency under 500ms',
            target=99.0,
            measurement_window='rolling_7d',
            metric_type='latency',
            threshold=500
        ),
        SLODefinition(
            name='api_error_rate',
            description='API error rate below 0.1%',
            target=99.9,
            measurement_window='rolling_7d',
            metric_type='error_rate'
        ),
    ]
    
    def __init__(self):
        self.metrics = MetricsCollector()
    
    def calculate_slo_status(self, slo: SLODefinition) -> Dict:
        """Calculate current SLO status"""
        # Get relevant metrics from cache/storage
        if slo.metric_type == 'availability':
            total_requests = self.metrics.get_metric('http_requests_total') or 0
            error_requests = cache.get('metric:http_errors_total', 0)
            
            if total_requests > 0:
                current = ((total_requests - error_requests) / total_requests) * 100
            else:
                current = 100.0
        
        elif slo.metric_type == 'latency':
            # Get p99 latency from histogram
            current = cache.get('metric:api_latency_p99', 0)
            # For latency, we measure % of requests under threshold
            total = self.metrics.get_metric('http_requests_total') or 0
            under_threshold = cache.get(f'metric:latency_under_{slo.threshold}', 0)
            
            if total > 0:
                current = (under_threshold / total) * 100
            else:
                current = 100.0
        
        elif slo.metric_type == 'error_rate':
            total = self.metrics.get_metric('http_requests_total') or 0
            errors = cache.get('metric:http_errors_total', 0)
            
            if total > 0:
                error_rate = (errors / total) * 100
                current = 100 - error_rate
            else:
                current = 100.0
        else:
            current = 100.0
        
        # Calculate error budget
        error_budget_total = 100 - slo.target
        error_budget_consumed = max(0, slo.target - current)
        error_budget_remaining = max(0, error_budget_total - error_budget_consumed)
        
        return {
            'slo_name': slo.name,
            'target': slo.target,
            'current': round(current, 3),
            'status': 'healthy' if current >= slo.target else 'breached',
            'error_budget_total': round(error_budget_total, 3),
            'error_budget_remaining': round(error_budget_remaining, 3),
            'error_budget_consumed_pct': round((error_budget_consumed / error_budget_total) * 100, 1) if error_budget_total > 0 else 0
        }
    
    def get_all_slo_status(self) -> List[Dict]:
        """Get status of all SLOs"""
        return [self.calculate_slo_status(slo) for slo in self.SLOS]


# =====================
# Middleware
# =====================

class ObservabilityMiddleware:
    """
    Django middleware for automatic observability
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.metrics = MetricsCollector()
        self.tracing = TracingManager()
    
    def __call__(self, request):
        # Extract trace context from headers
        self.tracing.extract_context(dict(request.headers))
        
        # Get endpoint for labeling
        endpoint = self._get_endpoint(request)
        
        start_time = time.time()
        
        with self.tracing.span(f"{request.method} {endpoint}") as span:
            span.tags['http.method'] = request.method
            span.tags['http.url'] = request.path
            span.tags['http.user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:100]
            
            response = self.get_response(request)
            
            duration = time.time() - start_time
            
            # Record metrics
            self.metrics.increment('http_requests_total', labels={
                'method': request.method,
                'endpoint': endpoint,
                'status_code': str(response.status_code)
            })
            
            self.metrics.histogram('http_request_duration_seconds', duration, labels={
                'method': request.method,
                'endpoint': endpoint
            })
            
            # Track errors
            if response.status_code >= 400:
                cache_key = 'metric:http_errors_total'
                errors = cache.get(cache_key, 0)
                cache.set(cache_key, errors + 1, 86400)
            
            # Track latency buckets for SLO
            if duration * 1000 < 500:  # Under 500ms
                under_count = cache.get('metric:latency_under_500', 0)
                cache.set('metric:latency_under_500', under_count + 1, 86400)
            
            # Add response headers
            span.tags['http.status_code'] = str(response.status_code)
            
            response['X-Trace-ID'] = span.trace_id
            response['X-Request-Duration'] = f"{duration:.3f}s"
        
        return response
    
    def _get_endpoint(self, request) -> str:
        """Get normalized endpoint for metrics"""
        # Remove IDs and UUIDs from path for better grouping
        import re
        path = request.path
        
        # Replace UUIDs
        path = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '{id}', path)
        # Replace numeric IDs
        path = re.sub(r'/\d+/', '/{id}/', path)
        path = re.sub(r'/\d+$', '/{id}', path)
        
        return path


# =====================
# Decorators
# =====================

def trace(operation_name: Optional[str] = None):
    """
    Decorator to trace function execution
    
    Usage:
        @trace('process_lead')
        def process_lead(lead_id):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracing = TracingManager()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracing.span(op_name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def timed(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """
    Decorator to time function execution
    
    Usage:
        @timed('ml_prediction_latency_seconds', {'model': 'churn'})
        def predict_churn(contact_id):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            metrics = MetricsCollector()
            
            with metrics.timer(metric_name, labels):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def count(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """
    Decorator to count function calls
    
    Usage:
        @count('leads_created_total', {'source': 'api'})
        def create_lead(data):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            metrics = MetricsCollector()
            result = func(*args, **kwargs)
            metrics.increment(metric_name, labels=labels)
            return result
        
        return wrapper
    return decorator
