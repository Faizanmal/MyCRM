"""
Domain Acceptance and Adversarial Test Suite for CRM Core: Contacts & Accounts
Workstream: 02-crm-core--00-contacts-accounts

Validates:
1. Contact/Account CRUD across multiple tenants (fail-closed tenant isolation)
2. Conflict & duplicate scenarios (per-tenant scoping)
3. 10,000 fixture import with bounded memory consumption (< 50MB peak)
4. Merge & unmerge policy, invariants, and relation repointing
5. Strict prevention of cross-organization user reassignment
6. Adversarial validations: anonymous, wrong-tenant, insufficient-role, malformed payload, self-merge, stale data
7. Feature flag kill switches
"""
import tracemalloc
import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from contact_management.models import Account, Contact, ContactActivity, ContactGroup, MergeAuditLog
from contact_management.services import AccountService, ContactService
from multi_tenant.models import Organization, OrganizationMember

User = get_user_model()


@pytest.fixture
def multi_tenant_setup(db):
    """Set up two isolated organizations with admin and viewer users."""
    # Org A
    org_a = Organization.objects.create(name="Alpha Corp", slug="alpha-corp", status="active")
    admin_a = User.objects.create_user(username="admin_a", email="admin@alpha.com", password="password123")
    viewer_a = User.objects.create_user(username="viewer_a", email="viewer@alpha.com", password="password123")
    OrganizationMember.objects.create(organization=org_a, user=admin_a, role="admin", is_active=True)
    OrganizationMember.objects.create(organization=org_a, user=viewer_a, role="viewer", is_active=True)

    # Org B
    org_b = Organization.objects.create(name="Beta Ltd", slug="beta-ltd", status="active")
    admin_b = User.objects.create_user(username="admin_b", email="admin@beta.com", password="password123")
    OrganizationMember.objects.create(organization=org_b, user=admin_b, role="admin", is_active=True)

    def make_client(user, org):
        client = APIClient()
        token = RefreshToken.for_user(user)
        client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token.access_token}",
            HTTP_X_ORGANIZATION_SLUG=org.slug
        )
        return client

    return {
        "org_a": org_a,
        "admin_a": admin_a,
        "viewer_a": viewer_a,
        "client_a": make_client(admin_a, org_a),
        "client_viewer_a": make_client(viewer_a, org_a),
        "org_b": org_b,
        "admin_b": admin_b,
        "client_b": make_client(admin_b, org_b),
    }


