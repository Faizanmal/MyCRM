"""
Advanced Caching Strategies - Edge caching, prefetching, and query optimization.
"""

import hashlib
import json
import uuid
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from django.contrib.postgres.fields import ArrayField
from django.core.cache import caches
from django.db import models
from django.utils import timezone


class CacheConfiguration(models.Model):
    """Configuration for different cache layers."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # Cache layer
    layer = models.CharField(
        max_length=20,
        choices=[
            ('memory', 'In-Memory (Redis)'),
            ('database', 'Database Query Cache'),
            ('edge', 'Edge/CDN Cache'),
            ('browser', 'Browser Cache'),
        ]
    )

    # Pattern matching
    url_pattern = models.CharField(max_length=500)  # Regex pattern
    method = models.CharField(max_length=10, default='GET')

    # TTL settings
    ttl_seconds = models.PositiveIntegerField(default=300)
    stale_ttl_seconds = models.PositiveIntegerField(default=60)  # Serve stale while revalidating

    # Cache key configuration
    vary_headers = ArrayField(models.CharField(max_length=100), default=list)
    # e.g., ['Authorization', 'Accept-Language']
    vary_query_params = ArrayField(models.CharField(max_length=100), default=list)
    include_user_id = models.BooleanField(default=True)

    # Invalidation
    invalidation_tags = ArrayField(models.CharField(max_length=100), default=list)
    # e.g., ['contacts', 'user:{user_id}']

    # Conditions
    cache_private = models.BooleanField(default=True)  # Per-user caching
    cache_authenticated_only = models.BooleanField(default=True)
    min_response_size = models.PositiveIntegerField(default=0)
    max_response_size = models.PositiveIntegerField(default=1048576)  # 1MB

    # Status
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cache_configuration'
        ordering = ['-priority']


class CacheEntry(models.Model):
    """Tracks cache entries for debugging and analytics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cache_key = models.CharField(max_length=500)
    cache_layer = models.CharField(max_length=20)

    # Request context
    url = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    user_id = models.UUIDField(null=True, blank=True)

    # Cache data
    response_size = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100)

    # Timing
    ttl_seconds = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    # Status
    hit_count = models.PositiveIntegerField(default=0)
    last_hit_at = models.DateTimeField(null=True)
    invalidated_at = models.DateTimeField(null=True)
    invalidation_reason = models.CharField(max_length=200, blank=True)

    # Tags for invalidation
    tags = ArrayField(models.CharField(max_length=100), default=list)

    class Meta:
        db_table = 'cache_entry'
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['tags']),
        ]


class PrefetchRule(models.Model):
    """Rules for prefetching data."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Trigger conditions
    trigger_type = models.CharField(
        max_length=30,
        choices=[
            ('page_load', 'On Page Load'),
            ('user_action', 'On User Action'),
            ('time_based', 'Time-Based'),
            ('prediction', 'Predictive'),
        ]
    )
    trigger_pattern = models.CharField(max_length=500)  # URL pattern or action name

    # What to prefetch
    prefetch_urls = ArrayField(models.CharField(max_length=500), default=list)
    prefetch_priority = models.CharField(
        max_length=10,
        choices=[('high', 'High'), ('low', 'Low')],
        default='low'
    )

    # Conditions
    require_connection = models.CharField(
        max_length=20,
        choices=[
            ('any', 'Any Connection'),
            ('fast', 'Fast Connection Only'),
            ('wifi', 'WiFi Only'),
        ],
        default='fast'
    )
    max_prefetch_count = models.PositiveIntegerField(default=5)
    delay_ms = models.PositiveIntegerField(default=100)

    # User targeting
    user_segments = ArrayField(models.CharField(max_length=50), default=list)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cache_prefetch_rule'


class QueryCacheEntry(models.Model):
    """Caches expensive database queries."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Query identification
    query_hash = models.CharField(max_length=64, unique=True)  # SHA256 of query + params
    query_type = models.CharField(max_length=50)  # model name or custom identifier

    # Query details (for debugging)
    query_sql = models.TextField(blank=True)  # Sanitized SQL
    query_params_hash = models.CharField(max_length=64)

    # Result
    result_count = models.PositiveIntegerField(default=0)
    result_size_bytes = models.PositiveIntegerField(default=0)

    # Timing
    original_execution_ms = models.PositiveIntegerField()  # How long query took
    ttl_seconds = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    # Usage stats
    hit_count = models.PositiveIntegerField(default=0)
    total_time_saved_ms = models.PositiveIntegerField(default=0)

    # Invalidation
    invalidation_keys = ArrayField(models.CharField(max_length=100), default=list)
    # e.g., ['model:Contact', 'user:123']

    class Meta:
        db_table = 'cache_query_entry'
        indexes = [
            models.Index(fields=['query_type']),
            models.Index(fields=['expires_at']),
        ]


