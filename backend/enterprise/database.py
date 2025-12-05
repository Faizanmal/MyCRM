"""
Enterprise Database Optimization for MyCRM
==========================================

Database optimization utilities including:
- Connection pooling with PgBouncer support
- Read replica routing
- Query optimization and analysis
- Table partitioning helpers
- Automated index recommendations
- Slow query detection and logging

Author: MyCRM Enterprise Team
Version: 1.0.0
"""

import hashlib
import logging
import re
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar

from django.conf import settings
from django.db import connection, connections, router
from django.db.models import QuerySet

logger = logging.getLogger(__name__)

T = TypeVar('T')


# =============================================================================
# Read Replica Router
# =============================================================================

class ReadReplicaRouter:
    """
    Database router for read/write splitting.
    
    Configure in settings.py:
        DATABASE_ROUTERS = ['enterprise.database.ReadReplicaRouter']
        
        DATABASES = {
            'default': {...},  # Primary (write)
            'replica1': {...},  # Read replica 1
            'replica2': {...},  # Read replica 2
        }
        
        READ_REPLICA_DATABASES = ['replica1', 'replica2']
    """
    
    def __init__(self):
        self._replica_index = 0
        self._lock = threading.Lock()
        self._replicas = getattr(settings, 'READ_REPLICA_DATABASES', [])
        self._lag_thresholds: Dict[str, float] = {}
    
    def db_for_read(self, model, **hints):
        """Route read queries to replicas with health-aware load balancing."""
        # Check if we should use primary (e.g., immediately after write)
        if hints.get('instance') and hints['instance']._state.db:
            return hints['instance']._state.db
        
        # Check for explicit primary hint
        if hints.get('use_primary'):
            return 'default'
        
        # Check if replicas are configured
        if not self._replicas:
            return 'default'
        
        # Health-aware replica selection
        healthy_replicas = self._get_healthy_replicas()
        if not healthy_replicas:
            logger.warning("No healthy replicas available, using primary")
            return 'default'
        
        # Round-robin with thread safety
        with self._lock:
            replica = healthy_replicas[self._replica_index % len(healthy_replicas)]
            self._replica_index += 1
        
        return replica
    
    def db_for_write(self, model, **hints):
        """Route write queries to primary."""
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between objects in same database group."""
        db_set = {'default'} | set(self._replicas)
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Only allow migrations on primary."""
        return db == 'default'
    
    def _get_healthy_replicas(self) -> List[str]:
        """Get list of healthy replicas based on lag."""
        healthy = []
        max_lag_seconds = getattr(settings, 'MAX_REPLICA_LAG_SECONDS', 5.0)
        
        for replica in self._replicas:
            lag = self._get_replica_lag(replica)
            if lag is not None and lag <= max_lag_seconds:
                healthy.append(replica)
            else:
                logger.warning(f"Replica {replica} unhealthy, lag: {lag}s")
        
        return healthy
    
    def _get_replica_lag(self, replica: str) -> Optional[float]:
        """Get replication lag for a replica in seconds."""
        try:
            with connections[replica].cursor() as cursor:
                # PostgreSQL-specific query for replication lag
                cursor.execute("""
                    SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
                    AS lag_seconds
                """)
                result = cursor.fetchone()
                return float(result[0]) if result and result[0] else 0.0
        except Exception as e:
            logger.error(f"Error checking replica lag for {replica}: {e}")
            return None


class ReplicaContext:
    """
    Context manager for controlling read replica usage.
    
    Usage:
        # Force primary for consistent reads after write
        with ReplicaContext(use_primary=True):
            user = User.objects.get(id=user_id)
        
        # Explicitly use replica
        with ReplicaContext(use_replica='replica1'):
            reports = Report.objects.all()
    """
    
    _local = threading.local()
    
    def __init__(self, use_primary: bool = False, use_replica: Optional[str] = None):
        self.use_primary = use_primary
        self.use_replica = use_replica
        self._previous_state = None
    
    def __enter__(self):
        self._previous_state = getattr(self._local, 'db_override', None)
        if self.use_primary:
            self._local.db_override = 'default'
        elif self.use_replica:
            self._local.db_override = self.use_replica
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._previous_state is not None:
            self._local.db_override = self._previous_state
        elif hasattr(self._local, 'db_override'):
            delattr(self._local, 'db_override')
        return False
    
    @classmethod
    def get_override(cls) -> Optional[str]:
        """Get current database override if set."""
        return getattr(cls._local, 'db_override', None)


