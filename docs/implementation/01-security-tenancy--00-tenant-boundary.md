# Engineering Evidence Report: 01-security-tenancy / 00-tenant-boundary

**Workstream**: Multi-Tenant Boundary Isolation & Authorization Hardening  
**Target Repository**: `Faizanmal/MyCRM`  
**Execution Branch**: `master` (strict adherence to user branch policy)  
**Status**: VERIFIED & DEPLOYED

---

## 1. Discovered Initial State & Critical Vulnerabilities

During deep forensic inspection of the codebase prior to remediation, the following high-risk multi-tenant isolation flaws were identified:

1. **Unsafe Ambient State (`backend/multi_tenant/middleware.py`)**:
   - Stored tenant and user state on `threading.local()`, which is unsafe under asynchronous ASGI/Channels workloads and threaded worker pool re-use.
2. **Silent Default Fallback / Auto-Creation**:
   - `TenantMiddleware` automatically resolved or auto-created an organization named `default` (`Organization.objects.get_or_create(slug='default')`) when missing or unauthenticated, bypassing tenant boundary enforcement.
   - `TenantAwareModel.save()` likewise silently bound records to `slug='default'`.
3. **Premature Evaluation of JWT Tokens**:
   - Standard Django middleware executes before Django REST Framework (DRF) view dispatch. Bearer JWT tokens were not parsed during middleware execution, causing `request.user` to appear anonymous and resulting in false-positive default fallbacks or missed membership validation.
4. **Detail Endpoint Authorization Bypass**:
   - `multi_tenant/permissions.py` contained `if getattr(view, 'detail', False): return True` in `IsOrganizationMember`, `IsOrganizationAdmin`, and `IsOrganizationOwner`, permitting unauthorized access to any resource detail view whenever object-level permissions were not independently wired.
5. **Missing Tenant Foreign Keys on Core CRM Models**:
   - `Lead`, `Contact`, `Opportunity`, and `Task` did not have explicit direct foreign keys to `multi_tenant.Organization`.
6. **Cross-Tenant Query and Mutation Bleed**:
   - API V1 ViewSets (`LeadViewSet`, `ContactViewSet`, `OpportunityViewSet`, `TaskViewSet`) queried `all()` without enforcing tenant isolation in `get_queryset()`.
   - `bulk_update` accepted arbitrary lists of primary keys without ensuring they belonged to the caller's organization.
   - `CSVExportView` exported all records across all tenants.
7. **WebSocket Cross-Tenant Information Leak**:
   - `ActivityFeedConsumer` joined a global, unscoped Channel layer group (`activity_feed`), broadcasting updates across all tenants.

---

## 2. Architecture Decisions & Implementation

### 2.1 Async-Safe ContextVars
- Replaced `threading.local` with Python `contextvars.ContextVar`:
  - `_current_organization_ctx: ContextVar[Optional[Organization]]`
  - `_current_user_ctx: ContextVar[Optional[User]]`
  - `_current_member_ctx: ContextVar[Optional[OrganizationMember]]`
- Exported thread- and coroutine-safe helpers: `get_current_organization()`, `set_current_organization()`, and `reset_tenant_context()`.

### 2.2 Pre-Authentication & Fail-Closed Middleware
- Implemented `_preauthenticate_jwt(request)` within `TenantMiddleware` using `rest_framework_simplejwt.authentication.JWTAuthentication`.
- If an explicit tenant header (`X-Organization-Slug` or `X-Tenant-ID`) or tenant subdomain/domain is supplied:
  - If the authenticated user is NOT an active member of that tenant, the request fails closed immediately with `403 Forbidden` (`{"error": "Forbidden: You do not have access to this organization.", "code": "tenant_forbidden"}`).
  - Removed all production fallbacks to `slug='default'`.

### 2.3 Direct Foreign Keys & Automatic Scoping
- Added `organization = models.ForeignKey('multi_tenant.Organization', on_delete=models.CASCADE, ...)` to `Lead`, `Contact`, `Opportunity`, and `Task`.
- Wired `save()` methods to auto-populate `organization` from the active contextvar or active user membership.
- Applied non-destructive database migrations.

### 2.4 Queryset and Bulk Scoping
- Integrated `TenantObjectPermission` across `LeadViewSet`, `ContactViewSet`, `OpportunityViewSet`, and `TaskViewSet`.
- In `get_queryset()`, scoped queries to `queryset.filter(organization=request.organization)` (or `none()` if not authenticated/no org).
- In `bulk_update()`, scoped updates to `self.get_queryset().filter(id__in=ids)`. If any ID belongs to another tenant, the entire request is rejected with `404 Not Found`.
- In `CSVExportView`, strictly filtered queryset by `request.organization`.

### 2.5 Real-Time WebSocket Scoping
- Scoped `ActivityFeedConsumer` to tenant-specific channel groups: `f"activity_feed_tenant_{self.tenant_id}"`.
- Anonymous connections or connections from users without active organization memberships are rejected immediately (`await self.close()`).

---

## 3. Concrete Touched Paths

- `backend/multi_tenant/middleware.py`
- `backend/multi_tenant/permissions.py`
- `backend/multi_tenant/models.py`
- `backend/lead_management/models.py`
- `backend/contact_management/models.py`
- `backend/opportunity_management/models.py`
- `backend/task_management/models.py`
- `backend/api/v1/views.py`
- `backend/api/v1/import_export.py`
- `backend/core/consumers.py`
- `backend/backend/settings.py`
- `backend/lead_qualification/models.py`
- `scripts/verify_tenant_boundary.py`
- `backend/tests/test_tenant_boundary.py`

---

## 4. Verification & Validation Evidence

### Verification Harness: `scripts/verify_tenant_boundary.py`
```
======================================================================
STARTING 00-TENANT-BOUNDARY VERIFICATION SUITE
======================================================================

[Check 1] Cross-Tenant Header Rejection (Org A user requesting Org B slug)
  PASS: Header spoofing correctly rejected with 403 tenant_forbidden.

[Check 2] Cross-Tenant Subdomain Rejection
  PASS: Host spoofing correctly rejected with 403.

[Check 3] Unauthenticated / Anonymous Access with Org Header
  PASS: Anonymous access fails closed.

[Check 4] Cross-Tenant Direct Object Access (Lead, Contact, Opportunity, Task)
  PASS: Cross-tenant direct object access properly isolated (404/Not Found).

[Check 5] Cross-Tenant Bulk Mutation Attack Rejection
  PASS: Cross-tenant bulk operations rejected without mutating foreign records.

[Check 6] CSV Export Tenant Scoping
  PASS: CSV export is strictly scoped to the requesting tenant.

[Check 7] WebSocket ActivityFeedConsumer Tenant Isolation
  PASS: ActivityFeedConsumer resolves correct tenant channel (activity_feed_tenant_...).

[Check 8] ContextVar Async Cleanup
  PASS: ContextVar safely resets without ambient state leaks.

======================================================================
ALL 00-TENANT-BOUNDARY VERIFICATION CHECKS PASSED SUCCESSFULLY!
======================================================================
```
Result: **100% Passed**.
