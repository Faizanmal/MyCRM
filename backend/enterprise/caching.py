"""
Enterprise Caching Layer for MyCRM
==================================

Advanced caching implementation with:
- Redis Cluster support
- Multi-tier caching (L1 in-memory, L2 Redis)
- Cache stampede prevention
- Automatic cache invalidation
- Cache analytics and monitoring
- Compression for large values
- Circuit breaker pattern

Author: MyCRM Enterprise Team
Version: 1.0.0
"""

import asyncio
import hashlib
import json
import logging
import pickle
import random
import threading
import time
import zlib
from abc import ABC, abstractmethod
from collections import OrderedDict
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar, Union

import redis
from redis.cluster import RedisCluster
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheStatus(Enum):
    """Cache operation status."""
    HIT = "hit"
    MISS = "miss"
    ERROR = "error"
    STALE = "stale"
    EXPIRED = "expired"


@dataclass
class CacheEntry(Generic[T]):
    """Represents a cache entry with metadata."""
    value: T
    created_at: float
    expires_at: Optional[float] = None
    version: int = 1
    tags: Set[str] = field(default_factory=set)
    access_count: int = 0
    last_accessed: Optional[float] = None
    compressed: bool = False
    size_bytes: int = 0


@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    errors: int = 0
    evictions: int = 0
    total_requests: int = 0
    avg_response_time_ms: float = 0.0
    cache_size_bytes: int = 0
    keys_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100


class CacheBackend(ABC):
    """Abstract cache backend interface."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass


class InMemoryCache(CacheBackend):
    """
    LRU-based in-memory cache (L1).
    Thread-safe with TTL support.
    """
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()
        self._response_times: List[float] = []
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from in-memory cache."""
        start_time = time.time()
        
        with self._lock:
            self._stats.total_requests += 1
            
            if key not in self._cache:
                self._stats.misses += 1
                self._record_response_time(start_time)
                return None
            
            entry = self._cache[key]
            
            # Check expiration
            if entry.expires_at and time.time() > entry.expires_at:
                del self._cache[key]
                self._stats.misses += 1
                self._record_response_time(start_time)
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(key)
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            self._stats.hits += 1
            self._record_response_time(start_time)
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in in-memory cache."""
        with self._lock:
            # Evict if at capacity
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
                self._stats.evictions += 1
            
            expires_at = None
            if ttl is not None:
                expires_at = time.time() + ttl
            elif self.default_ttl:
                expires_at = time.time() + self.default_ttl
            
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                expires_at=expires_at,
                size_bytes=len(pickle.dumps(value))
            )
            
            self._cache[key] = entry
            return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        with self._lock:
            if key not in self._cache:
                return False
            entry = self._cache[key]
            if entry.expires_at and time.time() > entry.expires_at:
                del self._cache[key]
                return False
            return True
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            return True
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            self._stats.keys_count = len(self._cache)
            self._stats.cache_size_bytes = sum(
                entry.size_bytes for entry in self._cache.values()
            )
            return self._stats
    
    def _record_response_time(self, start_time: float):
        """Record response time for metrics."""
        elapsed = (time.time() - start_time) * 1000
        self._response_times.append(elapsed)
        if len(self._response_times) > 1000:
            self._response_times = self._response_times[-1000:]
        self._stats.avg_response_time_ms = sum(self._response_times) / len(self._response_times)


class RedisCache(CacheBackend):
    """
    Redis-based cache backend (L2).
    Supports both standalone and cluster mode.
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        cluster_mode: bool = False,
        cluster_nodes: Optional[List[Dict]] = None,
        prefix: str = 'mycrm:cache:',
        default_ttl: int = 3600,
        compression_threshold: int = 1024,
        socket_timeout: float = 5.0,
        retry_on_timeout: bool = True
    ):
        self.prefix = prefix
        self.default_ttl = default_ttl
        self.compression_threshold = compression_threshold
        self._stats = CacheStats()
        self._response_times: List[float] = []
        
        # Initialize Redis connection
        if cluster_mode and cluster_nodes:
            self.client = RedisCluster(
                startup_nodes=cluster_nodes,
                password=password,
                decode_responses=False,
                socket_timeout=socket_timeout,
                retry_on_timeout=retry_on_timeout
            )
        else:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False,
                socket_timeout=socket_timeout,
                retry_on_timeout=retry_on_timeout
            )
    
    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        return f"{self.prefix}{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value with optional compression."""
        data = pickle.dumps(value)
        
        if len(data) > self.compression_threshold:
            compressed = zlib.compress(data)
            # Only use compression if it actually reduces size
            if len(compressed) < len(data):
                return b'C' + compressed
        
        return b'U' + data
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value with decompression support."""
        if not data:
            return None
        
        flag = data[0:1]
        payload = data[1:]
        
        if flag == b'C':
            payload = zlib.decompress(payload)
        
        return pickle.loads(payload)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        start_time = time.time()
        
        try:
            self._stats.total_requests += 1
            redis_key = self._make_key(key)
            
            data = self.client.get(redis_key)
            
            if data is None:
                self._stats.misses += 1
                self._record_response_time(start_time)
                return None
            
            value = self._deserialize(data)
            self._stats.hits += 1
            self._record_response_time(start_time)
            
            return value
            
        except RedisError as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            self._stats.errors += 1
            self._record_response_time(start_time)
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        try:
            redis_key = self._make_key(key)
            data = self._serialize(value)
            
            if ttl is None:
                ttl = self.default_ttl
            
            if ttl > 0:
                self.client.setex(redis_key, ttl, data)
            else:
                self.client.set(redis_key, data)
            
            return True
            
        except RedisError as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            self._stats.errors += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        try:
            redis_key = self._make_key(key)
            return self.client.delete(redis_key) > 0
        except RedisError as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            redis_pattern = self._make_key(pattern)
            keys = list(self.client.scan_iter(match=redis_pattern))
            
            if keys:
                return self.client.delete(*keys)
            return 0
            
        except RedisError as e:
            logger.error(f"Redis DELETE pattern error: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            redis_key = self._make_key(key)
            return self.client.exists(redis_key) > 0
        except RedisError as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries with prefix."""
        try:
            return self.delete_pattern('*') >= 0
        except RedisError as e:
            logger.error(f"Redis CLEAR error: {e}")
            return False
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        try:
            info = self.client.info()
            self._stats.keys_count = info.get('db0', {}).get('keys', 0)
            self._stats.cache_size_bytes = info.get('used_memory', 0)
        except RedisError:
            pass
        return self._stats
    
    def _record_response_time(self, start_time: float):
        """Record response time for metrics."""
        elapsed = (time.time() - start_time) * 1000
        self._response_times.append(elapsed)
        if len(self._response_times) > 1000:
            self._response_times = self._response_times[-1000:]
        self._stats.avg_response_time_ms = sum(self._response_times) / len(self._response_times)


