# Engineering Evidence Report: 01-security-tenancy / 01-rbac

**Workstream**: Parameterized Role-Based Access Control (RBAC) Hardening  
**Target Repository**: `Faizanmal/MyCRM`  
**Execution Branch**: `master` (retained directly on master per user constraint)  
**Status**: VERIFIED & DEPLOYED

---

## 1. Discovered Initial State & Critical Deficiencies

Forensic inspection of the access control system revealed key vulnerabilities:

1. **Unparameterized ViewSet Permissions**:
   - DRF ViewSets relied solely on `IsAuthenticated` or generic tenant checking without inspecting specific actions against tenant member roles (`owner`, `admin`, `manager`, `member`/`sales_rep`, `viewer`/`guest`).
2. **Missing Action-Level Constraints on Sensitive Operations**:
   - `bulk_update` accepted both `update` and `delete` commands identically without checking whether the user held high-privilege administrative roles. Non-admin users were able to invoke bulk deletions.
3. **Lack of Forbidden Field Rejection**:
   - Payloads with injected administrative/tenant fields (`organization`, `organization_id`, `is_merged`, `merged_into`, `created_by`, `role`, `is_superuser`) were either silently ignored or bypassed without rejecting the request or explaining the violation.
4. **Lack of Row-Level Isolation Under List, Search, and Aggregations**:
   - Members and sales representatives could see records belonging to their organization on `list` and search endpoints, rather than being restricted to records assigned to or owned by them.
   - Aggregation endpoints (`/statistics/`, `/pipeline/`) needed verification to guarantee row-level isolation for member roles.
5. **Data Exfiltration via Bulk Export**:
   - `CSVExportView` and contact export endpoints did not gate export capabilities by role, allowing low-privilege viewers or guests to exfiltrate entire tenant datasets.
6. **Frontend/Backend Role Discrepancies**:
   - The frontend RBAC type definitions lacked full alignment with backend tenant membership roles (`owner`, `admin`, `manager`, `member`, `sales_rep`, `viewer`, `guest`).

---

## 2. Architecture Decisions & Implementation

### 2.1 Granular `HasRolePermission` Implementation (`backend/multi_tenant/permissions.py`)
- Built a reusable, parameterized permission class enforcing:
  - **Role Hierarchy**: `Owner (50) > Admin (40) > Manager (30) > Member/SalesRep (20) > Viewer/Guest (10)`.
  - **Action-to-Role Matrix**:
    - **Read (`list`, `retrieve`, `statistics`, `pipeline`, `timeline`, `activities`, `duplicates`)**: `['owner', 'admin', 'manager', 'member', 'sales_rep', 'viewer']`
    - **Create & Mutate (`create`, `update`, `partial_update`, `convert`, `complete`)**: `['owner', 'admin', 'manager', 'member', 'sales_rep']`
    - **Destructive & Bulk Mutation (`destroy`, `bulk_update` [action='update'], `merge`, `unmerge`, `merge_preview`, `import`, `export`, `import_contacts`, `import_accounts`, `export_contacts`)**: `['owner', 'admin', 'manager']`
    - **High-Risk Bulk Deletion (`bulk_update` [action='delete'], `bulk_delete`)**: `['owner', 'admin']` only.
  - **Descriptive 403 Forbidden Explanations**:
    Returns exact details on missing permissions (e.g. `Insufficient permissions: Role 'viewer' cannot perform action 'create'. Required roles: owner, admin, manager, member, sales_rep.`).
    Bulk deletion returns `Insufficient permissions: Role 'manager' cannot perform bulk delete. Required roles: owner, admin.`.
  - **Explicit Forbidden Fields Rejection**:
    Enforces `FORBIDDEN_FIELDS_BY_ROLE` on `POST`, `PUT`, `PATCH`. Non-privileged roles attempting to supply restricted fields (`organization`, `role`, `created_by`, `is_superuser`, etc.) are rejected with HTTP 403 Forbidden:
    `Forbidden field(s) rejected for role '<role>': <fields>. Missing permission: role '<role>' cannot modify restricted system or tenant fields.`
  - **Row-Level Ownership Validation**:
    Enforces that `member` and `sales_rep` roles can only mutate objects where `owner_id == request.user.id`, `assigned_to_id == request.user.id`, or `created_by_id == request.user.id`.