class CacheMetrics(models.Model):
    """Aggregated cache performance metrics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Time period
    period_type = models.CharField(
        max_length=10,
        choices=[('minute', 'Minute'), ('hour', 'Hour'), ('day', 'Day')]
    )
    period_start = models.DateTimeField()

    # Cache layer
    cache_layer = models.CharField(max_length=20)
    cache_key_prefix = models.CharField(max_length=100, blank=True)  # For grouping

    # Hit/Miss metrics
    total_requests = models.PositiveIntegerField(default=0)
    cache_hits = models.PositiveIntegerField(default=0)
    cache_misses = models.PositiveIntegerField(default=0)
    stale_hits = models.PositiveIntegerField(default=0)  # Served stale while revalidating

    # Performance
    avg_hit_time_ms = models.FloatField(default=0)
    avg_miss_time_ms = models.FloatField(default=0)
    total_time_saved_ms = models.PositiveIntegerField(default=0)

    # Size metrics
    total_bytes_served = models.BigIntegerField(default=0)
    avg_entry_size_bytes = models.PositiveIntegerField(default=0)

    # Invalidation
    invalidations = models.PositiveIntegerField(default=0)
    expirations = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cache_metrics'
        indexes = [
            models.Index(fields=['period_type', 'period_start']),
            models.Index(fields=['cache_layer', 'period_start']),
        ]


# Services

class CacheKeyGenerator:
    """Generates consistent cache keys."""

    @staticmethod
    def generate(
        prefix: str,
        path: str,
        method: str = 'GET',
        user_id: str | None = None,
        query_params: dict | None = None,
        vary_headers: dict | None = None,
    ) -> str:
        """Generate a cache key from request parameters."""
        key_parts = [prefix, method, path]

        if user_id:
            key_parts.append(f'user:{user_id}')

        if query_params:
            sorted_params = sorted(query_params.items())
            params_str = '&'.join(f'{k}={v}' for k, v in sorted_params)
            key_parts.append(f'params:{hashlib.md5(params_str.encode()).hexdigest()[:8]}')

        if vary_headers:
            sorted_headers = sorted(vary_headers.items())
            headers_str = '&'.join(f'{k}={v}' for k, v in sorted_headers)
            key_parts.append(f'headers:{hashlib.md5(headers_str.encode()).hexdigest()[:8]}')

        return ':'.join(key_parts)

    @staticmethod
    def generate_query_key(query_type: str, query_params: dict) -> str:
        """Generate a cache key for a database query."""
        params_json = json.dumps(query_params, sort_keys=True)
        params_hash = hashlib.sha256(params_json.encode()).hexdigest()
        return f'query:{query_type}:{params_hash}'


class CacheInvalidationService:
    """Service for cache invalidation."""

    def __init__(self):
        self.cache = caches['default']

    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with a specific tag."""
        # In production, use Redis SCAN + DEL or a tag-based system
        invalidated = 0

        # Find all entries with this tag
        entries = CacheEntry.objects.filter(
            tags__contains=[tag],
            invalidated_at__isnull=True
        )

        for entry in entries:
            self.cache.delete(entry.cache_key)
            entry.invalidated_at = timezone.now()
            entry.invalidation_reason = f'tag:{tag}'
            entry.save(update_fields=['invalidated_at', 'invalidation_reason'])
            invalidated += 1

        return invalidated

    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        # In production, use Redis SCAN with pattern matching
        return 0

    def invalidate_for_model(self, model_name: str, instance_id: str | None = None) -> int:
        """Invalidate cache for a model change."""
        tags_to_invalidate = [f'model:{model_name}']

        if instance_id:
            tags_to_invalidate.append(f'{model_name}:{instance_id}')

        total = 0
        for tag in tags_to_invalidate:
            total += self.invalidate_by_tag(tag)

        return total

    def invalidate_for_user(self, user_id: str) -> int:
        """Invalidate all user-specific cache entries."""
        return self.invalidate_by_tag(f'user:{user_id}')


