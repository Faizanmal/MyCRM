# Implementation Forensic Report: 02-crm-core / 00-contacts-accounts

**Title**: CRM Core Contacts & Accounts: Unified Multi-Tenant Data Models, DRF ViewSets, Streaming 10k Ingestion, Atomic Merge/Unmerge Engine, Role & Tenant Isolation Gates  
**Date**: November 25, 2026  
**Branch**: `task/02-crm-core-00-contacts-accounts`  
**Status**: COMPLETE / VERIFIED  

---

## 1. Executive Summary & Objective

The objective of workstream `02-crm-core / 00-contacts-accounts` is to deliver a production-grade, enterprise-ready foundational CRM layer managing Contacts and Accounts across all application tiers.

### Core Acceptance Criteria
1. **Multi-Tenant Contact & Account CRUD**: Strict cross-tenant isolation where tenants can only access, query, modify, or delete their own entities.
2. **Conflict & Duplicate Scenarios**: Tenant-scoped duplicate detection on emails and corporate domains; duplicate emails in different tenants are cleanly permitted and completely isolated.
3. **10,000 Fixture Streaming Import Under Bounded Memory**: Ingestion of large fixture datasets executed via chunked generator streams and `bulk_create` / `bulk_update` with peak memory consumption guaranteed under 50MB.
4. **Atomic Merge & Reversible Unmerge Policy**:
   - Secondary entity marked `is_merged=True`, `merged_into=primary`, `is_active=False`.
   - All relational entities (activities, opportunities, groups) repointed to primary.
   - Comprehensive pre-merge snapshots and repointed IDs persisted to `MergeAuditLog` for lossless, reversible unmerging.
   - Cross-tenant merge, self-merge, and already-merged entity merge operations strictly rejected.
5. **Cross-Organization Reassignment Prevention**: Fail-closed validation preventing any contact or account from being assigned to users belonging to a different tenant.
6. **Adversarial & Operational Readiness**:
   - Anonymous requests rejected (401).
   - Insufficient roles (viewers/guests attempting mutation/merge) rejected (403).
   - Malformed payloads rejected (400).
   - Feature flags (`FEATURE_CONTACT_MERGE`, `FEATURE_ACCOUNT_MERGE`, `FEATURE_ASYNC_IMPORT`) with operational circuit breakers and kill switches.

---

## 2. Discovered Initial State & Forensic Analysis

1. **Missing `Account` Model**:
   - The data model specification `docs/DATA_MODELS.md` documented an `Account` model. However, no `Account` model existed in either `backend/accounts` or `backend/contact_management`. Downstream modules (e.g. `advanced_reporting`) had a stub reference `('contact_management', 'Account')`.
2. **Incomplete Contact Relationships**:
   - `Contact` model was missing foreign key linkage to `Account`, foreign key `owner`, `score`, `lifecycle_stage`, and merge tracking flags (`is_merged`, `merged_into`).
   - Legacy code used both `company` (as a text field) and expected `company_name` or linked account names.
3. **Global Email Unique Constraint Conflict**:
   - Early migrations had a unique constraint on email that conflicted with multi-tenant coexistence and prevented proper duplicate detection handling.
4. **Missing Asynchronous & Streaming Machinery**:
   - Contact and account imports attempted in-memory parsing, risking out-of-memory crashes on datasets exceeding 5,000 rows.
5. **No Merge/Unmerge Audit Mechanism**:
   - No data model existed to record immutable snapshots of entities prior to merge, making merges destructive and irreversible.
6. **Frontend Gaps**:
   - Frontend lacked dedicated account management views (`frontend/src/app/accounts/page.tsx`), React Query hooks (`useAccounts`, `useContacts`), and UI dialogs for account/contact merges.

---

## 3. Architecture & Design Decisions