def use_primary(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to force primary database for a function."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        with ReplicaContext(use_primary=True):
            return func(*args, **kwargs)
    return wrapper


# =============================================================================
# Connection Pool Manager
# =============================================================================

@dataclass
class PoolStats:
    """Connection pool statistics."""
    pool_size: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    waiting_requests: int = 0
    total_connections_created: int = 0
    total_connections_closed: int = 0
    avg_wait_time_ms: float = 0.0


class ConnectionPoolManager:
    """
    Manages database connection pooling with PgBouncer support.
    
    For optimal performance, configure PgBouncer in transaction mode:
        [pgbouncer]
        pool_mode = transaction
        max_client_conn = 1000
        default_pool_size = 20
        min_pool_size = 10
        reserve_pool_size = 5
    """
    
    _instance: Optional['ConnectionPoolManager'] = None
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
        self._stats: Dict[str, PoolStats] = {}
        self._health_check_interval = 30
        self._last_health_check: Dict[str, datetime] = {}
    
    def get_stats(self, alias: str = 'default') -> PoolStats:
        """Get connection pool statistics."""
        try:
            with connections[alias].cursor() as cursor:
                # PostgreSQL-specific: get connection stats
                cursor.execute("""
                    SELECT 
                        numbackends as active_connections,
                        (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as pool_size
                    FROM pg_stat_database 
                    WHERE datname = current_database()
                """)
                result = cursor.fetchone()
                
                if result:
                    return PoolStats(
                        pool_size=result[1] or 0,
                        active_connections=result[0] or 0,
                        idle_connections=(result[1] or 0) - (result[0] or 0)
                    )
        except Exception as e:
            logger.error(f"Error getting pool stats: {e}")
        
        return PoolStats()
    
    def health_check(self, alias: str = 'default') -> bool:
        """Perform health check on database connection."""
        try:
            with connections[alias].cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone()[0] == 1
        except Exception as e:
            logger.error(f"Database health check failed for {alias}: {e}")
            return False
    
    def optimize_connection_settings(self):
        """
        Suggest optimal connection pool settings based on workload.
        """
        stats = self.get_stats()
        recommendations = []
        
        # Calculate utilization
        if stats.pool_size > 0:
            utilization = stats.active_connections / stats.pool_size
            
            if utilization > 0.8:
                recommendations.append(
                    f"High utilization ({utilization:.1%}). Consider increasing pool_size."
                )
            elif utilization < 0.2:
                recommendations.append(
                    f"Low utilization ({utilization:.1%}). Consider decreasing pool_size to save resources."
                )
        
        return recommendations


# =============================================================================
# Query Analyzer
# =============================================================================

@dataclass
class QueryAnalysis:
    """Analysis result for a SQL query."""
    query: str
    execution_time_ms: float
    rows_examined: int
    rows_returned: int
    index_used: bool
    index_name: Optional[str]
    scan_type: str
    recommendations: List[str] = field(default_factory=list)
    explain_plan: Optional[str] = None


class QueryAnalyzer:
    """
    Analyzes SQL queries for optimization opportunities.
    """
    
    # Patterns that indicate potential issues
    PROBLEMATIC_PATTERNS = [
        (r'SELECT \*', 'Avoid SELECT *, specify needed columns'),
        (r'NOT IN', 'Consider using NOT EXISTS for better performance'),
        (r'OR\s+\w+\s*=', 'Multiple ORs may prevent index usage, consider UNION'),
        (r'LIKE\s+[\'"]%', 'Leading wildcard prevents index usage'),
        (r'!=|<>', 'Not-equal operators may prevent index usage'),
    ]
    
    def __init__(self, connection_alias: str = 'default'):
        self.alias = connection_alias
        self._slow_queries: List[QueryAnalysis] = []
        self._query_stats: Dict[str, Dict] = {}
    
    def analyze(self, query: str, params: tuple = None) -> QueryAnalysis:
        """Analyze a query and return optimization recommendations."""
        recommendations = []
        
        # Check for problematic patterns
        for pattern, recommendation in self.PROBLEMATIC_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                recommendations.append(recommendation)
        
        # Get EXPLAIN ANALYZE
        explain_result = self._explain_analyze(query, params)
        
        # Parse explain result
        analysis = QueryAnalysis(
            query=query,
            execution_time_ms=explain_result.get('execution_time', 0),
            rows_examined=explain_result.get('rows_examined', 0),
            rows_returned=explain_result.get('rows_returned', 0),
            index_used=explain_result.get('index_used', False),
            index_name=explain_result.get('index_name'),
            scan_type=explain_result.get('scan_type', 'unknown'),
            recommendations=recommendations,
            explain_plan=explain_result.get('plan')
        )
        
        # Additional recommendations based on analysis
        if not analysis.index_used and analysis.rows_examined > 1000:
            recommendations.append(
                f"Query examined {analysis.rows_examined} rows without index. "
                "Consider adding an index."
            )
        
        if analysis.rows_examined > analysis.rows_returned * 10:
            recommendations.append(
                f"Query examined {analysis.rows_examined} rows but only returned "
                f"{analysis.rows_returned}. Consider adding more specific filters."
            )
        
        return analysis
    
    def _explain_analyze(self, query: str, params: tuple = None) -> Dict:
        """Run EXPLAIN ANALYZE on query."""
        try:
            with connections[self.alias].cursor() as cursor:
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                cursor.execute(explain_query, params)
                result = cursor.fetchone()[0]
                
                if result and len(result) > 0:
                    plan = result[0]
                    return {
                        'execution_time': plan.get('Execution Time', 0),
                        'rows_examined': plan.get('Plan', {}).get('Actual Rows', 0),
                        'rows_returned': plan.get('Plan', {}).get('Actual Rows', 0),
                        'index_used': 'Index' in plan.get('Plan', {}).get('Node Type', ''),
                        'index_name': plan.get('Plan', {}).get('Index Name'),
                        'scan_type': plan.get('Plan', {}).get('Node Type', 'unknown'),
                        'plan': str(plan)
                    }
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
        
        return {}
    
    def suggest_indexes(self, table_name: str) -> List[str]:
        """Suggest indexes based on query patterns."""
        suggestions = []
        
        try:
            with connections[self.alias].cursor() as cursor:
                # Get columns frequently used in WHERE clauses
                cursor.execute("""
                    SELECT 
                        attname as column_name,
                        n_distinct,
                        correlation
                    FROM pg_stats
                    WHERE tablename = %s
                    ORDER BY n_distinct DESC
                """, [table_name])
                
                columns = cursor.fetchall()
                
                # Get existing indexes
                cursor.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = %s
                """, [table_name])
                
                existing_indexes = {row[0]: row[1] for row in cursor.fetchall()}
                
                for col_name, n_distinct, correlation in columns:
                    # High cardinality columns are good index candidates
                    if n_distinct and abs(n_distinct) > 100:
                        index_name = f"idx_{table_name}_{col_name}"
                        if index_name not in existing_indexes:
                            suggestions.append(
                                f"CREATE INDEX {index_name} ON {table_name} ({col_name});"
                            )
                
        except Exception as e:
            logger.error(f"Error suggesting indexes: {e}")
        
        return suggestions


class SlowQueryLogger:
    """
    Logs slow queries for analysis.
    
    Configure in settings.py:
        SLOW_QUERY_THRESHOLD_MS = 100
        SLOW_QUERY_LOG_FILE = '/var/log/mycrm/slow_queries.log'
    """
    
    def __init__(
        self,
        threshold_ms: float = 100,
        log_file: Optional[str] = None
    ):
        self.threshold_ms = threshold_ms
        self.log_file = log_file
        self._queries: List[Dict] = []
        self._lock = threading.Lock()
    
    def log_query(
        self,
        query: str,
        duration_ms: float,
        params: Optional[tuple] = None,
        stack_trace: Optional[str] = None
    ):
        """Log a query if it exceeds threshold."""
        if duration_ms >= self.threshold_ms:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'duration_ms': duration_ms,
                'params': str(params) if params else None,
                'stack_trace': stack_trace
            }
            
            with self._lock:
                self._queries.append(entry)
                
                # Keep only last 1000 queries in memory
                if len(self._queries) > 1000:
                    self._queries = self._queries[-1000:]
            
            # Log to file if configured
            if self.log_file:
                self._write_to_file(entry)
            
            logger.warning(
                f"Slow query detected ({duration_ms:.2f}ms): {query[:200]}..."
            )
    
    def _write_to_file(self, entry: Dict):
        """Write slow query to log file."""
        try:
            import json
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing to slow query log: {e}")
    
    def get_slow_queries(
        self,
        limit: int = 100,
        min_duration_ms: Optional[float] = None
    ) -> List[Dict]:
        """Get recent slow queries."""
        with self._lock:
            queries = self._queries.copy()
        
        if min_duration_ms:
            queries = [q for q in queries if q['duration_ms'] >= min_duration_ms]
        
        return sorted(queries, key=lambda x: -x['duration_ms'])[:limit]
    
    def get_query_stats(self) -> Dict:
        """Get slow query statistics."""
        with self._lock:
            if not self._queries:
                return {'count': 0}
            
            durations = [q['duration_ms'] for q in self._queries]
            
            return {
                'count': len(self._queries),
                'avg_duration_ms': sum(durations) / len(durations),
                'max_duration_ms': max(durations),
                'min_duration_ms': min(durations),
                'total_time_ms': sum(durations)
            }


# =============================================================================
# Table Partitioning Helper
# =============================================================================

class PartitionType(Enum):
    """Partition types."""
    RANGE = "RANGE"
    LIST = "LIST"
    HASH = "HASH"


@dataclass
class PartitionConfig:
    """Configuration for table partitioning."""
    table_name: str
    partition_column: str
    partition_type: PartitionType
    partition_interval: Optional[str] = None  # For range: 'month', 'year', 'day'
    partition_count: Optional[int] = None  # For hash partitioning
    retention_days: Optional[int] = None  # Auto-drop old partitions


class PartitionManager:
    """
    Manages PostgreSQL table partitioning.
    
    Usage:
        manager = PartitionManager()
        
        # Create partitioned table
        manager.create_partitioned_table(
            PartitionConfig(
                table_name='activity_log',
                partition_column='created_at',
                partition_type=PartitionType.RANGE,
                partition_interval='month',
                retention_days=365
            )
        )
        
        # Maintain partitions
        manager.maintain_partitions('activity_log')
    """
    
    def __init__(self, connection_alias: str = 'default'):
        self.alias = connection_alias
    
    def create_partitioned_table(
        self,
        config: PartitionConfig,
        columns: List[str],
        primary_key: Optional[str] = None
    ) -> bool:
        """Create a partitioned table."""
        try:
            with connections[self.alias].cursor() as cursor:
                # Build column definitions
                cols_sql = ', '.join(columns)
                
                # Build partition clause
                partition_clause = f"PARTITION BY {config.partition_type.value} ({config.partition_column})"
                
                # Add primary key if specified (must include partition column)
                pk_clause = ""
                if primary_key:
                    pk_clause = f", PRIMARY KEY ({primary_key}, {config.partition_column})"
                
                sql = f"""
                    CREATE TABLE IF NOT EXISTS {config.table_name} (
                        {cols_sql}
                        {pk_clause}
                    ) {partition_clause}
                """
                
                cursor.execute(sql)
                logger.info(f"Created partitioned table: {config.table_name}")
                
                # Create initial partitions
                if config.partition_type == PartitionType.RANGE:
                    self._create_range_partitions(cursor, config)
                elif config.partition_type == PartitionType.HASH:
                    self._create_hash_partitions(cursor, config)
                
                return True
                
        except Exception as e:
            logger.error(f"Error creating partitioned table: {e}")
            return False
    
    def _create_range_partitions(self, cursor, config: PartitionConfig):
        """Create range partitions based on interval."""
        from dateutil.relativedelta import relativedelta
        
        now = datetime.now()
        
        if config.partition_interval == 'month':
            delta = relativedelta(months=1)
            format_str = '%Y_%m'
        elif config.partition_interval == 'year':
            delta = relativedelta(years=1)
            format_str = '%Y'
        else:  # day
            delta = timedelta(days=1)
            format_str = '%Y_%m_%d'
        
        # Create partitions for past and future
        start = now - (delta * 3 if hasattr(delta, '__mul__') else relativedelta(months=3))
        end = now + (delta * 3 if hasattr(delta, '__mul__') else relativedelta(months=3))
        
        current = start
        while current < end:
            next_period = current + delta
            partition_name = f"{config.table_name}_{current.strftime(format_str)}"
            
            sql = f"""
                CREATE TABLE IF NOT EXISTS {partition_name}
                PARTITION OF {config.table_name}
                FOR VALUES FROM ('{current.strftime('%Y-%m-%d')}') 
                TO ('{next_period.strftime('%Y-%m-%d')}')
            """
            
            try:
                cursor.execute(sql)
                logger.info(f"Created partition: {partition_name}")
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    logger.error(f"Error creating partition {partition_name}: {e}")
            
            current = next_period
    
    def _create_hash_partitions(self, cursor, config: PartitionConfig):
        """Create hash partitions."""
        count = config.partition_count or 4
        
        for i in range(count):
            partition_name = f"{config.table_name}_p{i}"
            
            sql = f"""
                CREATE TABLE IF NOT EXISTS {partition_name}
                PARTITION OF {config.table_name}
                FOR VALUES WITH (MODULUS {count}, REMAINDER {i})
            """
            
            try:
                cursor.execute(sql)
                logger.info(f"Created hash partition: {partition_name}")
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    logger.error(f"Error creating partition {partition_name}: {e}")
    
    def maintain_partitions(self, table_name: str):
        """
        Maintain partitions - create future ones, drop old ones.
        Should be run periodically via cron/celery.
        """
        try:
            with connections[self.alias].cursor() as cursor:
                # Get partition info
                cursor.execute("""
                    SELECT 
                        child.relname as partition_name,
                        pg_get_expr(child.relpartbound, child.oid) as partition_range
                    FROM pg_inherits
                    JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
                    JOIN pg_class child ON pg_inherits.inhrelid = child.oid
                    WHERE parent.relname = %s
                    ORDER BY child.relname
                """, [table_name])
                
                partitions = cursor.fetchall()
                logger.info(f"Found {len(partitions)} partitions for {table_name}")
                
                # Logic to create new partitions and drop old ones would go here
                
        except Exception as e:
            logger.error(f"Error maintaining partitions for {table_name}: {e}")
    
    def drop_old_partitions(
        self,
        table_name: str,
        retention_days: int
    ) -> int:
        """Drop partitions older than retention period."""
        dropped = 0
        cutoff = datetime.now() - timedelta(days=retention_days)
        
        try:
            with connections[self.alias].cursor() as cursor:
                # Find old partitions
                cursor.execute("""
                    SELECT child.relname as partition_name
                    FROM pg_inherits
                    JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
                    JOIN pg_class child ON pg_inherits.inhrelid = child.oid
                    WHERE parent.relname = %s
                """, [table_name])
                
                for (partition_name,) in cursor.fetchall():
                    # Extract date from partition name
                    # Assumes format: table_YYYY_MM or table_YYYY_MM_DD
                    try:
                        date_part = partition_name.replace(f"{table_name}_", "")
                        if len(date_part) == 7:  # YYYY_MM
                            partition_date = datetime.strptime(date_part, "%Y_%m")
                        elif len(date_part) == 10:  # YYYY_MM_DD
                            partition_date = datetime.strptime(date_part, "%Y_%m_%d")
                        else:
                            continue
                        
                        if partition_date < cutoff:
                            cursor.execute(f"DROP TABLE IF EXISTS {partition_name}")
                            logger.info(f"Dropped old partition: {partition_name}")
                            dropped += 1
                            
                    except ValueError:
                        continue
                
        except Exception as e:
            logger.error(f"Error dropping old partitions: {e}")
        
        return dropped


# =============================================================================
# Query Decorator and Context Manager
# =============================================================================

def log_slow_queries(threshold_ms: float = 100):
    """Decorator to log slow database queries."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration_ms = (time.time() - start_time) * 1000
                if duration_ms >= threshold_ms:
                    logger.warning(
                        f"Slow function {func.__name__} took {duration_ms:.2f}ms"
                    )
        return wrapper
    return decorator


@contextmanager
def query_timer(name: str = "query"):
    """Context manager for timing database operations."""
    start_time = time.time()
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"{name} completed in {duration_ms:.2f}ms")


