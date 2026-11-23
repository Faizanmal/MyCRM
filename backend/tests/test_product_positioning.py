"""
Product Positioning, ICP, JTBD, and Buyer Task Tests
===================================================
Tests:
1. Product positioning profile retrieval and update
2. 5 Buyer tasks completion progression
3. Value metrics computation
4. Prioritized product spec endpoint (P0/P1/P2)
5. Multi-tenant boundary isolation
6. RBAC permissions (Admin vs Member)
7. Adversarial input validation (anonymous, malformed keys)
8. Operational readiness (feature flag circuit breaker)
"""
import os
import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate

from multi_tenant.models import Organization, OrganizationMember, ProductPositioningProfile
from multi_tenant.positioning_views import ProductPositioningViewSet

User = get_user_model()


class TestProductPositioningSuite(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.test_id = str(uuid.uuid4())[:8]

        self.org_a = Organization.objects.create(name=f"Org A {self.test_id}", slug=f"org-a-{self.test_id}")
        self.org_b = Organization.objects.create(name=f"Org B {self.test_id}", slug=f"org-b-{self.test_id}")

        self.admin_user = User.objects.create_user(
            username=f"admin_{self.test_id}",
            email=f"admin_{self.test_id}@example.com",
            password="password123"
        )
        self.admin_user.organization = self.org_a
        self.admin_user.save()
        OrganizationMember.objects.create(organization=self.org_a, user=self.admin_user, role="admin")

        self.rep_user = User.objects.create_user(
            username=f"rep_{self.test_id}",
            email=f"rep_{self.test_id}@example.com",
            password="password123"
        )
        self.rep_user.organization = self.org_a
        self.rep_user.save()
        OrganizationMember.objects.create(organization=self.org_a, user=self.rep_user, role="member")

        self.org_b_user = User.objects.create_user(
            username=f"user_b_{self.test_id}",
            email=f"user_b_{self.test_id}@example.com",
            password="password123"
        )
        self.org_b_user.organization = self.org_b
        self.org_b_user.save()
        OrganizationMember.objects.create(organization=self.org_b, user=self.org_b_user, role="admin")

        self.view = ProductPositioningViewSet.as_view({'get': 'list', 'post': 'create'})
        self.complete_task_view = ProductPositioningViewSet.as_view({'post': 'complete_task'})
        self.spec_view = ProductPositioningViewSet.as_view({'get': 'spec'})
        self.metrics_view = ProductPositioningViewSet.as_view({'get': 'metrics'})

    def test_profile_retrieval_and_update(self):
        req = self.factory.get('/api/v1/product-position/')
        force_authenticate(req, user=self.admin_user)
        res = self.view(req)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('target_market'), 'b2b_saas')

        req_update = self.factory.post('/api/v1/product-position/', {
            'target_market': 'healthtech',
            'ideal_customer_profile': 'mid_market',
            'team_size_tier': '20_100',
            'primary_jtbd': 'data_consolidation'
        }, format='json')
        force_authenticate(req_update, user=self.admin_user)
        res_update = self.view(req_update)
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.data.get('target_market'), 'healthtech')

    def test_five_buyer_tasks_progression(self):
        tasks = ['eval_poc', 'data_migration', 'team_onboarding', 'pipeline_execution', 'roi_measurement']
        expected_pct = [20.0, 40.0, 60.0, 80.0, 100.0]

        for i, task_key in enumerate(tasks):
            req = self.factory.post('/api/v1/product-position/complete-task/', {'task_key': task_key}, format='json')
            force_authenticate(req, user=self.admin_user)
            res = self.complete_task_view(req)
            self.assertEqual(res.status_code, 200)
            self.assertIn(task_key, res.data.get('buyer_tasks_completed', []))
            self.assertEqual(res.data.get('completion_percentage'), expected_pct[i])

        req_final = self.factory.get('/api/v1/product-position/')
        force_authenticate(req_final, user=self.admin_user)
        res_final = self.view(req_final)
        self.assertEqual(res_final.data.get('onboarding_status'), 'completed')
        self.assertIsNotNone(res_final.data.get('completed_at'))

    def test_value_metrics_and_product_spec(self):
        req_metrics = self.factory.get('/api/v1/product-position/metrics/')
        force_authenticate(req_metrics, user=self.admin_user)
        res_metrics = self.metrics_view(req_metrics)
        self.assertEqual(res_metrics.status_code, 200)
        self.assertEqual(res_metrics.data.get('administrative_time_reduction_pct'), 42.0)

        req_spec = self.factory.get('/api/v1/product-position/spec/')
        force_authenticate(req_spec, user=self.admin_user)
        res_spec = self.spec_view(req_spec)
        self.assertEqual(res_spec.status_code, 200)
        self.assertIn('strategic_vision', res_spec.data)
        self.assertGreaterEqual(len(res_spec.data.get('prioritized_roadmap', [])), 6)

    def test_multi_tenant_isolation(self):
        # Admin updates Org A
        req_update = self.factory.post('/api/v1/product-position/', {'target_market': 'fintech'}, format='json')
        force_authenticate(req_update, user=self.admin_user)
        self.view(req_update)

        # Org B reads profile
        req_org_b = self.factory.get('/api/v1/product-position/')
        force_authenticate(req_org_b, user=self.org_b_user)
        res_org_b = self.view(req_org_b)
        self.assertEqual(res_org_b.status_code, 200)
        self.assertEqual(res_org_b.data.get('target_market'), 'b2b_saas')

    def test_rbac_and_adversarial_validation(self):
        # Rep cannot mutate
        req_rep = self.factory.post('/api/v1/product-position/', {'target_market': 'illegal'}, format='json')
        force_authenticate(req_rep, user=self.rep_user)
        res_rep = self.view(req_rep)
        self.assertEqual(res_rep.status_code, 403)

        # Anonymous cannot read
        req_anon = self.factory.get('/api/v1/product-position/')
        res_anon = self.view(req_anon)
        self.assertEqual(res_anon.status_code, 401)

        # Invalid task key
        req_bad = self.factory.post('/api/v1/product-position/complete-task/', {'task_key': 'invalid_task'}, format='json')
        force_authenticate(req_bad, user=self.admin_user)
        res_bad = self.complete_task_view(req_bad)
        self.assertEqual(res_bad.status_code, 400)

    def test_feature_flag_circuit_breaker(self):
        os.environ['PRODUCT_POSITIONING_ENABLED'] = 'False'
        try:
            req = self.factory.get('/api/v1/product-position/')
            force_authenticate(req, user=self.admin_user)
            res = self.view(req)
            self.assertEqual(res.status_code, 503)
        finally:
            os.environ['PRODUCT_POSITIONING_ENABLED'] = 'True'
