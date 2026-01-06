"""
Database Performance Optimizations

Provides utilities for database query optimization including:
- Query analysis and profiling
- Index recommendations
- N+1 query detection
- Caching strategies
"""

import logging
import time
from functools import wraps
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db import connection, reset_queries
from django.db.models import Model, QuerySet

logger = logging.getLogger(__name__)


class QueryProfiler:
    """
    Profile database queries for performance optimization.
    """

    def __init__(self):
        self.queries: list[dict[str, Any]] = []
        self.start_time: float = 0
        self.enabled = settings.DEBUG

    def __enter__(self):
        if self.enabled:
            reset_queries()
            self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enabled:
            self.queries = list(connection.queries)
            self.elapsed_time = time.time() - self.start_time

    def get_stats(self) -> dict[str, Any]:
        """Get query statistics."""
        if not self.queries:
            return {}

        total_time = sum(float(q.get('time', 0)) for q in self.queries)

        return {
            'query_count': len(self.queries),
            'total_db_time': round(total_time * 1000, 2),  # ms
            'elapsed_time': round(self.elapsed_time * 1000, 2),  # ms
            'avg_query_time': round((total_time / len(self.queries)) * 1000, 2) if self.queries else 0,
            'queries': self.queries if settings.DEBUG else [],
        }

    def detect_n_plus_one(self) -> list[dict[str, Any]]:
        """Detect potential N+1 query patterns."""
        if not self.queries:
            return []

        # Group similar queries
        query_patterns: dict[str, list[dict]] = {}
        for query in self.queries:
            sql = query.get('sql', '')
            # Normalize query (remove specific IDs)
            import re
            normalized = re.sub(r'\b\d+\b', '?', sql)
            normalized = re.sub(r"'[^']*'", '?', normalized)

            if normalized not in query_patterns:
                query_patterns[normalized] = []
            query_patterns[normalized].append(query)

        # Find patterns with many similar queries
        n_plus_one = []
        for pattern, queries in query_patterns.items():
            if len(queries) > 3:  # Threshold for N+1 detection
                n_plus_one.append({
                    'pattern': pattern[:200],
                    'count': len(queries),
                    'total_time': sum(float(q.get('time', 0)) for q in queries),
                    'suggestion': 'Consider using select_related() or prefetch_related()'
                })

        return n_plus_one


def profile_queries(view_func):
    """Decorator to profile queries in a view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not settings.DEBUG:
            return view_func(request, *args, **kwargs)

        with QueryProfiler() as profiler:
            response = view_func(request, *args, **kwargs)

        stats = profiler.get_stats()
        n_plus_one = profiler.detect_n_plus_one()

        if stats.get('query_count', 0) > 10:
            logger.warning(
                f"High query count in {view_func.__name__}: "
                f"{stats['query_count']} queries in {stats['elapsed_time']}ms"
            )

        if n_plus_one:
            logger.warning(
                f"Potential N+1 queries detected in {view_func.__name__}: "
                f"{len(n_plus_one)} patterns"
            )

        return response
    return wrapper


class CachedQuerySet:
    """
    Wrapper for QuerySet with automatic caching.
    """

    def __init__(
        self,
        queryset: QuerySet,
        cache_key: str,
        timeout: int = 300,
        version: int | None = None
    ):
        self.queryset = queryset
        self.cache_key = cache_key
        self.timeout = timeout
        self.version = version

    def get(self) -> list[Model]:
        """Get results from cache or database."""
        cached = cache.get(self.cache_key, version=self.version)
        if cached is not None:
            return cached

        results = list(self.queryset)
        cache.set(self.cache_key, results, timeout=self.timeout, version=self.version)
        return results

    def invalidate(self) -> None:
        """Invalidate the cache."""
        cache.delete(self.cache_key, version=self.version)


def cached_query(
    cache_key: str,
    timeout: int = 300,
    version: int | None = None
):
    """Decorator to cache query results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key with args
            full_key = f"{cache_key}:{hash(str(args) + str(kwargs))}"

            cached = cache.get(full_key, version=version)
            if cached is not None:
                return cached

            result = func(*args, **kwargs)
            cache.set(full_key, result, timeout=timeout, version=version)
            return result
        return wrapper
    return decorator


