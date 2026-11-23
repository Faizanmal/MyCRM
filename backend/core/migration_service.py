"""
Database Migration & Staged Backfill Service
============================================
Operational readiness service for database migrations, expand/contract schema evolution,
batch backfills, correlation tracking, feature flags, and foreign key integrity.
"""
import logging
import os
import time
import uuid
import sqlite3
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.db import connection, transaction

logger = logging.getLogger('core.migration')


class MigrationService:
    """
    Manages safe expand/contract migrations, batched backfills with circuit breakers,
    and foreign key integrity audits.
    """

    @classmethod
    def is_backfill_enabled(cls) -> bool:
        """Feature flag gate for background data backfills."""
        return os.getenv('MIGRATION_BACKFILL_ENABLED', 'True').lower() in ('true', '1', 'yes')

    @classmethod
    def execute_batched_backfill(
        cls,
        model_class,
        update_fields: Dict[str, Any],
        batch_size: int = 100,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes an expand/contract backfill in atomic batches with correlation tracking.
        Fails safely if feature flag is disabled.
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        logger.info(f"[{correlation_id}] Starting backfill for {model_class.__name__} with fields: {list(update_fields.keys())}")

        if not cls.is_backfill_enabled():
            logger.warning(f"[{correlation_id}] Backfill aborted: MIGRATION_BACKFILL_ENABLED is false.")
            return {
                'success': False,
                'status': 'disabled',
                'correlation_id': correlation_id,
                'records_processed': 0,
                'message': 'Migration backfill feature flag is disabled'
            }

        start_time = time.time()
        total_processed = 0

        try:
            # Find records requiring update
            filter_kwargs = {f"{k}__isnull": True for k in update_fields.keys()}
            queryset = model_class.objects.filter(**filter_kwargs)
            total_matching = queryset.count()

            while True:
                # Process in chunks to prevent long transaction locks
                batch_ids = list(queryset.values_list('id', flat=True)[:batch_size])
                if not batch_ids:
                    break

                with transaction.atomic():
                    updated = model_class.objects.filter(id__in=batch_ids).update(**update_fields)
                    total_processed += updated

                logger.debug(f"[{correlation_id}] Batch processed: {len(batch_ids)} rows.")

            duration = time.time() - start_time
            logger.info(f"[{correlation_id}] Backfill completed: {total_processed}/{total_matching} rows updated in {duration:.3f}s.")
            return {
                'success': True,
                'status': 'completed',
                'correlation_id': correlation_id,
                'records_processed': total_processed,
                'duration_seconds': duration,
            }

        except Exception as e:
            logger.error(f"[{correlation_id}] Backfill failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'status': 'error',
                'correlation_id': correlation_id,
                'records_processed': total_processed,
                'error': str(e),
            }

    @classmethod
    def check_foreign_key_integrity(cls) -> List[Dict[str, Any]]:
        """
        Runs SQLite PRAGMA foreign_key_check to detect any orphaned foreign keys.
        Returns a list of violations (empty list if database is clean).
        """
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_key_check;")
            violations = cursor.fetchall()

        results = []
        for v in violations:
            results.append({
                'table': v[0],
                'rowid': v[1],
                'referenced_table': v[2],
                'fkid': v[3],
            })
        return results

    @classmethod
    def benchmark_query_plans(cls) -> Dict[str, Any]:
        """
        Gathers EXPLAIN QUERY PLAN benchmarks across critical filter queries.
        Works across live database connections and pytest in-memory databases.
        """
        critical_queries = {
            'lead_status_priority': (
                "EXPLAIN QUERY PLAN SELECT * FROM crm_leads WHERE status = %s AND priority = %s;",
                ['new', 'high'],
                'idx_lead_status_prio'
            ),
            'opportunity_stage_assigned': (
                "EXPLAIN QUERY PLAN SELECT * FROM crm_opportunities WHERE stage = %s AND assigned_to_id = %s;",
                ['qualification', 1],
                'idx_opp_stage_assign'
            ),
            'task_status_priority': (
                "EXPLAIN QUERY PLAN SELECT * FROM crm_tasks WHERE status = %s AND priority = %s;",
                ['pending', 'high'],
                'idx_task_status_prio'
            ),
            'contact_email_search': (
                "EXPLAIN QUERY PLAN SELECT * FROM crm_contacts WHERE email = %s;",
                ['test@example.com'],
                'sqlite_autoindex_crm_contacts_1'
            ),
        }

        benchmarks = {}
        with connection.cursor() as cursor:
            for name, (sql, params, expected_index) in critical_queries.items():
                cursor.execute(sql, params)
                plan_rows = cursor.fetchall()
                plan_str = " -> ".join([r[3] for r in plan_rows if len(r) >= 4])
                uses_index = expected_index in plan_str or 'USING INDEX' in plan_str

                # Latency micro-benchmark
                exec_sql = sql.replace("EXPLAIN QUERY PLAN ", "")
                iterations = 50
                start = time.perf_counter()
                for _ in range(iterations):
                    cursor.execute(exec_sql, params)
                    cursor.fetchall()
                avg_ms = ((time.perf_counter() - start) / iterations) * 1000

                benchmarks[name] = {
                    'plan': plan_str,
                    'uses_index': uses_index,
                    'expected_index': expected_index,
                    'avg_latency_ms': round(avg_ms, 4)
                }

        return benchmarks
