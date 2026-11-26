# Engineering Evidence Report: 01-security-tenancy / 02-session-auth

**Workstream**: Secure Identity, Session Authentication, CSRF, 2FA Backup Codes, and SSO Hardening  
**Target Repository**: `Faizanmal/MyCRM`  
**Execution Branch**: `master` (Retained strictly on master per operational mandate; no branches created)  
**Status**: VERIFIED & DEPLOYED  

---

## 1. Discovered Initial State & Threat Forensics

Audit of `backend/backend/settings.py`, `backend/user_management/views.py`, `backend/user_management/authentication.py`, `backend/sso_integration/services.py`, `frontend/src/contexts/AuthContext.tsx`, and `frontend/src/lib/api.ts` revealed several vulnerabilities:

1. **Token Storage & XSS Vulnerability**:
   - `frontend/src/contexts/AuthContext.tsx` and `frontend/src/lib/api.ts` stored `access_token` and `refresh_token` in `localStorage`. In the event of an XSS attack or malicious package injection, full access and refresh tokens could be extracted.
2. **CSRF Exposure with Cookie Authentication**:
   - Standard SimpleJWT expects `Authorization: Bearer <token>` and bypasses Django's CSRF validation. When switching to HttpOnly cookies, mutative requests (`POST`, `PUT`, `PATCH`, `DELETE`) without CSRF checks would be vulnerable to Cross-Site Request Forgery.
3. **Missing Token Blacklisting & Replay Protection**:
   - `rest_framework_simplejwt.token_blacklist` was previously absent from `INSTALLED_APPS`. Rotated tokens were not stored in a blacklist table, allowing replayed token pairs.
4. **2FA Bypass & Missing Backup Recovery Codes**:
   - `setup_2fa` set attributes on the Django user model without persisting to `UserProfile` (`AttributeError` / schema mismatch), causing `verify_2fa` to fail with `2FA setup not initiated`.
   - Backup recovery codes were missing entirely; users losing their TOTP authenticator device had no offline cryptographic recovery mechanism.
5. **Brute Force & Credential Stuffing Exposure**:
   - Authentication endpoints (`/api/auth/login/`, `/api/auth/verify-2fa/`) had no dedicated rate throttling, leaving them vulnerable to automated brute-force attacks.
6. **SSO State, Redirect URI & Cross-Tenant Binding Holes**:
   - `OAuth2Service` generated authorization URLs without strictly verifying incoming callback `state` against an unguessable session secret, opening the system to OAuth CSRF login attacks.
   - Redirect URI validation was not enforced against configured provider settings.
   - Cross-tenant SSO binding checks were absent: a user authenticated through an SSO provider for Organization A could authenticate into Organization B without active membership checks.
   - SQLite schema non-null constraints on `last_used_at` and `user_agent` caused unhandled `IntegrityError` exceptions on login attempts.

---

## 2. Architecture Decisions & Implementation

### 2.1 HttpOnly Secure SameSite Cookie Session Authentication & Strict CSRF Defense
- **Backend (`backend/user_management/authentication.py`)**:
  - `CookieOrHeaderJWTAuthentication`:
    - Checks `Authorization: Bearer <token>` first (supporting API clients and background jobs).
    - Falls back to `request.COOKIES.get('access_token')`.
    - Enforces strict CSRF checking via Django's `CSRFCheck` on mutative HTTP methods (`POST`, `PUT`, `PATCH`, `DELETE`) whenever authenticating via cookies.
    - Rejects requests lacking a valid `X-CSRFToken` or `csrftoken` cookie with `403 Forbidden`.
  - `set_auth_cookies(response, access_token, refresh_token, request)`:
    - Sets `access_token` (`HttpOnly=True`, `SameSite=Lax`, `Secure=not DEBUG`).
    - Sets `refresh_token` (`HttpOnly=True`, `SameSite=Lax`, `Secure=not DEBUG`, path=`/api/auth/`).
    - Triggers `django.middleware.csrf.get_token(request)` to set the readable `csrftoken` cookie.