class QueryOptimizer:
    """
    Provides query optimization utilities.
    """
    
    @staticmethod
    def prefetch_related_for_serializer(queryset: QuerySet, serializer_class) -> QuerySet:
        """
        Automatically add prefetch_related based on serializer fields.
        Analyzes serializer to determine related fields to prefetch.
        """
        prefetch_fields = []
        select_fields = []
        
        # Analyze serializer fields
        if hasattr(serializer_class, 'Meta') and hasattr(serializer_class.Meta, 'model'):
            model = serializer_class.Meta.model
            
            for field_name, field in serializer_class().fields.items():
                # Check if it's a relation field
                if hasattr(model, field_name):
                    model_field = getattr(model, field_name, None)
                    if model_field and hasattr(model_field, 'field'):
                        related = getattr(model_field.field, 'related_model', None)
                        if related:
                            # Determine if FK or M2M
                            if hasattr(model_field, 'is_cached'):
                                select_fields.append(field_name)
                            else:
                                prefetch_fields.append(field_name)
        
        if select_fields:
            queryset = queryset.select_related(*select_fields)
        if prefetch_fields:
            queryset = queryset.prefetch_related(*prefetch_fields)
        
        return queryset
    
    @staticmethod
    def chunk_queryset(queryset: QuerySet, chunk_size: int = 1000):
        """
        Iterate over queryset in chunks to avoid memory issues.
        
        Usage:
            for chunk in QueryOptimizer.chunk_queryset(MyModel.objects.all()):
                process(chunk)
        """
        start = 0
        while True:
            chunk = list(queryset[start:start + chunk_size])
            if not chunk:
                break
            yield chunk
            start += chunk_size