class SmartCacheService:
    """Intelligent caching with automatic optimization."""

    def __init__(self):
        self.cache = caches['default']
        self.key_generator = CacheKeyGenerator()
        self.invalidation_service = CacheInvalidationService()

    def get_or_set(
        self,
        key: str,
        callback: Callable,
        ttl: int = 300,
        tags: list[str] = None,
        stale_ttl: int = 60,
    ) -> Any:
        """Get from cache or set using callback."""
        # Try to get from cache
        result = self.cache.get(key)

        if result is not None:
            self._record_hit(key)
            return result

        # Cache miss - execute callback
        start_time = timezone.now()
        result = callback()
        execution_time = (timezone.now() - start_time).total_seconds() * 1000

        # Store in cache
        self.cache.set(key, result, ttl)

        # Record metrics
        self._record_miss(key, execution_time)

        # Store entry for tracking
        if tags:
            CacheEntry.objects.create(
                cache_key=key,
                cache_layer='memory',
                url='',
                method='GET',
                response_size=len(str(result)),
                content_type='application/json',
                ttl_seconds=ttl,
                expires_at=timezone.now() + timedelta(seconds=ttl),
                tags=tags,
            )

        return result

    def get_with_stale(
        self,
        key: str,
        callback: Callable,
        ttl: int = 300,
        stale_ttl: int = 60,
    ) -> Any:
        """Get from cache, serving stale data while revalidating."""
        stale_key = f'{key}:stale'
        fresh_key = f'{key}:fresh'

        # Check for fresh data
        fresh = self.cache.get(fresh_key)
        if fresh is not None:
            return fresh

        # Check for stale data
        stale = self.cache.get(stale_key)

        if stale is not None:
            # Serve stale, trigger background refresh
            self._trigger_background_refresh(key, callback, ttl, stale_ttl)
            return stale

        # Complete cache miss
        result = callback()

        # Store both fresh and stale versions
        self.cache.set(fresh_key, result, ttl)
        self.cache.set(stale_key, result, ttl + stale_ttl)

        return result

    def _record_hit(self, key: str) -> None:
        """Record a cache hit."""
        CacheEntry.objects.filter(cache_key=key).update(
            hit_count=models.F('hit_count') + 1,
            last_hit_at=timezone.now()
        )

    def _record_miss(self, key: str, execution_time: float) -> None:
        """Record a cache miss."""
        pass  # Metrics aggregation

    def _trigger_background_refresh(
        self,
        key: str,
        callback: Callable,
        ttl: int,
        stale_ttl: int,
    ) -> None:
        """Trigger a background cache refresh."""
        # In production, use Celery or similar for background task
        pass


