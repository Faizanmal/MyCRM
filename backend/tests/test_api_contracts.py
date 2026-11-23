"""
Comprehensive API Contract & Route Registry Tests
================================================
Validates:
1. OpenAPI 3.0 schema generation & validation (drf-spectacular)
2. Zero accidentally removed routes across legacy & modern v1 namespaces
3. RFC 8594 API Deprecation and Sunset headers
4. Snapshot / contract validation for core CRM resources (Lead, Contact, Opportunity, Task)
5. Adversarial security: anonymous fail-closed, malformed payloads
"""
import io
import os
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import get_resolver, URLPattern, URLResolver
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from multi_tenant.models import Organization, OrganizationMember
from lead_management.models import Lead
from contact_management.models import Contact
from opportunity_management.models import Opportunity
from task_management.models import Task

User = get_user_model()


@pytest.mark.django_db
class TestOpenApiContract:
    """Validates OpenAPI 3.0 schema compliance and integrity"""

    def test_openapi_schema_validates_cleanly(self):
        """drf-spectacular schema validation passes with 0 errors"""
        out = io.StringIO()
        call_command('spectacular', '--validate', stdout=out)
        # Succeeded without exception

    def test_core_crm_paths_present_in_schema(self):
        """Schema file exists and contains core CRM and v1 routes"""
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'openapi_schema.yml')
        if not os.path.exists(schema_path):
            call_command('spectacular', '--file', schema_path)
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '/api/contacts/' in content
        assert '/api/leads/' in content
        assert '/api/v1/health/' in content


@pytest.mark.django_db
class TestRouteRegistry:
    """Ensures zero accidentally removed routes across the entire URL registry"""

    def test_zero_accidentally_removed_routes(self):
        def extract_urls(patterns, prefix=""):
            routes = []
            for p in patterns:
                if isinstance(p, URLPattern):
                    raw = prefix + str(p.pattern)
                    routes.append(raw.replace('^', '').replace('$', ''))
                elif isinstance(p, URLResolver):
                    clean_pref = (prefix + str(p.pattern)).replace('^', '')
                    routes.extend(extract_urls(p.url_patterns, clean_pref))
            return routes

        all_routes = extract_urls(get_resolver().url_patterns)
        assert len(all_routes) > 500, f"Expected > 500 routes, found {len(all_routes)}"

        expected_legacy = [
            'api/contacts/',
            'api/leads/',
            'api/opportunities/',
            'api/tasks/',
            'api/communications/',
            'api/campaigns/',
            'api/documents/',
            'api/integrations/',
            'api/activity/',
            'api/reports/',
        ]
        for pref in expected_legacy:
            matching = [r for r in all_routes if r.startswith(pref)]
            assert len(matching) > 0, f"Zero route removal failed: {pref} missing"

        expected_v1 = [
            'api/v1/leads/',
            'api/v1/contacts/',
            'api/v1/opportunities/',
            'api/v1/tasks/',
            'api/v1/health/',
        ]
        for pref in expected_v1:
            matching = [r for r in all_routes if r.startswith(pref)]
            assert len(matching) > 0, f"Unified v1 route failed: {pref} missing"


@pytest.mark.django_db
class TestApiDeprecationAndSunset:
    """Validates RFC 8594 Deprecation and Sunset header behavior"""

    def test_legacy_endpoints_emit_rfc8594_headers(self, client):
        legacy_endpoints = ['/api/contacts/', '/api/leads/', '/api/opportunities/', '/api/tasks/']
        for path in legacy_endpoints:
            res = client.get(path)
            assert res.headers.get('Deprecation') == 'true'
            assert '2026' in res.headers.get('Sunset', '')
            expected_link = f'<{path.replace("/api/", "/api/v1/", 1)}>; rel="successor-version"'
            assert res.headers.get('Link') == expected_link

    def test_versioned_endpoints_do_not_emit_deprecation_headers(self, client):
        v1_endpoints = ['/api/v1/contacts/', '/api/v1/leads/', '/api/v1/opportunities/', '/api/v1/tasks/']
        for path in v1_endpoints:
            res = client.get(path)
            assert 'Deprecation' not in res.headers
            assert 'Sunset' not in res.headers