# =============================================================================
# Database Health Monitor
# =============================================================================

class DatabaseHealthMonitor:
    """
    Monitors database health and performance.
    """
    
    def __init__(self, connection_alias: str = 'default'):
        self.alias = connection_alias
    
    def get_health_report(self) -> Dict:
        """Generate comprehensive database health report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'connection': self._check_connection(),
            'performance': self._get_performance_metrics(),
            'storage': self._get_storage_metrics(),
            'locks': self._get_lock_info(),
            'replication': self._get_replication_status(),
            'recommendations': []
        }
        
        # Add recommendations based on metrics
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _check_connection(self) -> Dict:
        """Check database connection health."""
        try:
            start = time.time()
            with connections[self.alias].cursor() as cursor:
                cursor.execute("SELECT 1")
            latency_ms = (time.time() - start) * 1000
            
            return {
                'status': 'healthy',
                'latency_ms': latency_ms
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _get_performance_metrics(self) -> Dict:
        """Get database performance metrics."""
        try:
            with connections[self.alias].cursor() as cursor:
                # Cache hit ratio
                cursor.execute("""
                    SELECT 
                        sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) as cache_hit_ratio
                    FROM pg_statio_user_tables
                """)
                cache_hit_ratio = cursor.fetchone()[0] or 0
                
                # Transaction stats
                cursor.execute("""
                    SELECT 
                        xact_commit,
                        xact_rollback,
                        blks_read,
                        blks_hit,
                        temp_files,
                        temp_bytes
                    FROM pg_stat_database
                    WHERE datname = current_database()
                """)
                db_stats = cursor.fetchone()
                
                return {
                    'cache_hit_ratio': float(cache_hit_ratio),
                    'transactions_committed': db_stats[0] if db_stats else 0,
                    'transactions_rolled_back': db_stats[1] if db_stats else 0,
                    'blocks_read': db_stats[2] if db_stats else 0,
                    'blocks_hit': db_stats[3] if db_stats else 0,
                    'temp_files': db_stats[4] if db_stats else 0,
                    'temp_bytes': db_stats[5] if db_stats else 0
                }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def _get_storage_metrics(self) -> Dict:
        """Get storage usage metrics."""
        try:
            with connections[self.alias].cursor() as cursor:
                # Database size
                cursor.execute("""
                    SELECT pg_database_size(current_database())
                """)
                db_size = cursor.fetchone()[0]
                
                # Table sizes
                cursor.execute("""
                    SELECT 
                        relname as table_name,
                        pg_total_relation_size(relid) as total_size
                    FROM pg_catalog.pg_statio_user_tables
                    ORDER BY pg_total_relation_size(relid) DESC
                    LIMIT 10
                """)
                top_tables = [
                    {'table': row[0], 'size_bytes': row[1]}
                    for row in cursor.fetchall()
                ]
                
                return {
                    'database_size_bytes': db_size,
                    'database_size_human': self._human_size(db_size),
                    'top_tables': top_tables
                }
        except Exception as e:
            logger.error(f"Error getting storage metrics: {e}")
            return {}
    
    def _get_lock_info(self) -> Dict:
        """Get current lock information."""
        try:
            with connections[self.alias].cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        count(*) as total_locks,
                        count(*) filter (where granted = false) as waiting_locks
                    FROM pg_locks
                """)
                result = cursor.fetchone()
                
                return {
                    'total_locks': result[0] if result else 0,
                    'waiting_locks': result[1] if result else 0
                }
        except Exception as e:
            logger.error(f"Error getting lock info: {e}")
            return {}
    
    def _get_replication_status(self) -> Dict:
        """Get replication status for read replicas."""
        try:
            with connections[self.alias].cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        client_addr,
                        state,
                        sent_lsn,
                        write_lsn,
                        flush_lsn,
                        replay_lsn
                    FROM pg_stat_replication
                """)
                replicas = [
                    {
                        'address': str(row[0]),
                        'state': row[1],
                        'sent_lsn': str(row[2]),
                        'replay_lsn': str(row[5])
                    }
                    for row in cursor.fetchall()
                ]
                
                return {
                    'is_primary': len(replicas) > 0,
                    'replicas': replicas
                }
        except Exception as e:
            return {'is_primary': None, 'replicas': []}
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        perf = report.get('performance', {})
        if perf.get('cache_hit_ratio', 1) < 0.95:
            recommendations.append(
                f"Cache hit ratio is {perf['cache_hit_ratio']:.2%}. "
                "Consider increasing shared_buffers."
            )
        
        if perf.get('temp_files', 0) > 0:
            recommendations.append(
                f"Database created {perf['temp_files']} temp files. "
                "Consider increasing work_mem."
            )
        
        locks = report.get('locks', {})
        if locks.get('waiting_locks', 0) > 10:
            recommendations.append(
                f"High lock contention: {locks['waiting_locks']} waiting locks. "
                "Review long-running transactions."
            )
        
        return recommendations
    
    @staticmethod
    def _human_size(size_bytes: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(size_bytes) < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"
