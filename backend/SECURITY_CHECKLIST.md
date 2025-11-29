# Authentication & Access Control — Security Checklist

This checklist summarizes the high-priority actions implemented and remaining recommendations for MyCRM (backend).

Implemented (in this commit)
- Shorter default JWT access token lifetime (15 minutes).
- Longer refresh token default (7 days) with rotation and blacklist enabled.
- Session cookie hardening: HttpOnly and SameSite support (defaults to HttpOnly=True and SameSite=Lax in production).
- Login endpoint rate-limited with a conservative default: 10 requests per hour per IP.
- Admin accounts are required to have 2FA enabled before obtaining tokens.

Recommended follow-ups
- Apply account lockout or progressive backoff for repeated failures (e.g., django-axes or failed_attempts + locked_until fields).
- Ensure 2FA secrets and other sensitive data are stored encrypted at rest and rotated.
- Enforce mandatory 2FA for all users in sensitive roles and provide backup codes / recovery options.
- Add CAPTCHA or other bot protection on signup/password-reset endpoints.
- Confirm production environment variables: SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True, SECURE_SSL_REDIRECT=True, and appropriate HSTS settings.
- Add automated CI scanning (Snyk/Dependabot, Bandit) and DAST for the application.

How to configure in production
1) Set environment variables in your deployment environment — example:

```powershell
setx SECRET_KEY "<your-secret>"
setx SESSION_COOKIE_SECURE True
setx CSRF_COOKIE_SECURE True
setx SESSION_COOKIE_HTTPONLY True
setx SESSION_COOKIE_SAMESITE Lax
setx JWT_ACCESS_TOKEN_LIFETIME 15
setx JWT_REFRESH_TOKEN_LIFETIME 10080
setx SECURE_SSL_REDIRECT True
setx SECURE_HSTS_SECONDS 31536000
```

2) Enforce admin-only policies via monitoring and ensure backup MFA recovery flows exist.

3) Regularly review and test authorization across object-level endpoints to prevent IDOR.