### 2.2 Row-Level Scoping in Querysets & Aggregations (`backend/api/v1/views.py`, `backend/contact_management/views.py`)
- Configured `get_queryset()` across viewsets (`LeadViewSet`, `ContactViewSet`, `AccountViewSet`, `OpportunityViewSet`, `TaskViewSet`):
  - When requester has role `member` or `sales_rep`, querysets automatically filter to records owned by or assigned to `request.user`.
  - Organization admins, owners, and managers retain organization-wide visibility.
  - Aggregation endpoints (`/statistics/`, `/pipeline/`) use `self.get_queryset()`, inheriting complete row-level isolation.
  - Search queries via DRF `SearchFilter` operate on `get_queryset()`, preventing search bypass.

### 2.3 Operational Readiness & Feature Flags (`backend/backend/settings.py`)
- Added operational controls:
  - `FEATURE_STRICT_RBAC` (default `True`): Kill switch allowing emergency fallback if RBAC rules block critical production operations.
  - `FEATURE_FORBIDDEN_FIELDS_ENFORCEMENT` (default `True`): Configurable flag to toggle strict forbidden field validation.

### 2.4 Frontend Role Hierarchy Synchronization (`frontend/src/lib/rbac.tsx`)
- Synchronized `Role` union type: `owner | admin | manager | member | sales_rep | viewer | guest`.
- Updated `roleHierarchy` to align with backend permission weights (`owner: 5, admin: 4, manager: 3, member: 2, sales_rep: 2, viewer: 1, guest: 0`).
- Configured permissions for `member`, `sales_rep`, and `owner` roles across frontend route and feature guards, adding `merge_contacts` and `unmerge_contacts` permissions.

---

## 3. Concrete Touched Paths

- `backend/multi_tenant/permissions.py`: Added `FORBIDDEN_FIELDS_BY_ROLE`, `_check_forbidden_fields`, missing permission explanations, and operational settings checks.
- `backend/backend/settings.py`: Added `FEATURE_STRICT_RBAC` and `FEATURE_FORBIDDEN_FIELDS_ENFORCEMENT`.
- `backend/api/v1/views.py`: Updated action signatures for `convert` and `complete` with `*args, **kwargs` and tenant scoping on created objects.
- `frontend/src/lib/rbac.tsx`: Added `merge_contacts`, `unmerge_contacts` permissions and synchronized role definitions.
- `scripts/verify_rbac.py`: Expanded with forbidden field rejection, aggregation row-level tests, and operational kill-switch validations.
- `backend/tests/test_rbac.py`: Full parameterized 19-test suite covering role matrix, forbidden fields, row-level isolation, search, aggregations, and adversarial scenarios.

---

## 4. Verification Evidence

### Harness: `python scripts/verify_rbac.py`
```
======================================================================
STARTING 01-RBAC PARAMETERIZED VERIFICATION SUITE
======================================================================

[Check 1] Read Matrix & Row-Level Filtering Under List
  PASS: Owner, Admin, Manager have organization-wide visibility.
  PASS: Member/SalesRep row-level isolation verified in list/pagination.
  PASS: Viewer allowed read access.

[Check 2] Mutation Permissions Matrix & Missing Permission Explanation
  PASS: Viewer rejected on create with descriptive permission explanation.
  PASS: Member successfully created lead.
  PASS: Member successfully updated own lead.
  PASS: Member forbidden from updating unassigned/other leads.

[Check 3] Forbidden Fields Rejection (403 with Explanation)
  PASS: Member attempting to supply 'organization' field rejected with 403.
  PASS: Member attempting to supply 'role' field rejected with 403.

[Check 4] Parameterized Bulk Update vs Bulk Delete
  PASS: Member rejected from bulk_update.
  PASS: Manager allowed bulk_update (action=update).
  PASS: Manager rejected from bulk delete with descriptive permission explanation.
  PASS: Admin allowed bulk delete.

[Check 5] Aggregation Endpoints Row-Level Isolation
  PASS: Row-level isolation verified on /api/v1/leads/statistics/.

[Check 6] Operational Kill-Switch Verification
  PASS: FEATURE_STRICT_RBAC emergency kill switch allows bypass during rollback.
  PASS: FEATURE_FORBIDDEN_FIELDS_ENFORCEMENT emergency toggle works.

======================================================================
ALL 01-RBAC PARAMETERIZED CHECKS PASSED SUCCESSFULLY!
======================================================================
```