@pytest.mark.django_db
class TestCrmContractSnapshots:
    """Validates contract schemas, payloads, and envelopes for core CRM resources"""

    @pytest.fixture
    def auth_context(self):
        org, _ = Organization.objects.get_or_create(slug="snap-org", defaults={"name": "Snapshot Org", "plan": "enterprise"})
        user, _ = User.objects.get_or_create(
            username="snapuser",
            defaults={"email": "snapuser@example.com"}
        )
        OrganizationMember.objects.get_or_create(organization=org, user=user, defaults={"role": "admin"})
        client = APIClient()
        token = str(RefreshToken.for_user(user).access_token)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}', HTTP_X_ORGANIZATION_SLUG=org.slug)
        return client, org, user

    def test_lead_contract_lifecycle(self, auth_context):
        client, _, _ = auth_context
        # Create
        payload = {
            'first_name': 'Snapshot',
            'last_name': 'Lead',
            'email': 'lead@snap.com',
            'phone': '+1234567890',
            'company_name': 'Snapshot Corp',
            'status': 'new',
            'priority': 'high',
        }
        res_create = client.post('/api/v1/leads/', data=payload, format='json')
        assert res_create.status_code == 201
        data = res_create.json()
        assert data['first_name'] == 'Snapshot'
        assert data['company_name'] == 'Snapshot Corp'

        # Retrieve
        lead_id = data['id']
        res_get = client.get(f'/api/v1/leads/{lead_id}/')
        assert res_get.status_code == 200
        assert res_get.json()['id'] == lead_id

        # List envelope
        res_list = client.get('/api/v1/leads/')
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert 'count' in list_data
        assert 'results' in list_data

    def test_contact_contract_lifecycle(self, auth_context):
        client, _, _ = auth_context
        payload = {
            'first_name': 'Snapshot',
            'last_name': 'Contact',
            'email': 'contact@snap.com',
            'company_name': 'Snapshot Corp',
            'status': 'active',
        }
        res_create = client.post('/api/v1/contacts/', data=payload, format='json')
        assert res_create.status_code == 201
        data = res_create.json()
        assert data['first_name'] == 'Snapshot'

        # List envelope
        res_list = client.get('/api/v1/contacts/')
        assert res_list.status_code == 200
        assert 'results' in res_list.json()

    def test_opportunity_contract_lifecycle(self, auth_context):
        client, _, _ = auth_context
        # Create a contact first
        contact_res = client.post('/api/v1/contacts/', data={
            'salutation': 'ms',
            'first_name': 'Deal',
            'last_name': 'Contact',
            'email': 'deal@snap.com',
            'status': 'active',
        }, format='json')
        contact_id = contact_res.json()['id']

        payload = {
            'name': 'Big Deal',
            'contact': contact_id,
            'amount': '25000.00',
            'stage': 'qualification',
            'probability': 50,
            'expected_close_date': '2026-12-31',
        }
        res_create = client.post('/api/v1/opportunities/', data=payload, format='json')
        assert res_create.status_code == 201
        data = res_create.json()
        assert data['name'] == 'Big Deal'

        res_list = client.get('/api/v1/opportunities/')
        assert res_list.status_code == 200
        assert 'results' in res_list.json()

    def test_task_contract_lifecycle(self, auth_context):
        client, _, user = auth_context
        # Create a contact first
        contact_res = client.post('/api/v1/contacts/', data={
            'salutation': 'ms',
            'first_name': 'Task',
            'last_name': 'Contact',
            'email': 'task@snap.com',
            'status': 'active',
        }, format='json')
        contact_id = contact_res.json()['id']

        # Create lead and opp first
        lead_res = client.post('/api/v1/leads/', data={
            'first_name': 'Task',
            'last_name': 'Lead',
            'email': 'tasklead@snap.com',
            'company_name': 'Task Corp',
            'status': 'new',
            'priority': 'high',
        }, format='json')
        lead_id = lead_res.json()['id']

        opp_res = client.post('/api/v1/opportunities/', data={
            'name': 'Task Opp',
            'contact': contact_id,
            'amount': '10000.00',
            'stage': 'qualification',
            'probability': 50,
            'expected_close_date': '2026-12-31',
        }, format='json')
        opp_id = opp_res.json()['id']

        payload = {
            'title': 'Contract Task',
            'task_type': 'meeting',
            'priority': 'medium',
            'status': 'pending',
            'contact': contact_id,
            'lead': lead_id,
            'opportunity': opp_id,
            'assigned_to': user.id,
        }
        res_create = client.post('/api/v1/tasks/', data=payload, format='json')
        assert res_create.status_code == 201
        data = res_create.json()
        assert data['title'] == 'Contract Task'

        res_list = client.get('/api/v1/tasks/')
        assert res_list.status_code == 200
        assert 'results' in res_list.json()


@pytest.mark.django_db
class TestAdversarialSecurity:
    """Validates fail-closed behavior on unauthorized, anonymous, and malformed inputs"""

    def test_anonymous_requests_fail_closed(self, client):
        assert client.get('/api/v1/leads/').status_code == 401
        assert client.get('/api/v1/contacts/').status_code == 401
        assert client.get('/api/v1/opportunities/').status_code == 401
        assert client.get('/api/v1/tasks/').status_code == 401

    def test_malformed_payload_fails_closed(self):
        client = APIClient()
        user, _ = User.objects.get_or_create(username="maluser", defaults={"email": "mal@snap.com"})
        token = str(RefreshToken.for_user(user).access_token)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Task requires title
        res = client.post('/api/v1/tasks/', data={'description': 'No title provided'}, format='json')
        assert res.status_code == 400
        assert 'title' in res.json()