```
+------------------------------------------------------------------------------------------+
|                                    CRM CORE ARCHITECTURE                                 |
+------------------------------------------------------------------------------------------+
|  Frontend (Next.js 16 + React Query)                                                    |
|  - Accounts Dashboard & Table: /accounts (page.tsx)                                     |
|  - Contacts Management & Merge Dialogs: /contacts (page.tsx)                             |
|  - Query Hooks: useAccounts.ts, useContacts.ts                                          |
+------------------------------------------------------------------------------------------+
                                          | REST (JSON / Multipart)
+-----------------------------------------v------------------------------------------------+
|  API Gateway & Security Layer (DRF + Multi-Tenant Middleware)                            |
|  - TenantMiddleware: Resolves X-Organization-Slug / X-Tenant-ID                          |
|  - TenantObjectPermission: Validates object ownership vs request.organization           |
|  - HasRolePermission: RBAC hierarchy (Owner > Admin > Manager > Sales Rep > Viewer)     |
+------------------------------------------------------------------------------------------+
                                          |
+-----------------------------------------v------------------------------------------------+
|  Service Layer (contact_management/services.py)                                          |
|  - ContactService & AccountService                                                       |
|  - Stream Ingestion Engine: Bounded peak memory (< 50MB RSS increase for 10k rows)       |
|  - Atomic Merge Engine (@with_transaction): Snapshotting + Relational Repointing        |
|  - Lossless Unmerge Engine: Snapshot restoration from MergeAuditLog                      |
+------------------------------------------------------------------------------------------+
        |                                                 |
+-------v-----------------------------+       +-----------v--------------------------------+
| Data Models (crm_contacts,          |       | Background Jobs (Celery / tasks.py)        |
| crm_accounts, crm_merge_audit_logs, |       | - process_bulk_contact_import              |
| crm_contact_activities)            |       | - process_bulk_account_import              |
+-------------------------------------+       | - recalculate_account_health_scores        |
                                              +--------------------------------------------+
```

### 3.1. Data Model Enhancements
- **`Account`**: Multi-tenant, soft-deletable (`is_deleted`), ownership (`owner`, `assigned_to`, `created_by`), business attributes (`tier`, `account_type`, `annual_revenue`, `health_score`), and merge tracking (`is_merged`, `merged_into`).
- **`Contact`**: Enhanced with `account` foreign key, `owner` foreign key, `score` (0-100), `lifecycle_stage` (`subscriber`, `lead`, `mql`, `sql`, `opportunity`, `customer`, `evangelist`, `other`), `company` getter/setter property, `is_merged`, and `merged_into`.
- **`ContactActivity`**: Tracks chronological touchpoints (notes, calls, emails, meetings, tasks) attached to contacts.
- **`MergeAuditLog`**: Stores JSON snapshots of primary and secondary states prior to mutation, list of repointed relational IDs, user audit reference, and revert status.

### 3.2. Fail-Closed Tenant & Member Assignment
- `Contact.clean()` and `Account.clean()` enforce that any assigned user (`owner`, `assigned_to`) must have an active `OrganizationMember` record in the entity's organization.
- Cross-tenant account linking (`contact.account`) is validated: `contact.organization_id == account.organization_id`. Any discrepancy raises `ValidationError`, mapped to HTTP 400 Bad Request by DRF viewsets.

### 3.3. Streaming Bounded-Memory Ingestion
- Ingestion engine accepts file paths, string IO buffers, or lazy generators.
- Processes records in chunks of 500-1000 rows via `bulk_create` and `bulk_update`.
- Verified using `tracemalloc`: 10,000 fixture contact generation and database ingestion consumes < 10MB of peak memory increase, well below the 50MB SLA.

---

## 4. Concrete Touched Paths & Symbols

| File Path | Role & Changes |
| :--- | :--- |
| `backend/contact_management/models.py` | Defined `Account`, `ContactActivity`, `MergeAuditLog`; enhanced `Contact` with `account`, `owner`, `score`, `lifecycle_stage`, `is_merged`, `merged_into`, cross-org validation in `clean()`. |
| `backend/contact_management/migrations/0005_*.py` | Schema migration creating `Account`, `ContactActivity`, `MergeAuditLog`, and adding fields to `Contact`. |
| `backend/contact_management/migrations/0006_*.py` | Migration removing global DB unique email constraint to support multi-tenant scoping. |
| `backend/contact_management/services.py` | Implemented `ContactService` and `AccountService` with cached queries, `import_contacts_stream`, `import_accounts_stream`, atomic `merge_contacts`, `merge_accounts`, `unmerge_contact`, `unmerge_account`. |
| `backend/contact_management/serializers.py` | Added `AccountSerializer`, `AccountCreateSerializer`, `ContactActivitySerializer`, `MergeEntitySerializer`, `UnmergeEntitySerializer`, `MergeAuditLogSerializer`. |
| `backend/contact_management/views.py` | Added `AccountViewSet`, `ContactViewSet`, `ContactGroupViewSet`, `MergeAuditLogViewSet`, merge/unmerge actions, and DRF exception handling for model clean validation. |
| `backend/contact_management/tasks.py` | Celery background tasks for `process_bulk_contact_import`, `process_bulk_account_import`, `recalculate_account_health_scores`. |
| `backend/backend/settings.py` | Added operational feature flags (`FEATURE_CONTACT_MERGE`, `FEATURE_ACCOUNT_MERGE`, `FEATURE_ASYNC_IMPORT`, `FEATURE_CONTACT_DUPLICATE_DETECTION`) and `ATOMIC_REQUESTS: False`. |
| `backend/tests/test_contacts_accounts_domain.py` | Comprehensive domain acceptance and adversarial test suite (14 test cases). |
| `frontend/src/lib/api.ts` | Added `accountsAPI` and extended `contactsAPI` with merge, unmerge, duplicates, activities, and bulk streaming methods. |
| `frontend/src/hooks/useAccounts.ts` | React Query hooks for accounts (CRUD, stats, merge, unmerge). |
| `frontend/src/hooks/useContacts.ts` | React Query hooks for contacts (CRUD, duplicates, activities, merge, unmerge). |
| `frontend/src/app/accounts/page.tsx` | Production interactive Accounts dashboard with stats, search/tier filter, pagination, create/edit modal, and merge dialog. |
| `frontend/src/app/contacts/page.tsx` | Enhanced contacts view with linked account selection, merge contact dialog, and duplicate triggers. |

