"""
Caching Layer Utilities

Provides advanced caching patterns for:
- Query result caching
- Cache invalidation strategies
- Cache warming
- Distributed caching
"""

import logging
import hashlib
import json
from typing import Any, Callable, Optional, List, Type, TypeVar
from functools import wraps
from datetime import timedelta

from django.core.cache import cache, caches
from django.db.models import Model, QuerySet
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheKey:
    """Generate consistent cache keys."""
    
    PREFIX = 'mycrm'
    
    @classmethod
    def make(cls, *parts: str) -> str:
        """Generate a cache key from parts."""
        return f"{cls.PREFIX}:{':'.join(str(p) for p in parts)}"
    
    @classmethod
    def hash_query(cls, query_string: str, params: dict = None) -> str:
        """Generate a hash for a query string and parameters."""
        content = query_string + json.dumps(params or {}, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    @classmethod
    def for_model(cls, model: Type[Model], pk: Any = None) -> str:
        """Generate a cache key for a model instance."""
        app = model._meta.app_label
        name = model._meta.model_name
        
        if pk is not None:
            return cls.make(app, name, str(pk))
        return cls.make(app, name, 'all')
    
    @classmethod
    def for_user(cls, user_id: int, *parts: str) -> str:
        """Generate a cache key scoped to a user."""
        return cls.make('user', str(user_id), *parts)


class CacheManager:
    """
    Advanced cache management with patterns for common use cases.
    """
    
    DEFAULT_TIMEOUT = 300  # 5 minutes
    LONG_TIMEOUT = 3600    # 1 hour
    SHORT_TIMEOUT = 60     # 1 minute
    
    @classmethod
    def get_or_set(
        cls,
        key: str,
        factory: Callable[[], T],
        timeout: int = DEFAULT_TIMEOUT,
        version: Optional[int] = None
    ) -> T:
        """Get value from cache or compute and store it."""
        value = cache.get(key, version=version)
        
        if value is None:
            value = factory()
            cache.set(key, value, timeout=timeout, version=version)
            logger.debug(f"Cache miss for key: {key}")
        else:
            logger.debug(f"Cache hit for key: {key}")
            
        return value
    
    @classmethod
    def get_many_or_set(
        cls,
        keys: List[str],
        factory: Callable[[List[str]], dict],
        timeout: int = DEFAULT_TIMEOUT
    ) -> dict:
        """Get multiple values, computing missing ones."""
        cached = cache.get_many(keys)
        missing_keys = [k for k in keys if k not in cached]
        
        if missing_keys:
            computed = factory(missing_keys)
            cache.set_many(computed, timeout=timeout)
            cached.update(computed)
            
        return cached
    
    @classmethod
    def delete_pattern(cls, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        # Note: This works with Redis backend
        try:
            redis_cache = caches['default']
            if hasattr(redis_cache, 'delete_pattern'):
                return redis_cache.delete_pattern(f"*{pattern}*")
        except Exception as e:
            logger.warning(f"Failed to delete pattern {pattern}: {e}")
        return 0
    
    @classmethod
    def invalidate_model(cls, model: Type[Model], pk: Any = None) -> None:
        """Invalidate cache for a model or instance."""
        if pk is not None:
            # Invalidate specific instance
            key = CacheKey.for_model(model, pk)
            cache.delete(key)
        else:
            # Invalidate all instances
            key = CacheKey.for_model(model)
            cache.delete(key)
            
        # Also invalidate list cache
        list_key = CacheKey.for_model(model) + ':list*'
        cls.delete_pattern(list_key)
        
        logger.debug(f"Invalidated cache for {model.__name__}")
    
    @classmethod
    def increment(cls, key: str, delta: int = 1, timeout: int = DEFAULT_TIMEOUT) -> int:
        """Atomically increment a counter."""
        try:
            return cache.incr(key, delta)
        except ValueError:
            cache.set(key, delta, timeout=timeout)
            return delta
    
    @classmethod
    def decrement(cls, key: str, delta: int = 1) -> int:
        """Atomically decrement a counter."""
        try:
            return cache.decr(key, delta)
        except ValueError:
            return 0


def cached_query(
    key_prefix: str,
    timeout: int = CacheManager.DEFAULT_TIMEOUT,
    key_builder: Callable[..., str] = None
):
    """
    Decorator to cache query results.
    
    Usage:
        @cached_query('leads', timeout=300)
        def get_leads_by_status(status):
            return Lead.objects.filter(status=status)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Build cache key
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                key_parts = [key_prefix, func.__name__]
                key_parts.extend(str(a) for a in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                key = CacheKey.make(*key_parts)
            
            # Get or compute
            def factory():
                result = func(*args, **kwargs)
                # Convert QuerySet to list for caching
                if isinstance(result, QuerySet):
                    return list(result)
                return result
            
            return CacheManager.get_or_set(key, factory, timeout)
        
        # Add method to invalidate this query's cache
        wrapper.invalidate = lambda: CacheManager.delete_pattern(key_prefix)
        
        return wrapper
    return decorator


def cached_property_with_ttl(ttl: int = CacheManager.DEFAULT_TIMEOUT):
    """
    Decorator for cached properties with TTL.
    
    Usage:
        class MyModel(Model):
            @cached_property_with_ttl(ttl=300)
            def expensive_computation(self):
                return self.related_objects.aggregate(...)
    """
    def decorator(method: Callable[[Any], T]) -> property:
        attr_name = f'_cached_{method.__name__}'
        
        @property
        @wraps(method)
        def wrapper(self) -> T:
            key = CacheKey.make(
                self.__class__.__name__,
                str(self.pk),
                method.__name__
            )
            
            def factory():
                return method(self)
            
            return CacheManager.get_or_set(key, factory, ttl)
        
        return wrapper
    return decorator


class QueryResultCache:
    """
    Cache queryset results with automatic invalidation.
    """
    
    def __init__(
        self,
        model: Type[Model],
        timeout: int = CacheManager.DEFAULT_TIMEOUT
    ):
        self.model = model
        self.timeout = timeout
        self._register_signals()
    
    def _register_signals(self):
        """Register signal handlers for automatic invalidation."""
        @receiver(post_save, sender=self.model)
        def on_save(sender, instance, **kwargs):
            self.invalidate(instance.pk)
        
        @receiver(post_delete, sender=self.model)
        def on_delete(sender, instance, **kwargs):
            self.invalidate(instance.pk)
    
    def get(self, pk: Any) -> Optional[Model]:
        """Get a cached model instance."""
        key = CacheKey.for_model(self.model, pk)
        
        def factory():
            try:
                return self.model.objects.get(pk=pk)
            except self.model.DoesNotExist:
                return None
        
        return CacheManager.get_or_set(key, factory, self.timeout)
    
    def get_list(
        self,
        filters: dict = None,
        order_by: str = None,
        limit: int = None
    ) -> List[Model]:
        """Get a cached list of model instances."""
        key_parts = [CacheKey.for_model(self.model), 'list']
        if filters:
            key_parts.append(CacheKey.hash_query('', filters))
        if order_by:
            key_parts.append(f'order_{order_by}')
        if limit:
            key_parts.append(f'limit_{limit}')
        
        key = ':'.join(key_parts)
        
        def factory():
            qs = self.model.objects.all()
            if filters:
                qs = qs.filter(**filters)
            if order_by:
                qs = qs.order_by(order_by)
            if limit:
                qs = qs[:limit]
            return list(qs)
        
        return CacheManager.get_or_set(key, factory, self.timeout)
    
    def invalidate(self, pk: Any = None) -> None:
        """Invalidate cache for instance or all."""
        CacheManager.invalidate_model(self.model, pk)
    
    def warm(self, pks: List[Any]) -> None:
        """Warm the cache with specific instances."""
        for pk in pks:
            self.get(pk)


class RateLimitCache:
    """
    Rate limiting using cache backend.
    """
    
    def __init__(self, key_prefix: str, limit: int, window: int):
        self.key_prefix = key_prefix
        self.limit = limit
        self.window = window  # seconds
    
    def is_allowed(self, identifier: str) -> tuple[bool, int]:
        """
        Check if request is allowed.
        Returns (is_allowed, remaining_requests).
        """
        key = CacheKey.make(self.key_prefix, 'ratelimit', identifier)
        current = cache.get(key, 0)
        
        if current >= self.limit:
            return False, 0
        
        # Increment counter
        new_count = CacheManager.increment(key, 1, self.window)
        remaining = max(0, self.limit - new_count)
        
        return True, remaining
    
    def reset(self, identifier: str) -> None:
        """Reset rate limit for an identifier."""
        key = CacheKey.make(self.key_prefix, 'ratelimit', identifier)
        cache.delete(key)


# Pre-configured caches for common models
def create_model_cache(model: Type[Model], timeout: int = 300) -> QueryResultCache:
    """Create a query result cache for a model."""
    return QueryResultCache(model, timeout)


# Example usage:
# lead_cache = create_model_cache(Lead)
# contact_cache = create_model_cache(Contact)
# opportunity_cache = create_model_cache(Opportunity)