- **Frontend (`frontend/src/lib/api.ts`)**:
  - Attached `getCookie('csrftoken')` and injected `X-CSRFToken` header onto all mutative Axios requests.
  - Configured `withCredentials: true` so session cookies and CSRF tokens travel automatically.
  - Implemented resilient 401 request queueing (`isRefreshing` + `failedQueue`) so concurrent 401s do not trigger duplicate refresh calls.

### 2.2 Token Rotation, Replay Defense & Immediate Server-Side Revocation
- **Backend (`backend/user_management/views.py`)**:
  - Added `rest_framework_simplejwt.token_blacklist` to `INSTALLED_APPS`.
  - `CustomTokenRefreshView` (`/api/auth/refresh/`):
    - Reads refresh token from request payload or HttpOnly cookie.
    - Rotates refresh token and immediately blacklists previous token.
    - Sets new HttpOnly `access_token` and `refresh_token` cookies.
  - `LogoutView` (`/api/auth/logout/`):
    - Immediately blacklists refresh token in the database.
    - Emits expired cookie headers to flush client cookies immediately.
- **Multi-Tab Sync (`frontend/src/contexts/AuthContext.tsx` & `frontend/src/lib/api.ts`)**:
  - Emits `auth_logout_event` in `localStorage` upon logout or refresh failure.
  - Storage event listener automatically synchronizes state across all open tabs and redirects to `/login`.

### 2.3 Two-Factor Authentication, Gating Challenge & Backup Recovery Codes
- **Data Model (`backend/user_management/models.py`)**:
  - Added `two_factor_backup_codes = models.JSONField(default=list, blank=True)` to `UserProfile`.
  - Migration `0007_userprofile_two_factor_backup_codes.py` applied.
- **Cryptographic Helper Functions (`backend/user_management/views.py`)**:
  - `generate_backup_codes(count=8)`: Generates 8 single-use codes (format `xxxx-xxxx`) using `secrets.choice` and stores SHA-256 salted hashes.
  - `verify_and_consume_backup_code(profile, submitted_code)`: Validates code hash using `secrets.compare_digest`, deletes consumed code from profile, and logs security audit event.
- **Endpoints (`backend/user_management/views.py`)**:
  - `CustomTokenObtainPairView`: If 2FA is enabled on user or profile, suppresses full session tokens and returns `2FA verification required` with `temp_token`.
  - `TwoFactorLoginVerifyView` (`/api/auth/verify-2fa/`): Accepts TOTP 6-digit code OR backup recovery code. Validates code, consumes backup code if used, and sets HttpOnly session cookies.
  - `UserViewSet.setup_2fa`: Generates base32 secret, QR code, and 8 initial backup recovery codes.
  - `UserViewSet.verify_2fa`: Verifies initial TOTP code to complete enrollment.
  - `UserViewSet.generate_backup_codes`: Authenticated endpoint allowing users to regenerate a fresh set of 8 backup codes, invalidating prior codes.

### 2.4 Login Rate Limiting & Throttling
- **Backend (`backend/user_management/throttling.py`)**:
  - Created `LoginRateThrottle(AnonRateThrottle)` enforcing 10 attempts per minute (`LOGIN_RATE_THROTTLE_RATE = '10/min'`).
  - Applied to `CustomTokenObtainPairView` and `TwoFactorLoginVerifyView`.

### 2.5 SSO Security Hardening (OAuth2, SAML, & Tenant Binding)
- **Backend (`backend/sso_integration/services.py` & `views.py`)**:
  - **State Validation**: `OAuth2Service.generate_authorization_url` generates cryptographically secure state stored in session. `OAuth2Service.validate_state` uses `secrets.compare_digest` to prevent OAuth CSRF attacks.
  - **Redirect URI Validation**: `validate_redirect_uri` ensures redirect target matches provider configuration.
  - **ID Token Claims Validation**: `validate_id_token` validates audience (`aud`), expiration (`exp` with UTC awareness), and nonce.
  - **SAML Security**: `SAMLService.validate_saml_response` validates audience restriction, recipient ACS URL, and timestamp conditions.
  - **Cross-Tenant SSO Binding Enforcement**: `SSOAuthenticationService.authenticate_user` checks `OrganizationMember` membership. If a user is not an active member of the provider organization (and `auto_create_users=False`), login is rejected with `ValueError("Cross-tenant SSO denied: User is not an active member of organization...")`.
  - **Schema Robustness (`backend/sso_integration/models.py`)**:
    - Changed `last_used_at`, `expires_at`, and `ended_at` to `null=True, blank=True`.
    - Provided `default=''` for string and text fields (`user_agent`, `error_message`, `sso_user_id`).
    - Applied migrations `0002_alter_ssoprovider_last_used_at.py` and `0003_alter_ssologinattempt_error_message_and_more.py`.