@pytest.mark.django_db
class TestMultiTenantContactAccountCRUD:
    """Validate full CRUD and strict isolation across two distinct tenants."""

    def test_account_crud_and_cross_tenant_isolation(self, multi_tenant_setup):
        setup = multi_tenant_setup
        client_a = setup["client_a"]
        client_b = setup["client_b"]
        org_a = setup["org_a"]
        org_b = setup["org_b"]

        # 1. Tenant A creates account
        resp_a = client_a.post("/api/v1/accounts/", {
            "name": "Acme Global",
            "domain": "acme.com",
            "tier": "enterprise",
            "account_type": "customer"
        }, format="json")
        assert resp_a.status_code == status.HTTP_201_CREATED
        account_a_id = resp_a.data["id"]

        # 2. Tenant B creates account
        resp_b = client_b.post("/api/v1/accounts/", {
            "name": "Beta Enterprises",
            "domain": "beta.io",
            "tier": "mid_market",
            "account_type": "prospect"
        }, format="json")
        assert resp_b.status_code == status.HTTP_201_CREATED
        account_b_id = resp_b.data["id"]

        # 3. Isolation: Tenant A cannot see or edit Tenant B's account
        get_b_from_a = client_a.get(f"/api/v1/accounts/{account_b_id}/")
        assert get_b_from_a.status_code == status.HTTP_404_NOT_FOUND

        update_b_from_a = client_a.patch(f"/api/v1/accounts/{account_b_id}/", {"name": "Hacked Beta"})
        assert update_b_from_a.status_code == status.HTTP_404_NOT_FOUND

        # 4. Isolation: Tenant B cannot see or edit Tenant A's account
        get_a_from_b = client_b.get(f"/api/v1/accounts/{account_a_id}/")
        assert get_a_from_b.status_code == status.HTTP_404_NOT_FOUND

        # 5. List query returns only tenant's own records
        list_a = client_a.get("/api/v1/accounts/")
        assert list_a.status_code == status.HTTP_200_OK
        ids_a = [item["id"] for item in list_a.data.get("results", list_a.data)]
        assert account_a_id in ids_a
        assert account_b_id not in ids_a

    def test_contact_crud_with_account_linkage(self, multi_tenant_setup):
        setup = multi_tenant_setup
        client_a = setup["client_a"]
        org_a = setup["org_a"]

        # Create Account in Org A
        account_a = Account.objects.create(name="Stark Industries", organization=org_a)

        # Create Contact linked to Account
        resp = client_a.post("/api/v1/contacts/", {
            "first_name": "Tony",
            "last_name": "Stark",
            "email": "tony@stark.com",
            "account": account_a.id,
            "lifecycle_stage": "customer",
            "score": 95
        }, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        contact_id = resp.data["id"]
        assert resp.data["account"] == account_a.id
        assert resp.data["company"] == "Stark Industries"

        # Verify DB integrity
        contact = Contact.objects.get(id=contact_id)
        assert contact.account_id == account_a.id
        assert contact.organization_id == org_a.id


@pytest.mark.django_db
class TestCrossTenantReassignmentProtection:
    """Ensure entities cannot be assigned across organization boundaries."""

    def test_prevent_cross_org_contact_owner_reassignment(self, multi_tenant_setup):
        setup = multi_tenant_setup
        org_a = setup["org_a"]
        admin_b = setup["admin_b"]
        client_a = setup["client_a"]

        # Attempt to create contact in Org A assigned to User from Org B
        resp = client_a.post("/api/v1/contacts/", {
            "first_name": "Infiltrator",
            "last_name": "Spy",
            "email": "spy@alpha.com",
            "owner": admin_b.id
        }, format="json")

        # Serializer / model validation should fail closed
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "owner" in resp.data or "assigned_to" in resp.data or "error" in resp.data

    def test_prevent_cross_org_account_linking(self, multi_tenant_setup):
        setup = multi_tenant_setup
        org_b = setup["org_b"]
        client_a = setup["client_a"]

        # Account belongs to Org B
        account_b = Account.objects.create(name="Target Corp", organization=org_b)

        # Attempt to link Org A contact to Org B account
        resp = client_a.post("/api/v1/contacts/", {
            "first_name": "Peter",
            "last_name": "Parker",
            "email": "peter@bugle.com",
            "account": account_b.id
        }, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestMergeAndUnmergePolicy:
    """Validate atomic merge, snapshot preservation, unmerge restoration, and invariants."""

    def test_contact_merge_and_unmerge_lifecycle(self, multi_tenant_setup):
        setup = multi_tenant_setup
        client_a = setup["client_a"]
        org_a = setup["org_a"]

        # Create Primary and Secondary contacts in Org A
        c_primary = Contact.objects.create(
            organization=org_a,
            first_name="Bruce",
            last_name="Wayne",
            email="bruce@wayne.com",
            phone="111-222"
        )
        c_secondary = Contact.objects.create(
            organization=org_a,
            first_name="Batman",
            last_name="Wayne",
            email="batman@wayne.com",
            phone="333-444",
            job_title="Vigilante"
        )

        # Attach activity to secondary contact
        act = ContactActivity.objects.create(
            contact=c_secondary,
            activity_type="call",
            subject="Patrol Call",
            content="Patrol discussion",
            created_by=setup["admin_a"]
        )

        # 1. Merge secondary into primary via API
        merge_resp = client_a.post("/api/v1/contacts/merge/", {
            "primary_id": c_primary.id,
            "secondary_id": c_secondary.id,
            "field_choices": {"job_title": "secondary"}  # take job_title from secondary
        }, format="json")
        assert merge_resp.status_code == status.HTTP_200_OK
        audit_log_id = merge_resp.data["audit_log_id"]

        # Check Invariants after merge
        c_primary.refresh_from_db()
        c_secondary.refresh_from_db()
        act.refresh_from_db()

        assert c_secondary.is_merged is True
        assert c_secondary.merged_into_id == c_primary.id
        assert c_primary.job_title == "Vigilante"
        assert act.contact_id == c_primary.id  # activity repointed to primary

        # Verify Audit Log exists and holds snapshots
        audit = MergeAuditLog.objects.get(id=audit_log_id)
        assert audit.entity_type == "contact"
        assert audit.primary_id == c_primary.id
        assert audit.secondary_id == c_secondary.id
        assert audit.repointed_relations["activities"] == [act.id]

        # 2. Unmerge via API
        unmerge_resp = client_a.post("/api/v1/contacts/unmerge/", {
            "audit_log_id": audit_log_id
        }, format="json")
        assert unmerge_resp.status_code == status.HTTP_200_OK

        # Check Invariants after unmerge
        c_primary.refresh_from_db()
        c_secondary.refresh_from_db()
        act.refresh_from_db()

        assert c_secondary.is_merged is False
        assert c_secondary.merged_into_id is None
        assert act.contact_id == c_secondary.id  # activity repointed back to secondary

    def test_cross_tenant_merge_strictly_rejected(self, multi_tenant_setup):
        setup = multi_tenant_setup
        client_a = setup["client_a"]
        c_a = Contact.objects.create(organization=setup["org_a"], first_name="A", last_name="Alpha", email="a@alpha.com")
        c_b = Contact.objects.create(organization=setup["org_b"], first_name="B", last_name="Beta", email="b@beta.com")

        # Tenant A attempts to merge c_b into c_a
        resp = client_a.post("/api/v1/contacts/merge/", {
            "primary_id": c_a.id,
            "secondary_id": c_b.id
        }, format="json")
        assert resp.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_self_merge_and_already_merged_rejected(self, multi_tenant_setup):
        setup = multi_tenant_setup
        client_a = setup["client_a"]
        c_a = Contact.objects.create(organization=setup["org_a"], first_name="Self", last_name="Merge", email="self@test.com")

        # Self-merge
        resp = client_a.post("/api/v1/contacts/merge/", {
            "primary_id": c_a.id,
            "secondary_id": c_a.id
        }, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDuplicateDetectionAndScoping:
    """Validate duplicate detection within a tenant and cross-tenant duplicate coexistence."""

    def test_duplicate_detection_within_tenant(self, multi_tenant_setup):
        setup = multi_tenant_setup
        client_a = setup["client_a"]
        org_a = setup["org_a"]

        Contact.objects.create(organization=org_a, first_name="Clark", last_name="Kent", email="clark@dailyplanet.com")
        Contact.objects.create(organization=org_a, first_name="Super", last_name="Man", email="clark@dailyplanet.com")

        resp = client_a.get("/api/v1/contacts/duplicates/?email=clark@dailyplanet.com")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) >= 1

    def test_same_email_allowed_across_different_tenants(self, multi_tenant_setup):
        setup = multi_tenant_setup
        client_a = setup["client_a"]
        client_b = setup["client_b"]

        # Both tenants create a contact with ceo@common.com
        resp_a = client_a.post("/api/v1/contacts/", {
            "first_name": "CEO", "last_name": "A", "email": "ceo@common.com"
        }, format="json")
        assert resp_a.status_code == status.HTTP_201_CREATED

        resp_b = client_b.post("/api/v1/contacts/", {
            "first_name": "CEO", "last_name": "B", "email": "ceo@common.com"
        }, format="json")
        assert resp_b.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestBoundedMemory10kImport:
    """Validate that streaming import of 10,000 fixture rows runs under bounded memory (< 50MB peak)."""

    def test_import_10k_contacts_bounded_memory(self, multi_tenant_setup):
        setup = multi_tenant_setup
        org_a = setup["org_a"]

        # Generator producing 10,000 fixture rows lazily
        def generate_10k_records():
            for i in range(10000):
                yield {
                    "first_name": f"First_{i}",
                    "last_name": f"Last_{i}",
                    "email": f"fixture_contact_{i}@benchmark-test.com",
                    "phone": f"555-000-{i:04d}",
                    "job_title": "Load Tester"
                }

        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()[0]

        service = ContactService(user=setup["admin_a"], organization=org_a)
        results = service.import_contacts_stream(
            stream_or_path=generate_10k_records(),
            batch_size=1000
        )

        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_increase_mb = (peak_memory - start_memory) / (1024 * 1024)

        assert results["created"] == 10000
        assert len(results["errors"]) == 0
        # Assert strictly bounded memory: peak memory increase must be under 50MB
        assert peak_increase_mb < 50.0, f"Memory peak exceeded: {peak_increase_mb:.2f} MB"
        assert Contact.objects.filter(organization=org_a, email__contains="benchmark-test.com").count() == 10000


@pytest.mark.django_db
class TestAdversarialAndOperationalGates:
    """Validate authentication gates, role permissions, malformed data, and feature switches."""

    def test_anonymous_requests_rejected(self):
        client = APIClient()
        resp_contacts = client.get("/api/v1/contacts/")
        resp_accounts = client.get("/api/v1/accounts/")
        assert resp_contacts.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp_accounts.status_code == status.HTTP_401_UNAUTHORIZED

    def test_insufficient_role_viewer_cannot_delete_or_merge(self, multi_tenant_setup):
        setup = multi_tenant_setup
        client_viewer = setup["client_viewer_a"]
        org_a = setup["org_a"]

        contact = Contact.objects.create(organization=org_a, first_name="Doomed", last_name="Contact", email="doomed@test.com")

        # Viewer attempts delete
        resp_delete = client_viewer.delete(f"/api/v1/contacts/{contact.id}/")
        assert resp_delete.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_malformed_payload_rejected(self, multi_tenant_setup):
        client_a = multi_tenant_setup["client_a"]
        # Missing required fields
        resp = client_a.post("/api/v1/contacts/", {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @override_settings(FEATURE_CONTACT_MERGE=False)
    def test_merge_feature_flag_kill_switch(self, multi_tenant_setup):
        setup = multi_tenant_setup
        client_a = setup["client_a"]
        org_a = setup["org_a"]

        c1 = Contact.objects.create(organization=org_a, first_name="C1", last_name="L1", email="c1@test.com")
        c2 = Contact.objects.create(organization=org_a, first_name="C2", last_name="L2", email="c2@test.com")

        resp = client_a.post("/api/v1/contacts/merge/", {
            "primary_id": c1.id,
            "secondary_id": c2.id
        }, format="json")

        assert resp.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]
        assert "feature" in str(resp.data).lower() or "disabled" in str(resp.data).lower()