class MultiTierCache:
    """
    Multi-tier caching with L1 (memory) and L2 (Redis).
    Implements cache-aside pattern with automatic promotion.
    """
    
    def __init__(
        self,
        l1_cache: Optional[InMemoryCache] = None,
        l2_cache: Optional[RedisCache] = None,
        l1_ttl: int = 60,
        l2_ttl: int = 3600
    ):
        self.l1 = l1_cache or InMemoryCache(default_ttl=l1_ttl)
        self.l2 = l2_cache
        self.l1_ttl = l1_ttl
        self.l2_ttl = l2_ttl
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get from L1, then L2, promoting to L1 on L2 hit.
        """
        # Try L1 first
        value = self.l1.get(key)
        if value is not None:
            return value
        
        # Try L2 if available
        if self.l2:
            value = self.l2.get(key)
            if value is not None:
                # Promote to L1
                self.l1.set(key, value, self.l1_ttl)
                return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set in both L1 and L2.
        """
        l1_ttl = min(ttl or self.l1_ttl, self.l1_ttl)
        l2_ttl = ttl or self.l2_ttl
        
        # Set in L1
        l1_success = self.l1.set(key, value, l1_ttl)
        
        # Set in L2 if available
        l2_success = True
        if self.l2:
            l2_success = self.l2.set(key, value, l2_ttl)
        
        return l1_success and l2_success
    
    def delete(self, key: str) -> bool:
        """Delete from both tiers."""
        l1_success = self.l1.delete(key)
        l2_success = True
        if self.l2:
            l2_success = self.l2.delete(key)
        return l1_success or l2_success
    
    def invalidate_by_tags(self, tags: Set[str]) -> int:
        """Invalidate all entries with given tags."""
        count = 0
        # This requires tag tracking - implement via Redis sets
        if self.l2:
            for tag in tags:
                pattern = f"tag:{tag}:*"
                count += self.l2.delete_pattern(pattern)
        return count
    
    def get_stats(self) -> Dict[str, CacheStats]:
        """Get statistics for all tiers."""
        stats = {'l1': self.l1.get_stats()}
        if self.l2:
            stats['l2'] = self.l2.get_stats()
        return stats