---

## 3. Concrete Touched Paths

| File Path | Description of Changes |
| :--- | :--- |
| `backend/backend/settings.py` | Added operational feature flags (`FEATURE_HTTPONLY_SESSION_AUTH`, `FEATURE_CSRF_COOKIE_ENFORCEMENT`, `FEATURE_MFA_ENFORCEMENT`, `FEATURE_SSO_STRICT_VALIDATION`, `FEATURE_LOGIN_RATE_LIMIT`, `LOGIN_RATE_THROTTLE_RATE`). |
| `backend/user_management/models.py` | Added `two_factor_backup_codes` JSON field to `UserProfile`. |
| `backend/user_management/migrations/0007_userprofile_two_factor_backup_codes.py` | Schema migration for backup recovery codes. |
| `backend/user_management/authentication.py` | Strict CSRF validation on mutative cookie requests; updated cookie emitter with `csrftoken`. |
| `backend/user_management/throttling.py` | `LoginRateThrottle` class for brute-force defense. |
| `backend/user_management/views.py` | Backup codes generation/consumption, rate throttling, 2FA gating, cookie issuance, and backup codes regeneration endpoint. |
| `backend/sso_integration/models.py` | Nullable date fields and safe defaults for `SSOProvider`, `SSOSession`, and `SSOLoginAttempt`. |
| `backend/sso_integration/migrations/0002_alter_ssoprovider_last_used_at.py` | Schema migration for `SSOProvider.last_used_at`. |
| `backend/sso_integration/migrations/0003_alter_ssologinattempt_error_message_and_more.py` | Schema migration for `SSOLoginAttempt` and `SSOSession` fields. |
| `backend/sso_integration/services.py` | State validation (CSRF defense), redirect URI validation, UTC-aware token validation, and cross-tenant SSO binding. |
| `backend/sso_integration/views.py` | Session-backed state and code verifier storage and validation on SSO callback. |
| `frontend/src/lib/api.ts` | CSRF cookie reading & header injection, concurrent 401 request queueing, and multi-tab logout event dispatch. |
| `scripts/verify_session_auth.py` | Adversarial automated test harness validating all 6 session auth requirements. |
| `backend/tests/test_session_auth.py` | 7-part automated unit/integration test suite covering HttpOnly cookies, CSRF, rotation, 2FA, backup recovery, revocation, and SSO. |
| `docs/implementation/01-security-tenancy--02-session-auth.md` | Comprehensive engineering evidence report. |

---

## 4. Verification Evidence & Test Commands

