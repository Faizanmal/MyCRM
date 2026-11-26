# Implementation & Forensic Evidence: 01-security-tenancy / 04-uploads-webhooks

## Executive Summary
This document provides complete forensic evidence for the implementation and adversarial validation of workstream **`01-security-tenancy / 04-uploads-webhooks`** (Secure File Uploads, Signed URLs, Webhook Signature Verification, Replay Defense, and SSRF Hardening).

All six required domain-specific acceptance tests have been fully satisfied, verified with zero regressions, and committed directly to `master`.

---

## 1. Discovered Initial State

Prior to this workstream:
1. **Disguised Executable Vulnerability**:
   - `backend/document_management/models.py` had a basic `validate_file_content` function that fell back to `mimetypes.guess_type` whenever `python-magic` was missing or unconfigured.
   - An attacker could rename a Windows PE binary (`.exe`), Linux ELF binary, or malicious shell/PHP script to `.pdf`, `.docx`, or `.png`, bypassing validation completely.
2. **Document Multi-Tenant IDOR Vulnerability**:
   - The `Document` model in `document_management/models.py` lacked an `organization` (tenant) foreign key.
   - `DocumentViewSet.get_queryset()` returned `Document.objects.all()` for all authenticated users without tenant filtering.
   - Any authenticated user knowing a document UUID from another organization could inspect metadata or call `/api/documents/documents/{id}/download/` directly (IDOR).
3. **Download URL Expiration & Signed Tokens**:
   - Document downloads were only accessible via persistent URLs; time-limited cryptographically signed URLs with tamper-detection were not available for temporary access or direct frontend downloads.
4. **Outgoing Webhook & URL SSRF Vulnerability**:
   - Outgoing webhooks (`deliver_webhook` in `integration_hub/tasks.py`), custom marketplace webhooks (`WebhookBuilderService.deliver_webhook`), and workflow webhook steps (`core/workflow_services.py`) directly called `requests.post()` / `requests.request()`.
   - Users or webhook administrators could configure destinations pointing to internal loopback (`127.0.0.1`), RFC 1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), or cloud instance metadata services (`http://169.254.169.254/latest/meta-data/`), leaking cloud credentials or attacking internal services.
5. **Missing Inbound Webhook Signature & Replay Defense**:
   - The system lacked an enterprise inbound webhook receiver for third-party event delivery. There was no standardized HMAC verification, timestamp tolerance window, or event idempotency replay defense.
6. **Forged Tenant Identity Risk**:
   - External webhook payloads specifying arbitrary `tenant_id` fields could theoretically allow cross-tenant spoofing if the tenant identity was not strictly derived from the verified endpoint secret.

---

## 2. Architecture & Design Decisions

### 2.1 File Upload Security & Disguised Executable Defense (`backend/core/upload_security.py`)
- **Prohibited Extensions**: Strictly blacklists executable formats (`.exe`, `.dll`, `.so`, `.sh`, `.bat`, `.cmd`, `.ps1`, `.vbs`, `.php`, `.jsp`, `.asp`, `.cgi`, `.py`, `.pyc`, etc.).
- **Magic Byte Inspection**:
  - PE executables: flags files starting with `b"MZ"`.
  - ELF binaries: flags files starting with `b"\x7fELF"`.
  - Mach-O binaries: flags 32/64-bit Mach-O magic numbers (`\xfe\xed\xfa\xce`, `\xfe\xed\xfa\xcf`, etc.).
  - Scripts: flags shebang headers (`b"#!"`) and script tags (`<?php`, `<script`, `<%eval`).
  - Strict format verification: `.pdf` must have `%PDF-`, `.png` must start with PNG magic, `.jpg` with SOI header, `.zip`/`.docx`/`.xlsx` with `PK\x03\x04`.
  - Plaintext validation: ensures `.txt` and `.csv` contain valid UTF-8/ASCII without null bytes (`\x00`).
- **Filename Sanitization**: Cleanses filenames with `sanitize_filename` to strip directory traversal (`../`, `..\\`) and dangerous characters.

### 2.2 Multi-Tenant Organization Boundary & IDOR Prevention (`backend/document_management`)
- **Schema Migration**: Added `organization = models.ForeignKey('multi_tenant.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='documents')` to `Document` (migration `0004_document_organization.py`).
- **Automatic Boundary Inheritance**: `Document.save()` automatically resolves and persists `organization` from linked `lead`, `contact`, `opportunity`, `uploaded_by`, or `get_current_organization()`.
- **Queryset Tenant Isolation**: In `DocumentViewSet.get_queryset()`, queries are strictly filtered by `request.organization` or user's active `OrganizationMember` membership. Requests to documents belonging to other organizations return HTTP 404 (IDOR denied).