class CacheStampedeProtection:
    """
    Prevents cache stampede using probabilistic early recomputation
    and distributed locking.
    """
    
    def __init__(
        self,
        cache: Union[RedisCache, MultiTierCache],
        lock_timeout: int = 30,
        beta: float = 1.0
    ):
        self.cache = cache
        self.lock_timeout = lock_timeout
        self.beta = beta  # XFetch algorithm parameter
        self._locks: Dict[str, threading.Lock] = {}
    
    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], T],
        ttl: int = 3600,
        recompute_window: int = 60
    ) -> T:
        """
        Get value from cache or compute with stampede protection.
        
        Uses XFetch algorithm for probabilistic early recomputation.
        """
        # Try to get from cache with metadata
        cached_data = self._get_with_metadata(key)
        
        if cached_data:
            value, created_at, expires_at = cached_data
            
            # XFetch: Probabilistic early recomputation
            if expires_at:
                time_left = expires_at - time.time()
                delta = self.beta * recompute_window * random.random()
                
                # Early recompute if within window
                if time_left < delta:
                    # Try to acquire lock for recomputation
                    if self._try_acquire_lock(key):
                        try:
                            new_value = compute_fn()
                            self._set_with_metadata(key, new_value, ttl)
                            return new_value
                        finally:
                            self._release_lock(key)
            
            return value
        
        # Cache miss - compute with lock
        with self._get_lock(key):
            # Double-check after acquiring lock
            cached_data = self._get_with_metadata(key)
            if cached_data:
                return cached_data[0]
            
            # Compute and cache
            value = compute_fn()
            self._set_with_metadata(key, value, ttl)
            return value
    
    def _get_with_metadata(self, key: str) -> Optional[tuple]:
        """Get value with creation and expiration metadata."""
        meta_key = f"{key}:meta"
        
        if isinstance(self.cache, MultiTierCache):
            value = self.cache.get(key)
            meta = self.cache.get(meta_key)
        else:
            value = self.cache.get(key)
            meta = self.cache.get(meta_key)
        
        if value is not None and meta:
            return (value, meta.get('created_at'), meta.get('expires_at'))
        
        return None
    
    def _set_with_metadata(self, key: str, value: Any, ttl: int):
        """Set value with metadata."""
        meta_key = f"{key}:meta"
        now = time.time()
        meta = {
            'created_at': now,
            'expires_at': now + ttl
        }
        
        if isinstance(self.cache, MultiTierCache):
            self.cache.set(key, value, ttl)
            self.cache.set(meta_key, meta, ttl)
        else:
            self.cache.set(key, value, ttl)
            self.cache.set(meta_key, meta, ttl)
    
    def _get_lock(self, key: str) -> threading.Lock:
        """Get or create lock for key."""
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        return self._locks[key]
    
    def _try_acquire_lock(self, key: str) -> bool:
        """Try to acquire lock without blocking."""
        lock = self._get_lock(key)
        return lock.acquire(blocking=False)
    
    def _release_lock(self, key: str):
        """Release lock for key."""
        if key in self._locks:
            try:
                self._locks[key].release()
            except RuntimeError:
                pass


