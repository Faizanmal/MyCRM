"""
Verification Script for Product Positioning, ICP, JTBD, Buyer Tasks & Metrics
============================================================================
Validates:
1. Product positioning profile retrieval and updates
2. The 5 Real Buyer Tasks end-to-end execution lifecycle
3. Progress percentage calculations and status completion
4. Value metrics computation
5. Prioritized product spec endpoint (P0/P1/P2)
6. Multi-tenant boundary isolation (cross-tenant leak prevention)
7. RBAC role enforcement (admin/manager vs rep)
8. Adversarial validation (anonymous rejection, malformed payload)
9. Operational readiness: feature flag circuit breaker (PRODUCT_POSITIONING_ENABLED=False)
"""
import os
import sys
import uuid
import django

# Setup Django environment
sys.path.insert(0, os.path.abspath('backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
os.environ['CELERY_TASK_ALWAYS_EAGER'] = 'True'
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from multi_tenant.models import Organization, OrganizationMember, ProductPositioningProfile
from multi_tenant.positioning_views import ProductPositioningViewSet

User = get_user_model()
factory = APIRequestFactory()


def run_checks():
    print("=" * 70)
    print("STARTING PRODUCT POSITIONING & BUYER TASKS VERIFICATION")
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

    # Setup test tenants
    test_id = str(uuid.uuid4())[:8]
    org_a = Organization.objects.create(name=f"Acme Corp {test_id}", slug=f"acme-{test_id}")
    org_b = Organization.objects.create(name=f"Beta Ltd {test_id}", slug=f"beta-{test_id}")

    # Users
    admin_user = User.objects.create_user(
        username=f"admin_{test_id}",
        email=f"admin_{test_id}@example.com",
        password="password123"
    )
    admin_user.organization = org_a
    admin_user.save()
    OrganizationMember.objects.create(organization=org_a, user=admin_user, role="admin")

    rep_user = User.objects.create_user(
        username=f"rep_{test_id}",
        email=f"rep_{test_id}@example.com",
        password="password123"
    )
    rep_user.organization = org_a
    rep_user.save()
    OrganizationMember.objects.create(organization=org_a, user=rep_user, role="member")

    org_b_user = User.objects.create_user(
        username=f"user_b_{test_id}",
        email=f"user_b_{test_id}@example.com",
        password="password123"
    )
    org_b_user.organization = org_b
    org_b_user.save()
    OrganizationMember.objects.create(organization=org_b, user=org_b_user, role="admin")

    view = ProductPositioningViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })
    complete_task_view = ProductPositioningViewSet.as_view({
        'post': 'complete_task'
    })
    spec_view = ProductPositioningViewSet.as_view({
        'get': 'spec'
    })
    metrics_view = ProductPositioningViewSet.as_view({
        'get': 'metrics'
    })

    # ---------------------------------------------------------
    # 1. Product Positioning Profile Lifecycle
    # ---------------------------------------------------------
    print("\n--- 1. Product Positioning Profile Lifecycle ---")
    req = factory.get('/api/v1/product-position/')
    force_authenticate(req, user=admin_user)
    res = view(req)
    check("Profile retrieval returns 200 OK", res.status_code == 200, f"Got status {res.status_code}")
    check("Default target market is b2b_saas", res.data.get('target_market') == 'b2b_saas')
    check("Initial completion percentage is 0.0%", res.data.get('completion_percentage') == 0.0)
    check("All 5 buyer tasks present in schema", len(res.data.get('all_tasks', [])) == 5)

    # Update profile
    req_update = factory.post('/api/v1/product-position/', {
        'target_market': 'fintech',
        'ideal_customer_profile': 'enterprise',
        'team_size_tier': '51_200',
        'primary_jtbd': 'forecasting_accuracy'
    }, format='json')
    force_authenticate(req_update, user=admin_user)
    res_update = view(req_update)
    check("Profile update returns 200 OK", res_update.status_code == 200)
    check("Profile target_market updated to fintech", res_update.data.get('target_market') == 'fintech')
    check("Profile ICP updated to enterprise", res_update.data.get('ideal_customer_profile') == 'enterprise')

    # ---------------------------------------------------------
    # 2. Five Real Buyer Tasks End-to-End Progression
    # ---------------------------------------------------------
    print("\n--- 2. Five Real Buyer Tasks End-to-End Progression ---")
    tasks = ['eval_poc', 'data_migration', 'team_onboarding', 'pipeline_execution', 'roi_measurement']
    expected_pct = [20.0, 40.0, 60.0, 80.0, 100.0]

    for i, task_key in enumerate(tasks):
        req_task = factory.post('/api/v1/product-position/complete-task/', {'task_key': task_key}, format='json')
        force_authenticate(req_task, user=admin_user)
        res_task = complete_task_view(req_task)
        check(
            f"Buyer Task {i+1} ({task_key}) completed successfully",
            res_task.status_code == 200 and task_key in res_task.data.get('buyer_tasks_completed', [])
        )
        check(
            f"Buyer Task {i+1} completion percentage is {expected_pct[i]}%",
            res_task.data.get('completion_percentage') == expected_pct[i]
        )

    # Check that status became completed
    req_final = factory.get('/api/v1/product-position/')
    force_authenticate(req_final, user=admin_user)
    res_final = view(req_final)
    check("Onboarding status transitioned to 'completed'", res_final.data.get('onboarding_status') == 'completed')
    check("Completed timestamp recorded", res_final.data.get('completed_at') is not None)

    # ---------------------------------------------------------
    # 3. Value Metrics & Prioritized Product Spec Endpoints
    # ---------------------------------------------------------
    print("\n--- 3. Value Metrics & Prioritized Product Spec ---")
    req_metrics = factory.get('/api/v1/product-position/metrics/')
    force_authenticate(req_metrics, user=admin_user)
    res_metrics = metrics_view(req_metrics)
    check("Metrics endpoint returns 200 OK", res_metrics.status_code == 200)
    check("Metrics includes administrative time reduction (-42%)", res_metrics.data.get('administrative_time_reduction_pct') == 42.0)
    check("Metrics includes monthly hours saved", res_metrics.data.get('hours_saved_monthly') is not None)
    check("Metrics includes SLA uptime (99.95%)", res_metrics.data.get('tenant_sla_uptime_pct') == 99.95)

    req_spec = factory.get('/api/v1/product-position/spec/')
    force_authenticate(req_spec, user=admin_user)
    res_spec = spec_view(req_spec)
    check("Spec endpoint returns 200 OK", res_spec.status_code == 200)
    check("Spec includes strategic vision", 'AI-first' in res_spec.data.get('strategic_vision', ''))
    roadmap = res_spec.data.get('prioritized_roadmap', [])
    p0_items = [item for item in roadmap if item.get('priority') == 'P0']
    p1_items = [item for item in roadmap if item.get('priority') == 'P1']
    check("Spec includes P0 capabilities", len(p0_items) >= 3)
    check("Spec includes P1 capabilities", len(p1_items) >= 3)

    # ---------------------------------------------------------
    # 4. Multi-Tenant Boundary Isolation
    # ---------------------------------------------------------
    print("\n--- 4. Multi-Tenant Boundary Isolation ---")
    req_org_b = factory.get('/api/v1/product-position/')
    force_authenticate(req_org_b, user=org_b_user)
    res_org_b = view(req_org_b)
    check("Tenant B gets own isolated profile", res_org_b.status_code == 200)
    check("Tenant B profile does NOT leak Tenant A's market (fintech vs default)", res_org_b.data.get('target_market') == 'b2b_saas')
    check("Tenant B has 0 completed buyer tasks", len(res_org_b.data.get('buyer_tasks_completed', [])) == 0)

    # ---------------------------------------------------------
    # 5. RBAC & Adversarial Security Validation
    # ---------------------------------------------------------
    print("\n--- 5. RBAC & Adversarial Security Validation ---")
    # Rep cannot update positioning profile
    req_rep_mutate = factory.post('/api/v1/product-position/', {'target_market': 'healthcare'}, format='json')
    force_authenticate(req_rep_mutate, user=rep_user)
    res_rep_mutate = view(req_rep_mutate)
    check("Regular sales rep cannot modify positioning (403 Forbidden)", res_rep_mutate.status_code == 403)

    # Anonymous access rejected
    req_anon = factory.get('/api/v1/product-position/')
    res_anon = view(req_anon)
    check("Anonymous request fails closed (401 Unauthorized)", res_anon.status_code == 401)

    # Malformed task key rejected
    req_bad_task = factory.post('/api/v1/product-position/complete-task/', {'task_key': 'non_existent_step'}, format='json')
    force_authenticate(req_bad_task, user=admin_user)
    res_bad_task = complete_task_view(req_bad_task)
    check("Malformed buyer task key rejected (400 Bad Request)", res_bad_task.status_code == 400)

    # ---------------------------------------------------------
    # 6. Operational Readiness: Feature Flag Circuit Breaker
    # ---------------------------------------------------------
    print("\n--- 6. Operational Feature Flag Circuit Breaker ---")
    os.environ['PRODUCT_POSITIONING_ENABLED'] = 'False'
    try:
        req_flag = factory.get('/api/v1/product-position/')
        force_authenticate(req_flag, user=admin_user)
        res_flag = view(req_flag)
        check("Kill switch active: Returns 503 Service Unavailable when flag=False", res_flag.status_code == 503)
    finally:
        os.environ['PRODUCT_POSITIONING_ENABLED'] = 'True'

    req_flag_restored = factory.get('/api/v1/product-position/')
    force_authenticate(req_flag_restored, user=admin_user)
    res_flag_restored = view(req_flag_restored)
    check("Service restored: Returns 200 OK when flag=True", res_flag_restored.status_code == 200)

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"PRODUCT POSITIONING SUMMARY: {len(passes)} PASSED, {len(failures)} FAILED")
    print("=" * 70)

    if failures:
        print("\nFAILURES DETECTED:")
        for name, details in failures:
            print(f"- {name}: {details}")
        sys.exit(1)
    else:
        print("\nALL PRODUCT POSITIONING & BUYER TASK CHECKS PASSED!")
        sys.exit(0)


if __name__ == '__main__':
    run_checks()