### 2.3 Cryptographically Signed URLs (`backend/core/signed_urls.py`)
- Implemented `generate_signed_download_token(document_id, user_id, expires_in_seconds=300)` and `verify_signed_download_token(token, max_age)`.
- Uses `django.core.signing.TimestampSigner` with HMAC-SHA256 signature and salt isolation.
- `DocumentViewSet.signed_url`: Generates signed URL and token with custom TTL.
- `DocumentViewSet.signed_download`: Public endpoint accepting signed tokens; rejects expired tokens with `SignatureExpired` (HTTP 403) and tampered tokens with `BadSignature` (HTTP 403).
- `DocumentShareViewSet.download`: Validates share link expiration; expired shares return HTTP 403 ("Share link has expired").

### 2.4 SSRF Protection Engine (`backend/core/ssrf_protection.py`)
- `validate_safe_url(url, allow_private=False)`:
  - Enforces `http` or `https` schemes.
  - Prohibits reserved hostnames (`localhost`, `127.0.0.1`, `metadata.google.internal`, etc.).
  - Resolves target hostnames via DNS (`socket.getaddrinfo`) and verifies that all resolved IP addresses are safe.
  - Rejects:
    - Loopback (`127.0.0.0/8`, `::1`)
    - RFC 1918 Private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
    - Link-local addresses (`169.254.0.0/16`, `fe80::/10`)
    - Cloud metadata IPs (`169.254.169.254`, `100.100.100.200`)
    - Carrier-Grade NAT (`100.64.0.0/10`)
    - Broadcast, multicast, and reserved ranges.
  - Raises `SSRFProtectionError` upon any violation.
- `safe_requests_request(method, url, **kwargs)`: Wraps requests with pre-flight DNS inspection and response hooks to detect and block redirect hops targeting private destinations.
- Integrated into:
  - `backend/integration_hub/tasks.py` (`deliver_webhook`)
  - `backend/integration_hub/marketplace_services.py` (`WebhookBuilderService.deliver_webhook`)
  - `backend/core/workflow_services.py` (`_handle_webhook_action`)
  - `backend/integration_hub/serializers.py` (`WebhookSerializer.validate_url`)

### 2.5 Secure Inbound Webhook Receiver & Tenant Isolation (`backend/integration_hub`)
- **Schema Migration**: Added `InboundWebhookEndpoint` and `InboundWebhookDelivery` (migration `0003_inboundwebhookendpoint_inboundwebhookdelivery.py`).
- **Endpoint Structure**: `POST /api/integrations/webhooks/inbound/<uuid:endpoint_id>/`.
- **HMAC Verification**: Checks `X-Webhook-Signature` against `endpoint.secret_key` using constant-time comparison `hmac.compare_digest`.
- **Replay Protection**:
  - Validates `X-Webhook-Timestamp`: rejects requests where timestamp drift exceeds `endpoint.tolerance_seconds` (default 300s) with HTTP 400.
  - Idempotency check: rejects duplicate event deliveries (`X-Webhook-ID` / nonce) with HTTP 409 Conflict.
- **Forged Tenant Identity Protection**:
  - The endpoint is permanently bound to `endpoint.organization`.
  - If incoming payload declares an arbitrary `tenant_id` or `organization_id`, the system detects the spoofing attempt, logs a critical security alert, overrides the untrusted payload tenant, and binds execution strictly to `endpoint.organization`.

---

## 3. Concrete Touched Paths

