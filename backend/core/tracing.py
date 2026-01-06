"""
OpenTelemetry Instrumentation for MyCRM
Provides distributed tracing across all services
"""

from django.conf import settings

# Only initialize if OpenTelemetry is enabled
OTEL_ENABLED = getattr(settings, 'OTEL_ENABLED', False)

if OTEL_ENABLED:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.django import DjangoInstrumentor
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    def initialize_tracer():
        """Initialize OpenTelemetry tracer"""

        # Create resource with service information
        resource = Resource.create({
            SERVICE_NAME: getattr(settings, 'OTEL_SERVICE_NAME', 'mycrm-backend'),
            SERVICE_VERSION: getattr(settings, 'VERSION', '1.0.0'),
            "deployment.environment": "production" if not settings.DEBUG else "development"
        })

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Configure OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=getattr(settings, 'OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317'),
            insecure=True  # Use insecure for local development
        )

        # Add span processor
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        # Instrument frameworks
        DjangoInstrumentor().instrument()
        RequestsInstrumentor().instrument()
        RedisInstrumentor().instrument()
        Psycopg2Instrumentor().instrument()

        print("✓ OpenTelemetry instrumentation initialized")

    # Initialize when module is imported
    try:
        initialize_tracer()
    except Exception as e:
        print(f"Warning: Failed to initialize OpenTelemetry: {e}")
else:
    print("OpenTelemetry is disabled")


def get_tracer(name: str):
    """Get a tracer instance"""
    if OTEL_ENABLED:
        return trace.get_tracer(name)
    return None


def trace_function(func):
    """Decorator to trace a function"""
    if not OTEL_ENABLED:
        return func

    def wrapper(*args, **kwargs):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(func.__name__):
            return func(*args, **kwargs)

    return wrapper