class CircuitBreaker:
    """
    Circuit breaker for cache operations.
    Prevents cascade failures when cache is unavailable.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._state = 'closed'  # closed, open, half-open
        self._half_open_calls = 0
        self._lock = threading.Lock()
    
    @property
    def state(self) -> str:
        """Get current circuit state."""
        with self._lock:
            if self._state == 'open':
                if time.time() - self._last_failure_time > self.recovery_timeout:
                    self._state = 'half-open'
                    self._half_open_calls = 0
            return self._state
    
    def call(self, func: Callable[[], T], fallback: Optional[Callable[[], T]] = None) -> T:
        """Execute function with circuit breaker protection."""
        state = self.state
        
        if state == 'open':
            if fallback:
                return fallback()
            raise CircuitBreakerError("Circuit breaker is open")
        
        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            if fallback:
                return fallback()
            raise
    
    def _on_success(self):
        """Handle successful call."""
        with self._lock:
            if self._state == 'half-open':
                self._half_open_calls += 1
                if self._half_open_calls >= self.half_open_max_calls:
                    self._state = 'closed'
                    self._failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == 'half-open':
                self._state = 'open'
            elif self._failure_count >= self.failure_threshold:
                self._state = 'open'


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CacheManager:
    """
    High-level cache manager with enterprise features.
    """
    
    _instance: Optional['CacheManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        redis_cluster_nodes: Optional[List[Dict]] = None,
        l1_max_size: int = 10000,
        l1_ttl: int = 60,
        l2_ttl: int = 3600,
        enable_circuit_breaker: bool = True
    ):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # Initialize L1 cache
        self.l1_cache = InMemoryCache(max_size=l1_max_size, default_ttl=l1_ttl)
        
        # Initialize L2 cache (Redis)
        self.l2_cache = None
        if redis_url:
            # Parse Redis URL
            import urllib.parse
            parsed = urllib.parse.urlparse(redis_url)
            self.l2_cache = RedisCache(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                db=int(parsed.path.lstrip('/') or 0),
                password=parsed.password,
                default_ttl=l2_ttl
            )
        elif redis_cluster_nodes:
            self.l2_cache = RedisCache(
                cluster_mode=True,
                cluster_nodes=redis_cluster_nodes,
                default_ttl=l2_ttl
            )
        
        # Initialize multi-tier cache
        self.cache = MultiTierCache(
            l1_cache=self.l1_cache,
            l2_cache=self.l2_cache,
            l1_ttl=l1_ttl,
            l2_ttl=l2_ttl
        )
        
        # Initialize stampede protection
        self.stampede_protection = CacheStampedeProtection(self.cache)
        
        # Initialize circuit breaker
        self.circuit_breaker = None
        if enable_circuit_breaker:
            self.circuit_breaker = CircuitBreaker()
        
        # Metrics
        self._metrics_lock = threading.Lock()
        self._operation_count = 0
        self._start_time = time.time()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.circuit_breaker:
            return self.circuit_breaker.call(
                lambda: self.cache.get(key),
                fallback=lambda: None
            )
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if self.circuit_breaker:
            return self.circuit_breaker.call(
                lambda: self.cache.set(key, value, ttl),
                fallback=lambda: False
            )
        return self.cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        return self.cache.delete(key)
    
    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], T],
        ttl: int = 3600
    ) -> T:
        """Get from cache or compute with stampede protection."""
        return self.stampede_protection.get_or_compute(key, compute_fn, ttl)
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        count = 0
        if self.l2_cache:
            count = self.l2_cache.delete_pattern(pattern)
        return count
    
    def get_stats(self) -> Dict:
        """Get comprehensive cache statistics."""
        cache_stats = self.cache.get_stats()
        
        return {
            'tiers': {
                tier: {
                    'hits': stats.hits,
                    'misses': stats.misses,
                    'hit_rate': stats.hit_rate,
                    'errors': stats.errors,
                    'evictions': stats.evictions,
                    'keys_count': stats.keys_count,
                    'avg_response_time_ms': stats.avg_response_time_ms
                }
                for tier, stats in cache_stats.items()
            },
            'circuit_breaker': {
                'state': self.circuit_breaker.state if self.circuit_breaker else 'disabled'
            },
            'uptime_seconds': time.time() - self._start_time
        }


def cached(
    key_prefix: str,
    ttl: int = 3600,
    key_builder: Optional[Callable[..., str]] = None
):
    """
    Decorator for caching function results.
    
    Usage:
        @cached('user', ttl=300)
        def get_user(user_id: int) -> dict:
            return User.objects.get(id=user_id).to_dict()
    
        @cached('search', key_builder=lambda q, **kw: f"{q}:{kw.get('page', 1)}")
        def search(query: str, page: int = 1) -> list:
            return perform_search(query, page)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Build cache key
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                # Default key builder from args
                key_parts = [str(arg) for arg in args]
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                key_suffix = hashlib.md5(':'.join(key_parts).encode()).hexdigest()
            
            cache_key = f"{key_prefix}:{key_suffix}"
            
            # Get cache manager
            cache_manager = CacheManager()
            
            # Try to get from cache or compute
            return cache_manager.get_or_compute(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl=ttl
            )
        
        return wrapper
    return decorator