| File | Change Summary |
|---|---|
| `backend/core/upload_security.py` | New: Disguised executable detector, magic byte validator, filename sanitizer |
| `backend/core/ssrf_protection.py` | New: SSRF protection engine blocking loopback, RFC1918, link-local, cloud metadata |
| `backend/core/signed_urls.py` | New: Cryptographically signed expirable download tokens via `TimestampSigner` |
| `backend/document_management/models.py` | Modified: Integrated `validate_uploaded_file`, added `organization` tenant FK & auto-save |
| `backend/document_management/views.py` | Modified: Enforced tenant isolation in `get_queryset`, added `signed_url`, `signed_download`, and `download` share action |
| `backend/document_management/serializers.py` | Modified: Exposed `organization` in fields and read_only_fields |
| `backend/document_management/migrations/0004_document_organization.py` | New: Schema migration adding `organization` field to `Document` |
| `backend/integration_hub/models.py` | Modified: Added `InboundWebhookEndpoint` and `InboundWebhookDelivery` models |
| `backend/integration_hub/inbound_views.py` | New: Inbound webhook receiver with HMAC verification, replay defense, and tenant isolation |
| `backend/integration_hub/urls.py` | Modified: Registered `/webhooks/inbound/<uuid:endpoint_id>/` route |
| `backend/integration_hub/tasks.py` | Modified: Wrapped webhook delivery in `safe_requests_request` / SSRF protection |
| `backend/integration_hub/marketplace_services.py` | Modified: Wrapped custom webhook delivery in `safe_requests_request` |
| `backend/integration_hub/serializers.py` | Modified: Added SSRF URL validation in `WebhookSerializer.validate_url` |
| `backend/core/workflow_services.py` | Modified: Wrapped workflow webhook action in `safe_requests_request` |
| `backend/integration_hub/migrations/0003_inboundwebhookendpoint_inboundwebhookdelivery.py` | New: Schema migration for inbound webhook models |
| `frontend/src/lib/api.ts` | Modified: Added `getSignedUrl` and `downloadSigned` client methods |
| `frontend/src/app/documents/page.tsx` | Modified: Updated document download flow to utilize signed token download with fallback |
| `scripts/verify_uploads_webhooks.py` | New: Comprehensive 6-check verification harness |
| `backend/tests/test_uploads_webhooks.py` | New: Pytest suite covering all 6 domain acceptance criteria |

---

## 4. Verification Commands & Results

### 4.1 Verification Harness (`scripts/verify_uploads_webhooks.py`)
```bash
python scripts/verify_uploads_webhooks.py
```
**Output:**
```text
======================================================================
STARTING 04-UPLOADS-WEBHOOKS VERIFICATION HARNESS
======================================================================

[Check 1] Upload Disguised Executable Denied
  PASS: Disguised Windows PE executable rejected: ['Upload denied: disguised executable detected (Windows DOS/PE Executable). File content does not match extension .pdf.']
  PASS: Disguised Linux ELF binary rejected: ['Upload denied: disguised executable detected (Linux ELF Binary). File content does not match extension .docx.']
  PASS: Disguised shell script rejected: ['Upload denied: disguised executable detected (Script with Shebang Header). File content does not match extension .png.']
  PASS: Active script injection rejected: ['Upload denied: active script code detected in file content for extension .txt.']
  PASS: Legitimate PDF successfully accepted.

[Check 2] IDOR Across Orgs Denied
  PASS: User Beta retrieve of Org Alpha document denied with HTTP 404 (IDOR blocked).
  PASS: User Beta download of Org Alpha document denied with HTTP 404 (IDOR blocked).
  PASS: User Alpha can access their own organization's document (HTTP 200).

[Check 3] Expired Signed URL Denied
  PASS: Signed token verified successfully within TTL.
  PASS: SignatureExpired raised for expired token.
  PASS: BadSignature raised for tampered token.
  PASS: Expired DocumentShare download denied with HTTP 403 ('Share link has expired').

[Check 4] Internal-IP SSRF Blocked
  PASS: Blocked SSRF attempt to 127.0.0.1: Target hostname '127.0.0.1' is prohibited (SSRF blocked).
  PASS: Blocked SSRF attempt to localhost: Target hostname 'localhost' is prohibited (SSRF blocked).
  PASS: Blocked SSRF attempt to 169.254.169.254: Target URL 'http://169.254.169.254/latest/meta-data/' resolves to prohibited internal address 169.254.169.254 (SSRF blocked).
  PASS: Blocked SSRF attempt to 10.0.0.1: Target URL 'http://10.0.0.1/admin' resolves to prohibited internal address 10.0.0.1 (SSRF blocked).
  PASS: Blocked SSRF attempt to 192.168.1.1: Target URL 'http://192.168.1.1/router' resolves to prohibited internal address 192.168.1.1 (SSRF blocked).
  PASS: Blocked SSRF attempt to 172.16.0.5: Target URL 'http://172.16.0.5/api' resolves to prohibited internal address 172.16.0.5 (SSRF blocked).
  PASS: Valid external URL allowed: https://httpbin.org/status/200

[Check 5] Invalid or Replayed Webhook Denied
  PASS: Tampered/invalid HMAC signature denied with HTTP 401.
  PASS: Stale timestamp rejected with HTTP 400 (replay defense).
  PASS: Valid webhook processed successfully (HTTP 200).
  PASS: Replayed event with duplicate event ID rejected with HTTP 409 Conflict.

[Check 6] Forged Tenant Identity Ignored
  PASS: Forged tenant identity was detected, ignored, and strictly bound to endpoint organization.

======================================================================
ALL 04-UPLOADS-WEBHOOKS ACCEPTANCE CHECKS PASSED SUCCESSFULLY!
======================================================================
```