class OptimizedQueryBuilder:
    """
    Build optimized queries with automatic relationship loading.
    """

    def __init__(self, model: type[Model]):
        self.model = model
        self.select_related_fields: list[str] = []
        self.prefetch_related_fields: list[Any] = []
        self.only_fields: list[str] = []
        self.defer_fields: list[str] = []

    def with_related(self, *fields: str) -> 'OptimizedQueryBuilder':
        """Add select_related fields."""
        self.select_related_fields.extend(fields)
        return self

    def with_prefetch(self, *fields) -> 'OptimizedQueryBuilder':
        """Add prefetch_related fields."""
        self.prefetch_related_fields.extend(fields)
        return self

    def only(self, *fields: str) -> 'OptimizedQueryBuilder':
        """Limit fields loaded."""
        self.only_fields.extend(fields)
        return self

    def defer(self, *fields: str) -> 'OptimizedQueryBuilder':
        """Defer loading of fields."""
        self.defer_fields.extend(fields)
        return self

    def build(self) -> QuerySet:
        """Build the optimized queryset."""
        queryset = self.model.objects.all()

        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)

        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        if self.only_fields:
            queryset = queryset.only(*self.only_fields)
        elif self.defer_fields:
            queryset = queryset.defer(*self.defer_fields)

        return queryset


# Common optimization patterns
def optimize_contact_query() -> QuerySet:
    """Get optimized contact queryset."""
    from contact_management.models import Contact
    return OptimizedQueryBuilder(Contact)\
        .with_related('created_by', 'assigned_to')\
        .with_prefetch('tags', 'communications')\
        .defer('notes', 'description')\
        .build()


def optimize_lead_query() -> QuerySet:
    """Get optimized lead queryset."""
    from lead_management.models import Lead
    return OptimizedQueryBuilder(Lead)\
        .with_related('created_by', 'assigned_to', 'converted_contact')\
        .with_prefetch('activities', 'tags')\
        .defer('notes', 'description')\
        .build()


def optimize_opportunity_query() -> QuerySet:
    """Get optimized opportunity queryset."""
    from opportunity_management.models import Opportunity
    return OptimizedQueryBuilder(Opportunity)\
        .with_related('contact', 'lead', 'owner')\
        .with_prefetch('products', 'activities')\
        .defer('notes', 'description')\
        .build()


def get_index_recommendations(model: type[Model]) -> list[dict[str, Any]]:
    """Get index recommendations for a model based on common query patterns."""
    recommendations = []

    # Analyze model fields
    for field in model._meta.get_fields():
        if hasattr(field, 'db_index'):
            # Fields commonly used in WHERE clauses
            if field.name in ['status', 'created_at', 'updated_at', 'email', 'is_active']:
                if not field.db_index and not field.primary_key:
                    recommendations.append({
                        'field': field.name,
                        'model': model.__name__,
                        'recommendation': f'Consider adding db_index=True to {field.name}',
                        'reason': 'Commonly used in filters and ordering'
                    })

    # Check for missing composite indexes
    if hasattr(model._meta, 'indexes'):
        existing_indexes = [idx.fields for idx in model._meta.indexes]
    else:
        existing_indexes = []

    # Recommend common composite indexes
    composite_recommendations = [
        (['created_at', 'status'], 'Useful for date-based status queries'),
        (['assigned_to', 'status'], 'Useful for user workload queries'),
    ]

    for fields, reason in composite_recommendations:
        if list(fields) not in existing_indexes:
            # Check if model has these fields
            model_fields = [f.name for f in model._meta.get_fields()]
            if all(f in model_fields for f in fields):
                recommendations.append({
                    'fields': fields,
                    'model': model.__name__,
                    'recommendation': f'Consider adding composite index on {fields}',
                    'reason': reason
                })

    return recommendations