### Pytest Execution: `pytest backend/tests/test_rbac.py -v --no-cov`
```
============================= test session starts =============================
platform win32 -- Python 3.13.11, pytest-9.1.1, pluggy-1.7.0
django: version: 6.0.10, settings: backend.settings
collected 19 items

backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_list_visibility_by_role PASSED [  5%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_search_respects_row_level_isolation PASSED [ 10%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_statistics_aggregation_row_level_isolation PASSED [ 15%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_pipeline_aggregation_row_level_isolation PASSED [ 21%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_viewer_mutation_rejected_with_explanation PASSED [ 26%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_member_destroy_rejected_with_explanation PASSED [ 31%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_manager_destroy_allowed PASSED [ 36%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_member_update_own_allowed_other_rejected PASSED [ 42%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_convert_role_and_ownership_constraints PASSED [ 47%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_task_complete_role_constraints PASSED [ 52%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_bulk_update_and_bulk_delete_matrix PASSED [ 57%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_export_role_scoping PASSED [ 63%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_forbidden_fields_rejected_for_member PASSED [ 68%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_forbidden_fields_rejected_for_manager PASSED [ 73%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_cross_tenant_isolation PASSED [ 78%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_anonymous_access_rejected PASSED [ 84%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_malformed_bulk_update_payload_rejected PASSED [ 89%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_operational_strict_rbac_kill_switch PASSED [ 94%]
backend\tests\test_rbac.py::TestRBACParameterizedMatrix::test_operational_forbidden_fields_kill_switch PASSED [100%]

================== 19 passed, 1 warning in 135.27s (0:02:15) ==================
```

---

## 5. Rollback & Operational Instructions

- **Emergency Kill-Switch (Strict RBAC Bypass)**:
  Set environment variable `FEATURE_STRICT_RBAC=False` in production or deployment environment and restart backend pods/workers. This allows standard authenticated access without blocking on custom role action checks.
- **Forbidden Fields Validation Toggle**:
  Set environment variable `FEATURE_FORBIDDEN_FIELDS_ENFORCEMENT=False` to disable strict rejection of system fields if a legacy client requires sending non-mutated tenant fields.
- **Git Rollback**:
  All commits are directly maintained on `master`. A rollback can be performed via standard git revert:
  `git revert HEAD` without altering branch structure.

---

## 6. Acceptance Checklist

- [x] Parameterized role matrix implemented across endpoints and actions (`list`, `retrieve`, `create`, `update`, `destroy`, `convert`, `complete`, `bulk_update`, `bulk_delete`, `export`, `merge`).
- [x] Forbidden fields rejection: non-privileged roles modifying `organization`, `role`, `created_by`, `is_superuser` are rejected with HTTP 403 Forbidden explaining the violation.
- [x] Descriptive missing permission message returned on denial with required roles listed.
- [x] Row-level isolation enforced under pagination, search, and aggregations (`/statistics/`, `/pipeline/`).
- [x] Adversarial scenarios validated: wrong-tenant, anonymous, insufficient role, malformed payload, kill switches.
- [x] All 19 tests in `backend/tests/test_rbac.py` passing cleanly.
- [x] Verification harness `scripts/verify_rbac.py` passing all checks.
- [x] All commits retained directly on `master` without creating new branches.
