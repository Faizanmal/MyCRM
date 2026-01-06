"""
Enterprise Module for MyCRM
===========================

This module contains enterprise-grade features including:
- HashiCorp Vault integration for secrets management
- Zero-trust security middleware
- Observability stack (OpenTelemetry, Prometheus)
- MLOps pipeline management
- Compliance automation (SOC 2, ISO 27001, GDPR)
- AI services with GPT-4 integration
- Multi-tier caching with Redis Cluster support
- GraphQL API layer
- Database optimization and read replica routing
- Health check endpoints for Kubernetes

Author: MyCRM Enterprise Team
Version: 2.0.0
"""

__version__ = '2.0.0'
__author__ = 'MyCRM Enterprise Team'

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    """Lazy load enterprise components."""

    # Vault Manager - Secrets Management
    if name in ('VaultClient', 'VaultConfig', 'SecretNotFoundError', 'VaultManager'):
        from .vault_manager import SecretNotFoundError, VaultClient, VaultConfig
        if name == 'VaultManager':
            return VaultClient
        return locals()[name]

    # Zero Trust Security
    if name in ('ZeroTrustMiddleware', 'DeviceTrustManager', 'ContinuousAuthenticator',
                'TrustLevel', 'zero_trust_required', 'ZeroTrustPolicy'):
        from .zero_trust import (
            ContinuousAuthenticator,
            DeviceTrustManager,
            TrustLevel,
            ZeroTrustMiddleware,
            zero_trust_required,
        )
        if name == 'ZeroTrustPolicy':
            return TrustLevel
        return locals()[name]

    # Observability
    if name in ('DistributedTracer', 'PrometheusMetrics', 'BusinessMetrics',
                'setup_observability', 'trace', 'track_metric',
                'MetricsCollector', 'TracingManager'):
        from .observability import (
            BusinessMetrics,
            DistributedTracer,
            PrometheusMetrics,
            setup_observability,
            trace,
            track_metric,
        )
        if name == 'MetricsCollector':
            return PrometheusMetrics
        if name == 'TracingManager':
            return DistributedTracer
        return locals()[name]

    # MLOps
    if name in ('ModelRegistry', 'FeatureStore', 'ABTestManager',
                'ModelVersion', 'Experiment', 'MLOpsManager'):
        from .mlops import ABTestManager, Experiment, FeatureStore, ModelRegistry, ModelVersion
        if name == 'MLOpsManager':
            return ModelRegistry
        return locals()[name]

    # Compliance
    if name in ('ComplianceChecker', 'EvidenceCollector', 'ComplianceReporter',
                'ComplianceStatus', 'ComplianceFramework',
                'ComplianceEngine', 'AuditAutomation'):
        from .compliance import (
            ComplianceChecker,
            ComplianceFramework,
            ComplianceReporter,
            ComplianceStatus,
            EvidenceCollector,
        )
        if name == 'ComplianceEngine':
            return ComplianceChecker
        if name == 'AuditAutomation':
            return EvidenceCollector
        return locals()[name]

    # AI Services
    if name in ('AIAssistant', 'AIConfig', 'ConversationContext'):
        from .ai_services import AIAssistant, AIConfig, ConversationContext
        return locals()[name]

    # Caching
    if name in ('CacheManager', 'MultiTierCache', 'InMemoryCache', 'RedisCache',
                'CacheStampedeProtection', 'CircuitBreaker', 'cached',
                'cache_invalidate', 'CachedModelMixin'):
        from .caching import (
            CachedModelMixin,
            CacheManager,
            CacheStampedeProtection,
            CircuitBreaker,
            InMemoryCache,
            MultiTierCache,
            RedisCache,
            cache_invalidate,
            cached,
        )
        return locals()[name]

    # GraphQL
    if name in ('graphql_schema', 'graphql_view'):
        from .graphql_api import graphql_view
        from .graphql_api import schema as graphql_schema
        if name == 'graphql_schema':
            return graphql_schema
        return graphql_view

    # Database
    if name in ('ReadReplicaRouter', 'ReplicaContext', 'ConnectionPoolManager',
                'QueryAnalyzer', 'SlowQueryLogger', 'PartitionManager',
                'DatabaseHealthMonitor', 'QueryOptimizer', 'use_primary',
                'log_slow_queries', 'query_timer'):
        from .database import (
            ConnectionPoolManager,
            DatabaseHealthMonitor,
            PartitionManager,
            QueryAnalyzer,
            QueryOptimizer,
            ReadReplicaRouter,
            ReplicaContext,
            SlowQueryLogger,
            log_slow_queries,
            query_timer,
            use_primary,
        )
        return locals()[name]

    # Health Checks
    if name in ('HealthCheckRegistry', 'HealthChecker', 'HealthStatus',
                'HealthCheckResult', 'AggregatedHealth', 'DatabaseHealthChecker',
                'RedisHealthChecker', 'CeleryHealthChecker', 'DiskHealthChecker',
                'MemoryHealthChecker', 'ExternalServiceHealthChecker',
                'setup_default_health_checks', 'get_health_urls', 'StartupView'):
        from .health import (
            AggregatedHealth,
            CeleryHealthChecker,
            DatabaseHealthChecker,
            DiskHealthChecker,
            ExternalServiceHealthChecker,
            HealthChecker,
            HealthCheckRegistry,
            HealthCheckResult,
            HealthStatus,
            MemoryHealthChecker,
            RedisHealthChecker,
            StartupView,
            get_health_urls,
            setup_default_health_checks,
        )
        return locals()[name]

    raise AttributeError(f"module 'enterprise' has no attribute '{name}'")