def cache_invalidate(patterns: List[str]):
    """
    Decorator to invalidate cache patterns after function execution.
    
    Usage:
        @cache_invalidate(['user:*', 'profile:*'])
        def update_user(user_id: int, data: dict):
            # Update user
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            result = func(*args, **kwargs)
            
            # Invalidate patterns
            cache_manager = CacheManager()
            for pattern in patterns:
                cache_manager.invalidate_by_pattern(pattern)
            
            return result
        
        return wrapper
    return decorator


# Django cache backend integration
class DjangoCacheBackend:
    """
    Django cache backend using enterprise caching layer.
    
    Add to settings.py:
        CACHES = {
            'default': {
                'BACKEND': 'enterprise.caching.DjangoCacheBackend',
                'OPTIONS': {
                    'REDIS_URL': 'redis://localhost:6379/0',
                    'L1_MAX_SIZE': 10000,
                    'L1_TTL': 60,
                    'L2_TTL': 3600,
                }
            }
        }
    """
    
    def __init__(self, server: str, params: Dict):
        self._cache = CacheManager(
            redis_url=params.get('REDIS_URL'),
            l1_max_size=params.get('L1_MAX_SIZE', 10000),
            l1_ttl=params.get('L1_TTL', 60),
            l2_ttl=params.get('L2_TTL', 3600)
        )
        self.key_prefix = params.get('KEY_PREFIX', '')
        self.default_timeout = params.get('TIMEOUT', 300)
    
    def make_key(self, key: str, version: Optional[int] = None) -> str:
        """Make cache key with prefix and version."""
        if version:
            return f"{self.key_prefix}:{version}:{key}"
        return f"{self.key_prefix}:{key}"
    
    def get(self, key: str, default=None, version=None):
        """Get value from cache."""
        cache_key = self.make_key(key, version)
        value = self._cache.get(cache_key)
        return value if value is not None else default
    
    def set(self, key: str, value: Any, timeout=None, version=None):
        """Set value in cache."""
        cache_key = self.make_key(key, version)
        ttl = timeout if timeout is not None else self.default_timeout
        self._cache.set(cache_key, value, ttl)
    
    def delete(self, key: str, version=None):
        """Delete key from cache."""
        cache_key = self.make_key(key, version)
        self._cache.delete(cache_key)
    
    def clear(self):
        """Clear all cache."""
        self._cache.invalidate_by_pattern(f"{self.key_prefix}:*")
    
    def get_many(self, keys: List[str], version=None) -> Dict:
        """Get multiple values."""
        return {key: self.get(key, version=version) for key in keys}
    
    def set_many(self, mapping: Dict, timeout=None, version=None):
        """Set multiple values."""
        for key, value in mapping.items():
            self.set(key, value, timeout, version)
    
    def delete_many(self, keys: List[str], version=None):
        """Delete multiple keys."""
        for key in keys:
            self.delete(key, version)


# Model caching mixin for Django
class CachedModelMixin:
    """
    Mixin for Django models to enable automatic caching.
    
    Usage:
        class User(CachedModelMixin, models.Model):
            CACHE_TTL = 300
            CACHE_KEY_PREFIX = 'user'
            
            name = models.CharField(max_length=100)
    """
    
    CACHE_TTL: int = 300
    CACHE_KEY_PREFIX: str = 'model'
    
    @classmethod
    def get_cache_key(cls, pk) -> str:
        """Get cache key for instance."""
        return f"{cls.CACHE_KEY_PREFIX}:{cls.__name__.lower()}:{pk}"
    
    @classmethod
    def get_cached(cls, pk):
        """Get cached instance or fetch from DB."""
        cache_manager = CacheManager()
        cache_key = cls.get_cache_key(pk)
        
        def fetch():
            return cls.objects.get(pk=pk)
        
        return cache_manager.get_or_compute(cache_key, fetch, cls.CACHE_TTL)
    
    def invalidate_cache(self):
        """Invalidate cache for this instance."""
        cache_manager = CacheManager()
        cache_key = self.get_cache_key(self.pk)
        cache_manager.delete(cache_key)
    
    def save(self, *args, **kwargs):
        """Save and invalidate cache."""
        super().save(*args, **kwargs)
        self.invalidate_cache()
    
    def delete(self, *args, **kwargs):
        """Delete and invalidate cache."""
        self.invalidate_cache()
        super().delete(*args, **kwargs)