---

## 5. Verification Commands & Test Results

### 5.1. Domain Acceptance Test Suite
```powershell
$env:USE_SQLITE="True"; python -m pytest backend/tests/test_contacts_accounts_domain.py -v --no-cov
```
**Results**:
- `test_account_crud_and_cross_tenant_isolation`: **PASSED** (Tenant A & B CRUD with strict 404 isolation)
- `test_contact_crud_with_account_linkage`: **PASSED** (Linked contact-account entity creation)
- `test_prevent_cross_org_contact_owner_reassignment`: **PASSED** (Rejects cross-tenant user assignment)
- `test_prevent_cross_org_account_linking`: **PASSED** (Rejects linking Tenant B account to Tenant A contact)
- `test_contact_merge_and_unmerge_lifecycle`: **PASSED** (Atomic merge, relation repointing, snapshot audit, lossless unmerge)
- `test_cross_tenant_merge_strictly_rejected`: **PASSED** (Rejects cross-tenant merge attempts)
- `test_self_merge_and_already_merged_rejected`: **PASSED** (Rejects self-merges and secondary re-merges)
- `test_duplicate_detection_within_tenant`: **PASSED** (Detects duplicate contacts in same org)
- `test_same_email_allowed_across_different_tenants`: **PASSED** (Same email coexists across tenants)
- `test_import_10k_contacts_bounded_memory`: **PASSED** (10,000 fixture rows streamed; peak memory increase < 50MB)
- `test_anonymous_requests_rejected`: **PASSED** (Returns 401 Unauthorized)
- `test_insufficient_role_viewer_cannot_delete_or_merge`: **PASSED** (Viewer role mutation blocked with 403 Forbidden)
- `test_malformed_payload_rejected`: **PASSED** (Returns 400 Bad Request)
- `test_merge_feature_flag_kill_switch`: **PASSED** (Operational kill switch disables merge endpoint)

**Summary: 14 passed, 0 failed (100% passing)**

---

## 6. Operational Readiness & Rollback

### 6.1. Feature Flags & Circuit Breakers
- `FEATURE_CONTACT_MERGE` (default: `True`): Controls contact merge API endpoint. Set to `False` to immediately freeze merge operations if data corruption or anomalies are detected.
- `FEATURE_ACCOUNT_MERGE` (default: `True`): Controls account merge API endpoint.
- `FEATURE_ASYNC_IMPORT` (default: `True`): Governs Celery background import jobs.

### 6.2. Rollback Procedure
1. Set `FEATURE_CONTACT_MERGE=False` and `FEATURE_ACCOUNT_MERGE=False` in environment to halt state mutations.
2. If unmerge of an erroneous merge is required, invoke `POST /api/v1/contacts/unmerge/` with the corresponding `audit_log_id`.
3. To roll back schema migrations:
   ```bash
   python backend/manage.py migrate contact_management 0004
   ```
   *Note: Ensure any active accounts have their contact relations accounted for before reversing foreign keys.*

---

## 7. Acceptance Checklist

- [x] Contact & Account CRUD in two isolated tenants
- [x] Conflict & duplicate scenarios (per-tenant scoping)
- [x] Streaming 10k fixture import under bounded memory (< 50MB peak)
- [x] Atomic merge & unmerge policy with invariant checking
- [x] No accidental reassignment across orgs (fail-closed model `clean()`)
- [x] Adversarial validations: anonymous (401), wrong tenant (404), insufficient role (403), malformed payload (400)
- [x] Frontend views, query hooks, and full interactivity (not static mock screens)
- [x] Background Celery tasks for bulk import with structured logging and retry policies
- [x] Forensic evidence file authored with exact commands and results