class PrefetchService:
    """Service for intelligent data prefetching."""

    def __init__(self):
        self.cache_service = SmartCacheService()

    def get_prefetch_hints(self, current_url: str, user_id: str) -> list[dict]:
        """Get prefetch hints based on current page and user behavior."""
        hints = []

        # Get matching prefetch rules
        rules = PrefetchRule.objects.filter(
            is_active=True,
            trigger_pattern__icontains=current_url.split('?')[0]
        )

        for rule in rules:
            for url in rule.prefetch_urls[:rule.max_prefetch_count]:
                hints.append({
                    'url': url,
                    'priority': rule.prefetch_priority,
                    'delay_ms': rule.delay_ms,
                })

        # Add predictive prefetches based on user behavior
        predicted = self._predict_next_pages(current_url, user_id)
        hints.extend(predicted)

        return hints

    def _predict_next_pages(self, current_url: str, user_id: str) -> list[dict]:
        """Predict next pages user might visit."""
        # In production, use ML model based on user behavior
        predictions = []

        # Simple heuristics
        if '/contacts' in current_url:
            predictions.append({'url': '/api/contacts/recent', 'priority': 'low', 'delay_ms': 500})
        elif '/deals' in current_url:
            predictions.append({'url': '/api/deals/pipeline', 'priority': 'low', 'delay_ms': 500})

        return predictions

    def prefetch(self, urls: list[str], user_id: str) -> dict[str, bool]:
        """Prefetch multiple URLs into cache."""
        results = {}

        for url in urls:
            cache_key = self.cache_service.key_generator.generate(
                prefix='prefetch',
                path=url,
                user_id=user_id
            )

            # Check if already cached
            if self.cache_service.cache.get(cache_key):
                results[url] = True
                continue

            # Would trigger actual prefetch in production
            results[url] = False

        return results


class QueryOptimizer:
    """Service for query caching and optimization."""

    def __init__(self):
        self.cache = caches['default']

    def cached_query(
        self,
        query_type: str,
        queryset,
        params: dict,
        ttl: int = 300,
    ):
        """Execute a query with caching."""
        cache_key = CacheKeyGenerator.generate_query_key(query_type, params)

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            self._record_query_hit(cache_key)
            return cached

        # Execute query
        start_time = timezone.now()
        result = list(queryset)
        execution_time = (timezone.now() - start_time).total_seconds() * 1000

        # Cache result
        self.cache.set(cache_key, result, ttl)

        # Record for optimization
        QueryCacheEntry.objects.update_or_create(
            query_hash=cache_key,
            defaults={
                'query_type': query_type,
                'result_count': len(result),
                'original_execution_ms': int(execution_time),
                'ttl_seconds': ttl,
                'expires_at': timezone.now() + timedelta(seconds=ttl),
            }
        )

        return result

    def _record_query_hit(self, cache_key: str) -> None:
        """Record a query cache hit."""
        QueryCacheEntry.objects.filter(query_hash=cache_key).update(
            hit_count=models.F('hit_count') + 1
        )

    def get_optimization_suggestions(self) -> list[dict]:
        """Get suggestions for query optimization."""
        suggestions = []

        # Find frequently executed slow queries
        slow_queries = QueryCacheEntry.objects.filter(
            original_execution_ms__gt=100,
            hit_count__gt=10
        ).order_by('-hit_count')[:10]

        for query in slow_queries:
            suggestions.append({
                'query_type': query.query_type,
                'avg_time_ms': query.original_execution_ms,
                'hit_count': query.hit_count,
                'recommendation': 'Consider adding database indexes or optimizing query',
                'potential_time_saved_ms': query.original_execution_ms * query.hit_count,
            })

        return suggestions


class EdgeCacheService:
    """Service for CDN/edge cache management."""

    def __init__(self, cdn_provider: str = 'cloudflare'):
        self.provider = cdn_provider

    def purge_url(self, url: str) -> bool:
        """Purge a specific URL from edge cache."""
        # In production, call CDN API
        return True

    def purge_by_tag(self, tag: str) -> bool:
        """Purge edge cache by tag."""
        # In production, call CDN API with tag purge
        return True

    def get_cache_headers(self, config: CacheConfiguration) -> dict[str, str]:
        """Generate cache control headers."""
        headers = {}

        if config.cache_private:
            headers['Cache-Control'] = f'private, max-age={config.ttl_seconds}'
        else:
            headers['Cache-Control'] = f'public, max-age={config.ttl_seconds}'

        if config.stale_ttl_seconds:
            headers['Cache-Control'] += f', stale-while-revalidate={config.stale_ttl_seconds}'

        if config.vary_headers:
            headers['Vary'] = ', '.join(config.vary_headers)

        if config.invalidation_tags:
            headers['Cache-Tag'] = ','.join(config.invalidation_tags)

        return headers
