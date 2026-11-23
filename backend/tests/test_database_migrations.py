"""
Comprehensive Database Migration & Constraint Tests
===================================================
Tests:
1. Migration completeness: zero unapplied models
2. Database constraints: unique, nullability, foreign keys
3. Query plan index utilization: EXPLAIN QUERY PLAN benchmarks
4. Operational backfill: circuit breaker / feature flag kill-switch
5. Adversarial input validation: constraint violation handling
"""
import os
import time
import io
from django.test import TestCase, TransactionTestCase
from django.db import connection, IntegrityError
from django.core.management import call_command
from django.contrib.auth import get_user_model

from lead_management.models import Lead
from contact_management.models import Contact
from opportunity_management.models import Opportunity
from task_management.models import Task
from core.migration_service import MigrationService

User = get_user_model()


class TestDatabaseMigrationHealth(TestCase):
    """Verifies that all migrations are synchronized and no drift exists"""

    def test_no_pending_migrations(self):
        """makemigrations --check --dry-run must report zero changes"""
        out = io.StringIO()
        call_command('makemigrations', check=True, dry_run=True, interactive=False, stdout=out)
        self.assertIn("No changes detected", out.getvalue())

    def test_all_migrations_applied(self):
        """showmigrations must have no unapplied migrations"""
        out = io.StringIO()
        call_command('showmigrations', stdout=out)
        content = out.getvalue()
        unapplied = [line for line in content.splitlines() if '[ ]' in line]
        self.assertEqual(len(unapplied), 0, f"Unapplied migrations found: {unapplied}")


class TestDatabaseConstraints(TransactionTestCase):
    """Tests schema constraints, uniqueness, cascade rules, and foreign keys"""

    def test_foreign_key_integrity(self):
        """PRAGMA foreign_key_check returns zero orphaned foreign keys"""
        orphans = MigrationService.check_foreign_key_integrity()
        self.assertEqual(len(orphans), 0, f"Found orphaned foreign keys: {orphans}")

    def test_unique_constraint_enforcement(self):
        """Duplicate emails on Contact violate unique constraint"""
        unique_email = f"unique-{int(time.time())}@example.com"
        Contact.objects.create(first_name="Alice", last_name="Unique", email=unique_email)
        with self.assertRaises(IntegrityError):
            Contact.objects.create(first_name="Bob", last_name="Unique", email=unique_email)

    def test_cascade_delete_integrity(self):
        """Deleting a Contact cascades cleanly to related Tasks"""
        from django.utils import timezone
        now = timezone.now()
        user, _ = User.objects.get_or_create(username="dbuser", defaults={"email": "dbuser@example.com"})
        contact = Contact.objects.create(first_name="Cascade", last_name="Parent", email=f"cascade-{int(time.time())}@example.com")
        lead, _ = Lead.objects.get_or_create(first_name="L", last_name="Parent", email=f"lead-{int(time.time())}@example.com", owner=user)
        opp, _ = Opportunity.objects.get_or_create(name="O", contact=contact, owner=user, stage="qualification", probability=50, expected_close_date="2026-12-31")
        task = Task.objects.create(title="Child Task", contact=contact, lead=lead, opportunity=opp, assigned_to=user, created_by=user, due_date=now, completed_at=now, reminder_date=now)
        task_id = task.id
        contact.delete()
        self.assertFalse(Task.objects.filter(id=task_id).exists())


class TestQueryPlanBenchmarks(TestCase):
    """Validates that critical filters utilize composite indexes"""

    def test_index_utilization_benchmarks(self):
        benchmarks = MigrationService.benchmark_query_plans()
        for name, data in benchmarks.items():
            self.assertTrue(data['uses_index'], f"Query {name} did not use expected index: {data['plan']}")
            self.assertLess(data['avg_latency_ms'], 10.0, f"Query {name} latency too high: {data['avg_latency_ms']}ms")


class TestOperationalBackfill(TestCase):
    """Validates expand/contract batched backfill and feature flag circuit breaker"""

    def test_backfill_feature_flag_kill_switch(self):
        os.environ['MIGRATION_BACKFILL_ENABLED'] = 'False'
        res = MigrationService.execute_batched_backfill(
            model_class=Lead,
            update_fields={'notes': 'Should be blocked'},
            batch_size=10
        )
        self.assertEqual(res['status'], 'disabled')
        self.assertEqual(res['records_processed'], 0)

        # Re-enable
        os.environ['MIGRATION_BACKFILL_ENABLED'] = 'True'
        res_enabled = MigrationService.execute_batched_backfill(
            model_class=Lead,
            update_fields={'notes': 'Backfilled notes'},
            batch_size=10
        )
        self.assertTrue(res_enabled['success'])


class TestAdversarialDatabaseValidation(TransactionTestCase):
    """Validates closed-failure on invalid inputs and constraint violations"""

    def test_invalid_foreign_key_rejected(self):
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = ON;")
            with self.assertRaises(IntegrityError):
                cursor.execute(
                    "INSERT INTO crm_opportunities (id, name, stage, probability, owner_id, created_at, updated_at) "
                    "VALUES ('99999999-9999-9999-9999-999999999999', 'Ghost Opp', 'new', 10, 9999999, datetime('now'), datetime('now'));"
                )

    def test_null_constraint_violation_rejected(self):
        with connection.cursor() as cursor:
            with self.assertRaises(IntegrityError):
                cursor.execute("INSERT INTO crm_leads (id, first_name) VALUES (99999, NULL);")