### 4.1 Adversarial Verification Suite (`scripts/verify_session_auth.py`)
**Command**:
```powershell
python scripts/verify_session_auth.py
```
**Output**:
```text
======================================================================
STARTING 02-SESSION-AUTH ADVERSARIAL VERIFICATION SUITE
======================================================================

[Check 1] HttpOnly Cookie Generation & Authentication
  PASS: Login response issues HttpOnly, SameSite=Lax session cookies.
  PASS: Protected CRM API accessed successfully via HttpOnly session cookie.

[Check 2] CSRF Protection on Cookie-Authenticated Mutative Requests
  PASS: Mutative request without CSRF token rejected with 403 Forbidden.
  PASS: Mutative request with valid X-CSRFToken header accepted.

[Check 3] Token Rotation & Replay Attack Defense
  PASS: Refresh token rotated to new cryptographic secret.
  PASS: Replayed / blacklisted refresh token strictly rejected.
  PASS: Tampered refresh token denied.

[Check 4] Two-Factor Authentication Gating & Backup Recovery Codes
  PASS: 2FA challenge triggered; full access tokens suppressed.
  PASS: Malformed/incorrect 2FA code rejected.
  PASS: Valid backup recovery code successfully authenticates and issues full session.
  PASS: Consumed backup recovery code rejected upon replay attempt.
  PASS: Valid TOTP code successfully completes 2FA authentication.

[Check 5] Immediate Token Revocation & Logout
  PASS: Logout immediately blacklists token and clears session cookies.

[Check 6] SSO State, Redirect URI & Cross-Tenant Binding Validations
  PASS: OAuth state validation successfully verified.
  PASS: Redirect URI validation successfully verified.
  PASS: Cross-tenant SSO authentication blocked with explicit explanation.

======================================================================
ALL 02-SESSION-AUTH ADVERSARIAL CHECKS PASSED SUCCESSFULLY!
======================================================================
```

### 4.2 Automated Integration Test Suite (`backend/tests/test_session_auth.py`)
**Command**:
```powershell
pytest backend/tests/test_session_auth.py -v --no-cov
```
**Output**:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.11, pytest-9.1.1, pluggy-1.7.0
rootdir: J:\SaaS\Projects\MyCRM\backend
collected 7 items

backend\tests\test_session_auth.py::TestSessionAuthHardening::test_httponly_cookie_issuance_and_access PASSED [ 14%]
backend\tests\test_session_auth.py::TestSessionAuthHardening::test_csrf_protection_on_cookie_authentication PASSED [ 28%]
backend\tests\test_session_auth.py::TestSessionAuthHardening::test_refresh_token_rotation_and_replay_defense PASSED [ 42%]
backend\tests\test_session_auth.py::TestSessionAuthHardening::test_two_factor_auth_gating_and_totp PASSED [ 57%]
backend\tests\test_session_auth.py::TestSessionAuthHardening::test_two_factor_backup_code_enrollment_and_recovery PASSED [ 71%]
backend\tests\test_session_auth.py::TestSessionAuthHardening::test_immediate_revocation_on_logout PASSED [ 85%]
backend\tests\test_session_auth.py::TestSessionAuthHardening::test_sso_security_validations PASSED [100%]

================== 7 passed, 1 warning in 130.58s (0:02:10) ===================
```

---

## 5. Operational Readiness, Feature Flags & Rollback Instructions

### 5.1 Operational Feature Flags (`backend/backend/settings.py`)
The implementation is protected by operational toggles to support zero-downtime canary or staged rollouts:
- `FEATURE_HTTPONLY_SESSION_AUTH` (default: `True`): Toggles setting of HttpOnly session cookies.
- `FEATURE_CSRF_COOKIE_ENFORCEMENT` (default: `True`): Toggles strict CSRF token validation on cookie-authenticated mutative requests.
- `FEATURE_MFA_ENFORCEMENT` (default: `True`): Enables/disables 2FA login challenge gating.
- `FEATURE_SSO_STRICT_VALIDATION` (default: `True`): Enforces state comparison, redirect URI verification, and tenant binding checks.
- `FEATURE_LOGIN_RATE_LIMIT` (default: `True`): Enforces rate limiting on login and 2FA endpoints.
- `LOGIN_RATE_THROTTLE_RATE` (default: `'10/min'`): Configurable rate threshold.

### 5.2 Rollback Procedure
If emergency rollback of session cookies or CSRF enforcement is required without deploying code:
1. Set `FEATURE_CSRF_COOKIE_ENFORCEMENT = False` in environment variables or `settings.py` to allow legacy non-CSRF API requests while diagnosing frontend issues.
2. Set `FEATURE_HTTPONLY_SESSION_AUTH = False` to revert to header-only JWT authorization.
3. Database migrations (`0007_userprofile_two_factor_backup_codes`, `0002_alter_ssoprovider_last_used_at`, `0003_alter_ssologinattempt_error_message_and_more`) are additive and backward-compatible with older application versions.