### 4.2 Pytest Suite (`backend/tests/test_uploads_webhooks.py`)
```bash
python -m pytest backend/tests/test_uploads_webhooks.py --no-cov
```
**Output:**
```text
backend\tests\test_uploads_webhooks.py::TestUploadsAndWebhooks::test_upload_disguised_executable_denied PASSED [ 16%]
backend\tests\test_uploads_webhooks.py::TestUploadsAndWebhooks::test_idor_across_orgs_denied PASSED [ 33%]
backend\tests\test_uploads_webhooks.py::TestUploadsAndWebhooks::test_expired_url_denied PASSED [ 50%]
backend\tests\test_uploads_webhooks.py::TestUploadsAndWebhooks::test_internal_ip_ssrf_blocked PASSED [ 66%]
backend\tests\test_uploads_webhooks.py::TestUploadsAndWebhooks::test_invalid_or_replayed_webhook_denied PASSED [ 83%]
backend\tests\test_uploads_webhooks.py::TestUploadsAndWebhooks::test_forged_tenant_identity_ignored PASSED [100%]

================== 6 passed, 1 warning in 111.82s (0:01:51) ===================
```

---

## 5. Acceptance Matrix Checklist

| Requirement | Acceptance Criteria | Result | Implementation Details |
|---|---|---|---|
| **Disguised Executable** | Upload disguised executable denied | **PASS** | `backend/core/upload_security.py`: Inspects binary headers (`MZ`, `\x7fELF`, Mach-O, scripts). |
| **Cross-Org IDOR** | IDOR across orgs denied | **PASS** | `Document.organization` FK + `DocumentViewSet.get_queryset` tenant scoping returning 404. |
| **Expired URLs** | Expired URL denied | **PASS** | `backend/core/signed_urls.py`: `TimestampSigner` expiration + `DocumentShare.is_expired` 403. |
| **SSRF Protection** | Internal-IP SSRF blocked | **PASS** | `backend/core/ssrf_protection.py`: Blocks 127.0.0.1, localhost, RFC 1918, and 169.254.169.254. |
| **Webhook Replay & Sig** | Invalid or replayed webhook denied | **PASS** | `backend/integration_hub/inbound_views.py`: HMAC-SHA256 verification + timestamp drift tolerance + event ID idempotency (409). |
| **Tenant Forgery** | Forged tenant identity ignored | **PASS** | `InboundWebhookReceiverView`: Overrides untrusted payload `tenant_id` to bound endpoint tenant. |

---

## 6. Operational Readiness & Rollback Instructions

### 6.1 Logging & Observability
- All SSRF violations emit `WARNING` logs containing the blocked hostname and resolved prohibited IP address.
- All webhook signature failures emit `WARNING` logs.
- All forged tenant identity injection attempts emit `CRITICAL` audit logs:
  `SECURITY ALERT: Inbound webhook on endpoint <uuid> received forged tenant ID '<forged_id>' (bound organization is '<org_id>'). Overriding untrusted payload tenant.`

### 6.2 Operational Feature Flags (`backend/backend/settings.py`)
- `FEATURE_STRICT_UPLOAD_VALIDATION` (default: `True`): Toggles magic byte and disguised executable validation for uploads.
- `FEATURE_SSRF_PROTECTION` (default: `True`): Toggles egress filtering against private/loopback/cloud metadata destinations.
- `FEATURE_INBOUND_WEBHOOK_VERIFICATION` (default: `True`): Toggles strict HMAC-SHA256 signature verification for inbound webhooks.

### 6.3 Rollback Instructions
If a rollback is required:
1. Revert Git commit: `git revert HEAD`
2. Reverse database migrations:
   ```bash
   python backend/manage.py migrate integration_hub 0002
   python backend/manage.py migrate document_management 0003
   ```
3. Restart backend workers and Daphne server.