__all__ = [
    # Version
    '__version__',
    '__author__',

    # Vault (including legacy names)
    'VaultClient',
    'VaultConfig',
    'SecretNotFoundError',
    'VaultManager',  # Legacy alias

    # Zero Trust (including legacy names)
    'ZeroTrustMiddleware',
    'DeviceTrustManager',
    'ContinuousAuthenticator',
    'TrustLevel',
    'zero_trust_required',
    'ZeroTrustPolicy',  # Legacy alias

    # Observability (including legacy names)
    'DistributedTracer',
    'PrometheusMetrics',
    'BusinessMetrics',
    'setup_observability',
    'trace',
    'track_metric',
    'MetricsCollector',  # Legacy alias
    'TracingManager',  # Legacy alias

    # MLOps (including legacy names)
    'ModelRegistry',
    'FeatureStore',
    'ABTestManager',
    'ModelVersion',
    'Experiment',
    'MLOpsManager',  # Legacy alias

    # Compliance (including legacy names)
    'ComplianceChecker',
    'EvidenceCollector',
    'ComplianceReporter',
    'ComplianceStatus',
    'ComplianceFramework',
    'ComplianceEngine',  # Legacy alias
    'AuditAutomation',  # Legacy alias

    # AI Services
    'AIAssistant',
    'AIConfig',
    'ConversationContext',

    # Caching
    'CacheManager',
    'MultiTierCache',
    'InMemoryCache',
    'RedisCache',
    'CacheStampedeProtection',
    'CircuitBreaker',
    'cached',
    'cache_invalidate',
    'CachedModelMixin',

    # GraphQL
    'graphql_schema',
    'graphql_view',

    # Database
    'ReadReplicaRouter',
    'ReplicaContext',
    'ConnectionPoolManager',
    'QueryAnalyzer',
    'SlowQueryLogger',
    'PartitionManager',
    'DatabaseHealthMonitor',
    'QueryOptimizer',
    'use_primary',
    'log_slow_queries',
    'query_timer',

    # Health
    'HealthCheckRegistry',
    'HealthChecker',
    'HealthStatus',
    'HealthCheckResult',
    'AggregatedHealth',
    'DatabaseHealthChecker',
    'RedisHealthChecker',
    'CeleryHealthChecker',
    'DiskHealthChecker',
    'MemoryHealthChecker',
    'ExternalServiceHealthChecker',
    'setup_default_health_checks',
    'get_health_urls',
    'StartupView',
]


def setup_enterprise(settings_module=None):
    """
    Initialize all enterprise features.

    Call this in your Django settings or app ready() method:

        from enterprise import setup_enterprise
        setup_enterprise()

    Or with custom settings:

        setup_enterprise(settings_module=my_settings)
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Setup observability
        from .observability import setup_observability
        setup_observability()
        logger.info("Enterprise observability initialized")

        # Setup health checks
        from .health import StartupView, setup_default_health_checks
        setup_default_health_checks()
        logger.info("Enterprise health checks initialized")

        # Mark startup complete
        StartupView.mark_startup_complete()
        logger.info("Enterprise module startup complete")

    except Exception as e:
        logger.error(f"Error initializing enterprise features: {e}")
        raise
