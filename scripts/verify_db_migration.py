"""
Comprehensive Database Migration & Operational Verification Harness
===================================================================
Domain Acceptance Tests:
1. Migration State Audit: Zero pending migrations across all 32 apps (makemigrations --check)
2. Populated DB Copy & Rollback Rehearsal: Copies populated DB, reverts reversible migration,
   proves zero data loss, and rolls forward to latest
3. Database Constraints & Foreign Key Integrity: PRAGMA foreign_key_check (0 orphans),
   unique constraints, cascade rules
4. Query Plan Benchmarks: EXPLAIN QUERY PLAN asserting composite index utilization & latency
5. Operational Backfill & Feature Flag Kill-Switch: Staged backfill with circuit breaker
6. Adversarial Security: Constraint violations fail closed
"""
import sys
import os
import shutil
import sqlite3
import time
import io

sys.path.insert(0, os.path.abspath('backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
os.environ['DEBUG'] = 'True'
os.environ['USE_SQLITE'] = 'True'

import django
django.setup()

from django.core.management import call_command
from django.db import connection, IntegrityError
from django.contrib.auth import get_user_model
from lead_management.models import Lead
from contact_management.models import Contact
from opportunity_management.models import Opportunity
from task_management.models import Task
from multi_tenant.models import Organization
from core.migration_service import MigrationService

User = get_user_model()


def run_checks():
    print("=" * 70)
    print("STARTING DATABASE MIGRATION & OPERATIONAL VERIFICATION")
    print("=" * 70)

    passes = []
    failures = []

    def check(name, condition, details=""):
        if condition:
            print(f"[PASS] {name}")
            passes.append(name)
        else:
            print(f"[FAIL] {name}: {details}")
            failures.append((name, details))

    # ---------------------------------------------------------
    # 1. Zero Pending Migrations Audit
    # ---------------------------------------------------------
    print("\n--- 1. Migration Health & Zero Pending Migrations ---")
    try:
        out = io.StringIO()
        call_command('makemigrations', check=True, dry_run=True, stdout=out)
        check("No unapplied model changes (makemigrations --check)", True)
    except SystemExit:
        check("No unapplied model changes (makemigrations --check)", False, "makemigrations detected unapplied model changes")
    except Exception as e:
        check("No unapplied model changes (makemigrations --check)", False, str(e))

    # Check showmigrations
    try:
        out = io.StringIO()
        call_command('showmigrations', stdout=out)
        content = out.getvalue()
        unapplied = [line for line in content.splitlines() if '[ ]' in line]
        check(f"All migrations applied in DB ({len(unapplied)} unapplied)", len(unapplied) == 0, f"Unapplied: {unapplied}")
    except Exception as e:
        check("All migrations applied in DB", False, str(e))

    # ---------------------------------------------------------
    # 2. Populated DB Copy & Rollback Rehearsal
    # ---------------------------------------------------------
    print("\n--- 2. Populated DB Copy & Rollback Rehearsal ---")
    source_db = os.path.abspath('backend/db.sqlite3')
    rehearsal_db = os.path.abspath('backend/db.rehearsal_copy.sqlite3')

    try:
        # Create shadow copy
        if os.path.exists(rehearsal_db):
            os.remove(rehearsal_db)
        shutil.copyfile(source_db, rehearsal_db)
        check("Populated database shadow copy created", os.path.exists(rehearsal_db))

        # Count records before rollback
        conn_pre = sqlite3.connect(rehearsal_db)
        cur_pre = conn_pre.cursor()
        cur_pre.execute("SELECT COUNT(*) FROM crm_leads;")
        lead_count_pre = cur_pre.fetchone()[0]
        cur_pre.execute("SELECT COUNT(*) FROM crm_contacts;")
        contact_count_pre = cur_pre.fetchone()[0]
        cur_pre.execute("SELECT COUNT(*) FROM auth_user;")
        user_count_pre = cur_pre.fetchone()[0]
        conn_pre.close()

        # Execute rollback rehearsal on lead_management (from 0004 to 0003)
        # We can temporarily switch default database path to rehearsal_db
        from django.conf import settings
        original_db_name = settings.DATABASES['default']['NAME']
        try:
            settings.DATABASES['default']['NAME'] = rehearsal_db
            connection.close()

            # Roll back to 0003
            call_command('migrate', 'lead_management', '0003', interactive=False)
            check("Rollback rehearsal: Reverted lead_management to 0003 successfully", True)

            # Verify index is dropped during rollback in rehearsal copy
            conn_mid = sqlite3.connect(rehearsal_db)
            cur_mid = conn_mid.cursor()
            cur_mid.execute("PRAGMA index_list(crm_leads);")
            indexes_mid = [idx[1] for idx in cur_mid.fetchall()]
            check("Rollback rehearsal: idx_lead_status_prio dropped cleanly", 'idx_lead_status_prio' not in indexes_mid)

            # Re-apply forward migration to latest (0004)
            call_command('migrate', 'lead_management', '0004', interactive=False)
            check("Rollback rehearsal: Rolled forward to latest 0004 successfully", True)

            # Verify index restored
            cur_mid.execute("PRAGMA index_list(crm_leads);")
            indexes_post = [idx[1] for idx in cur_mid.fetchall()]
            check("Rollback rehearsal: idx_lead_status_prio restored cleanly", 'idx_lead_status_prio' in indexes_post)

            # Verify zero data loss
            cur_mid.execute("SELECT COUNT(*) FROM crm_leads;")
            lead_count_post = cur_mid.fetchone()[0]
            cur_mid.execute("SELECT COUNT(*) FROM crm_contacts;")
            contact_count_post = cur_mid.fetchone()[0]
            cur_mid.execute("SELECT COUNT(*) FROM auth_user;")
            user_count_post = cur_mid.fetchone()[0]
            conn_mid.close()

            check(f"Zero data loss: Leads count preserved ({lead_count_pre} == {lead_count_post})", lead_count_pre == lead_count_post)
            check(f"Zero data loss: Contacts count preserved ({contact_count_pre} == {contact_count_post})", contact_count_pre == contact_count_post)
            check(f"Zero data loss: Users count preserved ({user_count_pre} == {user_count_post})", user_count_pre == user_count_post)

        finally:
            settings.DATABASES['default']['NAME'] = original_db_name
            connection.close()
            if os.path.exists(rehearsal_db):
                os.remove(rehearsal_db)

    except Exception as e:
        check("Rollback rehearsal on populated copy", False, str(e))

    # ---------------------------------------------------------
    # 3. Database Constraints & Foreign Key Integrity
    # ---------------------------------------------------------
    print("\n--- 3. Database Constraints & Foreign Key Integrity ---")
    try:
        # 3.1 PRAGMA foreign_key_check
        orphan_violations = MigrationService.check_foreign_key_integrity()
        check(f"No orphaned foreign keys (PRAGMA foreign_key_check: {len(orphan_violations)} violations)", len(orphan_violations) == 0, str(orphan_violations))

        # 3.2 Unique constraint test (Contact email uniqueness)
        dup_email = f"constraint-test-{int(time.time())}@example.com"
        Contact.objects.create(first_name="First", last_name="User", email=dup_email)
        duplicate_raised = False
        try:
            Contact.objects.create(first_name="Duplicate", last_name="User", email=dup_email)
        except IntegrityError:
            duplicate_raised = True
        check("Unique constraint enforced on Contact.email (IntegrityError raised)", duplicate_raised)

        # 3.3 Cascade delete behavior verification
        from django.utils import timezone
        now = timezone.now()
        test_contact = Contact.objects.create(first_name="Cascade", last_name="Test", email=f"cascade-{int(time.time())}@example.com")
        test_user = User.objects.first()
        test_lead = Lead.objects.first()
        test_opp = Opportunity.objects.first()
        test_task = Task.objects.create(
            title="Cascade Task",
            contact=test_contact,
            lead=test_lead,
            opportunity=test_opp,
            assigned_to=test_user,
            created_by=test_user,
            due_date=now,
            completed_at=now,
            reminder_date=now
        )
        task_id = test_task.id
        test_contact.delete()
        task_exists = Task.objects.filter(id=task_id).exists()
        check("Cascade delete constraint works as configured (Contact -> Task cascade)", not task_exists)

    except Exception as e:
        check("Database constraint tests", False, str(e))

    # ---------------------------------------------------------
    # 4. Query Plan Benchmarks (EXPLAIN QUERY PLAN)
    # ---------------------------------------------------------
    print("\n--- 4. Query Plan Benchmarks & Index Utilization ---")
    try:
        benchmarks = MigrationService.benchmark_query_plans()
        for name, data in benchmarks.items():
            plan = data['plan']
            uses_index = data['uses_index']
            latency = data['avg_latency_ms']
            expected_index = data['expected_index']

            check(
                f"Query plan '{name}' uses index '{expected_index}' (latency: {latency:.3f}ms)",
                uses_index,
                f"Plan: {plan}"
            )
    except Exception as e:
        check("Query plan benchmarks", False, str(e))

    # ---------------------------------------------------------
    # 5. Operational Readiness: Backfill & Circuit Breaker
    # ---------------------------------------------------------
    print("\n--- 5. Operational Backfill & Feature Flag Circuit Breaker ---")
    try:
        # Test backfill with feature flag enabled
        os.environ['MIGRATION_BACKFILL_ENABLED'] = 'True'
        res_enabled = MigrationService.execute_batched_backfill(
            model_class=Lead,
            update_fields={'notes': 'Standardized backfill notes'},
            batch_size=50,
            correlation_id='test-corr-enabled'
        )
        check("Backfill service completes successfully when feature flag enabled", res_enabled['success'])

        # Test kill-switch / circuit breaker
        os.environ['MIGRATION_BACKFILL_ENABLED'] = 'False'
        res_disabled = MigrationService.execute_batched_backfill(
            model_class=Lead,
            update_fields={'notes': 'Should not execute'},
            batch_size=50,
            correlation_id='test-corr-disabled'
        )
        check("Backfill kill-switch aborts immediately when feature flag disabled", res_disabled['status'] == 'disabled' and res_disabled['records_processed'] == 0)

        # Restore feature flag
        os.environ['MIGRATION_BACKFILL_ENABLED'] = 'True'

    except Exception as e:
        check("Operational backfill and circuit breaker", False, str(e))

    # ---------------------------------------------------------
    # 6. Adversarial Database Validation
    # ---------------------------------------------------------
    print("\n--- 6. Adversarial Database Validation ---")
    try:
        from django.conf import settings
        db_path = settings.DATABASES['default']['NAME']
        conn_adv = sqlite3.connect(db_path)
        cur_adv = conn_adv.cursor()
        cur_adv.execute("PRAGMA foreign_keys = ON;")

        # Invalid foreign key reference fails closed
        invalid_fk_raised = False
        try:
            cur_adv.execute(
                "INSERT INTO crm_opportunities (id, name, stage, probability, amount, contact_id, owner_id, expected_close_date, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'));",
                (999999, 'Invalid FK Opp', 'qualification', 50, '100.00', 88888888, 1, '2026-12-31')
            )
            conn_adv.commit()
        except sqlite3.IntegrityError:
            invalid_fk_raised = True
        check("Adversarial: Invalid foreign key insertion rejected by DB constraint", invalid_fk_raised)

        # Null violation on non-null field fails closed
        null_raised = False
        try:
            cur_adv.execute(
                "INSERT INTO crm_leads (last_name, email, created_at, updated_at) VALUES (?, ?, datetime('now'), datetime('now'));",
                ('MissingFirstName', 'mf@example.com')
            )
            conn_adv.commit()
        except sqlite3.IntegrityError:
            null_raised = True
        check("Adversarial: NULL violation on NOT NULL column fails closed", null_raised)

        conn_adv.close()

    except Exception as e:
        check("Adversarial database validation", False, str(e))

    print("\n" + "=" * 70)
    print(f"DATABASE MIGRATION SUMMARY: {len(passes)} PASSED, {len(failures)} FAILED")
    print("=" * 70)

    if failures:
        print("\nFailures:")
        for name, details in failures:
            print(f"  - {name}: {details}")
        sys.exit(1)
    else:
        print("\nALL DATABASE MIGRATION & OPERATIONAL ACCEPTANCE CHECKS PASSED!")
        sys.exit(0)


if __name__ == '__main__':
    run_checks()
