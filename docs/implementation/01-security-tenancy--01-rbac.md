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
3. **Lack of Row-Level Isolation Under List & Pagination**:
   - Members and sales representatives could see all records belonging to their organization on `list` and search endpoints, rather than being restricted to records assigned to or owned by them.
4. **Data Exfiltration via Bulk Export**:
   - `CSVExportView` did not gate export capabilities by role, allowing low-privilege viewers or guests to exfiltrate entire tenant datasets.
5. **Frontend/Backend Role Discrepancies**:
   - The frontend RBAC type definitions (`Role = 'admin' | 'manager' | 'sales_rep' | 'viewer' | 'guest'`) lacked alignment with backend tenant membership roles (`owner`, `admin`, `manager`, `member`, `guest`).

---

## 2. Architecture Decisions & Implementation

### 2.1 Granular `HasRolePermission` Implementation (`backend/multi_tenant/permissions.py`)
- Built a reusable, parameterized permission class enforcing:
  - **Role Hierarchy**: `Owner (50) > Admin (40) > Manager (30) > Member/SalesRep (20) > Viewer/Guest (10)`.
  - **Action-to-Role Matrix**:
    - **Read (`list`, `retrieve`, `statistics`, `pipeline`)**: `['owner', 'admin', 'manager', 'member', 'sales_rep', 'viewer']`
    - **Create & Mutate (`create`, `update`, `partial_update`, `convert`, `complete`)**: `['owner', 'admin', 'manager', 'member', 'sales_rep']`
    - **Destructive & Bulk Mutation (`destroy`, `bulk_update` [action='update'], `import`, `export`)**: `['owner', 'admin', 'manager']`
    - **High-Risk Bulk Deletion (`bulk_update` [action='delete'])**: `['owner', 'admin']` only.
  - **Descriptive 403 Forbidden Explanations**: Returns exact details on missing permissions (e.g. `Insufficient permissions: Role 'viewer' cannot perform action 'create'.`).
  - **Row-Level Ownership Validation**: Enforces that `member` and `sales_rep` roles can only mutate objects where `owner_id == request.user.id`, `assigned_to_id == request.user.id`, or `created_by_id == request.user.id`.

### 2.2 Row-Level Scoping in Querysets (`backend/api/v1/views.py`)
- Configured `get_queryset()` in `LeadViewSet`, `ContactViewSet`, `OpportunityViewSet`, and `TaskViewSet`:
  - When the requester has role `member` or `sales_rep`, querysets automatically filter to records owned by or assigned to `request.user`.
  - Organization admins, owners, and managers retain organization-wide visibility.

### 2.3 Import/Export Role Hardening (`backend/api/v1/import_export.py`)
- Tagged `CSVImportView` (`action = 'import'`) and `CSVExportView` (`action = 'export'`) with `HasRolePermission`.
- Unauthorized requests from `viewer`, `guest`, or standard `member` are denied with `403 Forbidden`.

### 2.4 Frontend Role Hierarchy Synchronization (`frontend/src/lib/rbac.tsx`)
- Updated `Role` union type to include `'owner'` and `'member'`.
- Updated `roleHierarchy` to align with backend permission weights (`owner: 5, admin: 4, manager: 3, member: 2, sales_rep: 2, viewer: 1, guest: 0`).
- Configured permissions for `member` and `owner` roles across frontend route and feature guards.

---

## 3. Concrete Touched Paths

- `backend/multi_tenant/permissions.py`
- `backend/api/v1/views.py`
- `backend/api/v1/import_export.py`
- `frontend/src/lib/rbac.tsx`
- `scripts/verify_rbac.py`
- `backend/tests/test_rbac.py`
- `docs/implementation/01-security-tenancy--01-rbac.md`

---

## 4. Verification Evidence

### Harness: `scripts/verify_rbac.py`
```
======================================================================
STARTING 01-RBAC PARAMETERIZED VERIFICATION SUITE
======================================================================

[Check 1] Read Matrix & Row-Level Filtering Under List
  PASS: Owner, Admin, Manager have organization-wide visibility.
  PASS: Member/SalesRep row-level isolation verified in list/pagination.
  PASS: Viewer allowed read access.

[Check 2] Mutation Permissions Matrix (Create, Update)
  PASS: Viewer rejected on create with descriptive permission message.
  PASS: Member successfully created lead.
  PASS: Member successfully updated own lead.
  PASS: Member forbidden from updating unassigned/other leads.

[Check 3] Parameterized Bulk Update vs Bulk Delete
  PASS: Member rejected from bulk_update.
  PASS: Manager allowed bulk_update (action=update).
  PASS: Manager rejected from bulk delete with descriptive permission message.
  PASS: Admin allowed bulk delete.

[Check 4] Import/Export Role Boundaries
  PASS: Viewer rejected on export.
  PASS: Member rejected on export.
  PASS: Manager allowed on export.

======================================================================
ALL 01-RBAC PARAMETERIZED CHECKS PASSED SUCCESSFULLY!
======================================================================
```
Result: **100% Passed**.
