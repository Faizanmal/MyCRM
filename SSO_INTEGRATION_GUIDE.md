# SSO Integration Guide

## Overview

The SSO Integration feature provides enterprise-grade Single Sign-On capabilities for your MyCRM application. It supports both OAuth 2.0 and SAML 2.0 protocols, allowing your users to authenticate using their existing corporate credentials from providers like Google, Microsoft, Okta, and more.

## Architecture

### Components

1. **SSOProvider Model**: Stores SSO provider configurations (OAuth2/SAML)
2. **SSOSession Model**: Tracks active SSO login sessions
3. **SSOLoginAttempt Model**: Audit log for all SSO authentication attempts
4. **OAuth2Service**: Handles OAuth2 authentication flows with PKCE
5. **SAMLService**: Handles SAML 2.0 authentication flows
6. **SSOAuthenticationService**: Coordinates authentication and user management
7. **Frontend UI**: React-based configuration interface

### Supported Providers

#### OAuth 2.0 Providers
- **Google OAuth2**: Google Workspace accounts
- **Microsoft OAuth2**: Azure AD / Microsoft 365 accounts
- **GitHub OAuth2**: GitHub organization accounts
- **Okta OAuth2**: Okta OAuth2 flow

#### SAML 2.0 Providers
- **Okta SAML**: Okta SAML 2.0
- **OneLogin SAML**: OneLogin SAML 2.0
- **Azure AD SAML**: Microsoft Azure AD SAML
- **Custom SAML**: Any SAML 2.0 compliant identity provider

## Installation & Setup

### 1. Run Setup Script

```bash
cd /workspaces/MyCRM
./setup_sso_integration.sh
```

This will:
- Create database migrations
- Apply migrations
- Create 3 sample SSO providers (Google, Microsoft, Okta)

### 2. Configure Django Settings

The following settings are already configured in `backend/settings.py`:

```python
# SSO Configuration
BASE_URL = 'http://localhost:8000'  # Your backend URL
FRONTEND_URL = 'http://localhost:3000'  # Your frontend URL
SSO_SESSION_TIMEOUT = 3600  # Session timeout in seconds (1 hour)
```

Update these values for production:

```python
BASE_URL = 'https://api.mycrm.com'
FRONTEND_URL = 'https://app.mycrm.com'
SSO_SESSION_TIMEOUT = 28800  # 8 hours
```

### 3. URL Configuration

SSO endpoints are available at:
- `/api/v1/sso/providers/` - Provider management
- `/api/v1/sso/sessions/` - Session management
- `/api/v1/sso/attempts/` - Audit log
- `/api/v1/sso/callback/{provider-id}/` - OAuth2 callback endpoint

## Configuration

### OAuth2 Provider Setup

#### 1. Create Provider in Identity Provider

**Google Cloud Console:**
1. Go to https://console.cloud.google.com/
2. Create new project or select existing
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Authorized redirect URIs: `http://localhost:8000/api/v1/sso/callback/{provider-id}/`
7. Copy Client ID and Client Secret

**Microsoft Azure AD:**
1. Go to https://portal.azure.com/
2. Azure Active Directory → App registrations → New registration
3. Redirect URI: `http://localhost:8000/api/v1/sso/callback/{provider-id}/`
4. Certificates & secrets → New client secret
5. API permissions → Add "User.Read" permission
6. Copy Application (client) ID and client secret

**GitHub:**
1. Go to https://github.com/settings/developers
2. OAuth Apps → New OAuth App
3. Authorization callback URL: `http://localhost:8000/api/v1/sso/callback/{provider-id}/`
4. Copy Client ID and Client Secret

#### 2. Configure in MyCRM

Navigate to http://localhost:3000/sso-settings and click "Add Provider":

```javascript
// Example OAuth2 Configuration
{
  "provider_type": "oauth2_google",
  "provider_name": "Google Workspace",
  "status": "testing",
  "client_id": "123456789-abc.apps.googleusercontent.com",
  "client_secret": "your-client-secret",
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
  "token_url": "https://oauth2.googleapis.com/token",
  "user_info_url": "https://www.googleapis.com/oauth2/v1/userinfo",
  "scope": "openid profile email",
  "auto_create_users": true,
  "auto_update_user_info": true,
  "default_role": "member",
  "required_domains": ["company.com"]
}
```

### SAML 2.0 Provider Setup

#### 1. Configure Service Provider (SP) Metadata

Your SP metadata URL: `http://localhost:8000/api/v1/sso/providers/{provider-id}/metadata/`

SP Entity ID: `https://mycrm.com/saml/metadata`

Assertion Consumer Service (ACS) URL: `http://localhost:8000/api/v1/sso/saml/acs/`

#### 2. Get Identity Provider (IdP) Metadata

**Okta:**
1. Go to Okta Admin Console
2. Applications → Create App Integration → SAML 2.0
3. Single sign on URL: `http://localhost:8000/api/v1/sso/saml/acs/`
4. Audience URI (SP Entity ID): `https://mycrm.com/saml/metadata`
5. Download IdP metadata XML
6. Extract SSO URL and X.509 certificate

**Azure AD:**
1. Azure Active Directory → Enterprise applications → New application
2. Create your own application → SAML
3. Basic SAML Configuration:
   - Identifier (Entity ID): `https://mycrm.com/saml/metadata`
   - Reply URL (ACS URL): `http://localhost:8000/api/v1/sso/saml/acs/`
4. Download Federation Metadata XML
5. Extract Single Sign-On Service URL and certificate

#### 3. Configure in MyCRM

```javascript
// Example SAML Configuration
{
  "provider_type": "saml_okta",
  "provider_name": "Okta SAML",
  "status": "testing",
  "entity_id": "https://mycrm.com/saml/metadata",
  "sso_url": "https://your-domain.okta.com/app/appid/sso/saml",
  "slo_url": "https://your-domain.okta.com/app/appid/slo/saml",
  "x509_cert": "-----BEGIN CERTIFICATE-----\nMIIDpDCCAoyg...\n-----END CERTIFICATE-----",
  "attribute_mapping": {
    "email": "mail",
    "first_name": "givenName",
    "last_name": "sn"
  },
  "auto_create_users": true,
  "auto_update_user_info": true,
  "default_role": "member"
}
```

## API Reference

### Provider Management

#### List Providers
```bash
GET /api/v1/sso/providers/
```

Response:
```json
[
  {
    "id": "uuid",
    "provider_name": "Google Workspace",
    "provider_type": "oauth2_google",
    "status": "active",
    "is_active": true,
    "total_logins": 156,
    "last_used_at": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Create Provider
```bash
POST /api/v1/sso/providers/
Content-Type: application/json

{
  "provider_type": "oauth2_google",
  "provider_name": "Google Workspace",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
  "token_url": "https://oauth2.googleapis.com/token",
  "user_info_url": "https://www.googleapis.com/oauth2/v1/userinfo",
  "scope": "openid profile email",
  "auto_create_users": true,
  "default_role": "member",
  "required_domains": ["company.com"]
}
```

#### Test Connection
```bash
POST /api/v1/sso/providers/{id}/test_connection/
```

Response (OAuth2):
```json
{
  "status": "success",
  "message": "OAuth2 provider configuration is valid",
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "test_mode": true
}
```

#### Activate Provider
```bash
POST /api/v1/sso/providers/{id}/activate/
```

#### Deactivate Provider
```bash
POST /api/v1/sso/providers/{id}/deactivate/
```

#### Get Statistics
```bash
GET /api/v1/sso/providers/{id}/statistics/
```

Response:
```json
{
  "total_logins": 156,
  "successful_logins": 148,
  "failed_logins": 8,
  "unique_users": 42,
  "last_login_at": "2024-01-15T10:30:00Z",
  "avg_logins_per_day": 5.2,
  "recent_attempts": [...]
}
```

### Session Management

#### List Sessions
```bash
GET /api/v1/sso/sessions/
```

#### My Sessions
```bash
GET /api/v1/sso/sessions/my_sessions/
```

#### End Session
```bash
POST /api/v1/sso/sessions/{id}/end_session/
```

### Audit Log

#### List Login Attempts
```bash
GET /api/v1/sso/attempts/
GET /api/v1/sso/attempts/?provider={provider-id}
GET /api/v1/sso/attempts/?status=failed
```

## Authentication Flow

### OAuth 2.0 Flow with PKCE

1. **User clicks "Sign in with Google"**
   - Frontend calls backend to get authorization URL
   - Backend generates code_verifier and code_challenge (PKCE)
   - Returns authorization URL with state parameter

2. **User redirects to IdP**
   - User authenticates with identity provider
   - Grants permission to access profile

3. **IdP redirects to callback**
   - GET `/api/v1/sso/callback/{provider-id}/?code=...&state=...`
   - Backend exchanges code for tokens using code_verifier
   - Fetches user info from IdP

4. **User creation/authentication**
   - Backend maps IdP attributes to user fields
   - Creates user if `auto_create_users=true` and user doesn't exist
   - Updates user info if `auto_update_user_info=true`
   - Validates email domain against `required_domains`

5. **Session creation**
   - Creates SSOSession record
   - Logs in user (creates Django session)
   - Redirects to frontend dashboard

6. **Audit logging**
   - All attempts logged in SSOLoginAttempt
   - Tracks success/failure, IP, user agent, errors

### SAML 2.0 Flow

1. **User clicks "Sign in with Okta"**
   - Frontend calls backend to get SAML AuthnRequest
   - Backend generates signed SAML request
   - Returns SAML request and SSO URL

2. **User redirects to IdP**
   - SAML request POSTed to IdP SSO URL
   - User authenticates with identity provider

3. **IdP POSTs SAML Response**
   - POST `/api/v1/sso/saml/acs/`
   - Backend validates SAML response signature
   - Extracts SAML assertions and attributes

4. **User creation/authentication**
   - Maps SAML attributes using `attribute_mapping`
   - Creates/updates user as in OAuth2 flow

5. **Session creation**
   - Creates SSOSession with session_index and name_id
   - Supports Single Logout (SLO)

## User Management

### Auto-Create Users

When `auto_create_users=true`:
- Users are automatically created on first SSO login
- User fields populated from SSO attributes
- User added to organization with `default_role`
- Email is required and used as username

### Role Assignment

Default roles for auto-created users:
- `viewer`: Read-only access
- `member`: Standard user access
- `manager`: Team management access
- `admin`: Organization administration
- `owner`: Full control (cannot be auto-assigned)

### Domain Restrictions

`required_domains` field enforces email domain restrictions:

```python
"required_domains": ["company.com", "subsidiary.com"]
```

Only users with emails ending in these domains can authenticate.

### Attribute Mapping

Map SSO attributes to user fields:

**OAuth2 (Google):**
```json
{
  "email": "email",
  "first_name": "given_name",
  "last_name": "family_name",
  "picture": "picture"
}
```

**SAML (Okta):**
```json
{
  "email": "mail",
  "first_name": "givenName",
  "last_name": "sn",
  "department": "department"
}
```

## Security Features

### OAuth2 PKCE

All OAuth2 flows use PKCE (Proof Key for Code Exchange):
- Protects against authorization code interception
- Required for public clients
- Uses SHA-256 code challenge method

### Session Management

- Sessions tied to SSO provider
- Track IP address and user agent
- Support session expiration
- Enable Single Logout (SLO) for SAML

### Audit Logging

All authentication attempts logged:
- Success/failure status
- User email and SSO user ID
- IP address and user agent
- Error messages for failures
- SSO attributes received

### CSRF Protection

- OAuth2 state parameter prevents CSRF
- SAML responses validated with signatures
- Django CSRF middleware integration

## Troubleshooting

### Common Issues

#### "Authorization code not found"
- Code verifier not stored in session
- Session expired during OAuth flow
- **Solution**: Ensure Redis is running for session storage

#### "Token exchange failed"
- Invalid client credentials
- Wrong token URL
- **Solution**: Verify OAuth2 configuration in IdP console

#### "Email domain not allowed"
- User email domain not in `required_domains`
- **Solution**: Update provider configuration or relax restrictions

#### "User does not exist and auto-creation disabled"
- `auto_create_users=false` but user not in database
- **Solution**: Enable auto-creation or manually create user

#### "Failed to parse SAML response"
- Invalid XML or missing namespaces
- Certificate validation failed
- **Solution**: Verify X.509 certificate and IdP configuration

### Debug Mode

Enable debug logging:

```python
# settings.py
LOGGING = {
    'handlers': {
        'sso': {
            'class': 'logging.FileHandler',
            'filename': 'sso_debug.log',
        }
    },
    'loggers': {
        'sso_integration': {
            'handlers': ['sso'],
            'level': 'DEBUG',
        }
    }
}
```

### Testing Connections

Use the "Test Connection" button in the UI:
1. Opens OAuth2 authorization URL in new window
2. Complete authentication flow
3. Check for errors in Django logs
4. Verify callback URL is correct

## Production Deployment

### Environment Variables

```bash
# .env
BASE_URL=https://api.mycrm.com
FRONTEND_URL=https://app.mycrm.com
SSO_SESSION_TIMEOUT=28800

# OAuth2 Credentials (if shared across environments)
GOOGLE_CLIENT_ID=your-prod-client-id
GOOGLE_CLIENT_SECRET=your-prod-secret
```

### Redirect URIs

Update redirect URIs in all OAuth2 providers:
- Development: `http://localhost:8000/api/v1/sso/callback/{provider-id}/`
- Production: `https://api.mycrm.com/api/v1/sso/callback/{provider-id}/`

### HTTPS Required

OAuth2 and SAML require HTTPS in production:
- Configure SSL/TLS certificates
- Update `BASE_URL` to use `https://`
- Ensure identity providers accept HTTPS callbacks only

### Session Storage

Use Redis for session storage in production:

```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
    }
}
```

### Monitoring

Monitor SSO login attempts:
```bash
# Failed logins in last 24 hours
GET /api/v1/sso/attempts/?status=failed&created_at__gte=2024-01-15
```

Set up alerts for:
- High failure rates (> 10% failures)
- Unusual IP addresses
- Multiple failed attempts from same email
- Provider downtime

## Advanced Features

### Multi-Organization SSO

Each organization can have its own SSO providers:
- Tenant-aware queries filter by organization
- Different providers for different customers
- Centralized SSO configuration management

### Provider Failover

Configure multiple providers for redundancy:
```python
# Primary: Google OAuth2
# Fallback: Microsoft OAuth2
```

### Just-In-Time (JIT) Provisioning

Automatically provision users on first login:
- Extract roles from SSO groups/attributes
- Map to organization roles
- Set default permissions

### Single Logout (SLO)

SAML providers support Single Logout:
1. User clicks logout in MyCRM
2. Backend sends LogoutRequest to IdP
3. IdP terminates all SSO sessions
4. User fully logged out

## Best Practices

1. **Start with Testing Status**
   - Create providers in "testing" status
   - Verify configuration thoroughly
   - Activate only when ready for production

2. **Restrict Domains**
   - Use `required_domains` to limit access
   - Prevents unauthorized signups
   - Enforces corporate email use

3. **Monitor Audit Logs**
   - Review failed login attempts regularly
   - Investigate suspicious patterns
   - Use for compliance reporting

4. **Update Certificates**
   - SAML certificates expire
   - Set reminders to renew
   - Test after certificate updates

5. **Role Management**
   - Start with conservative default roles
   - Use "viewer" or "member" initially
   - Manually promote to admin/manager

6. **Session Timeout**
   - Balance security and UX
   - Typical: 8-hour timeout
   - Consider refresh token rotation

## API Client Examples

### Python

```python
import requests

# Get providers
response = requests.get(
    'http://localhost:8000/api/v1/sso/providers/',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
providers = response.json()

# Create provider
response = requests.post(
    'http://localhost:8000/api/v1/sso/providers/',
    headers={'Authorization': 'Bearer YOUR_TOKEN'},
    json={
        'provider_type': 'oauth2_google',
        'provider_name': 'Google Workspace',
        'client_id': 'your-client-id',
        'client_secret': 'your-client-secret',
        # ... other fields
    }
)
provider = response.json()

# Test connection
response = requests.post(
    f'http://localhost:8000/api/v1/sso/providers/{provider["id"]}/test_connection/',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
result = response.json()
print(result['authorization_url'])
```

### JavaScript/TypeScript

```typescript
// Get providers
const providers = await fetch('/api/v1/sso/providers/')
  .then(r => r.json());

// Create provider
const provider = await fetch('/api/v1/sso/providers/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    provider_type: 'oauth2_google',
    provider_name: 'Google Workspace',
    client_id: 'your-client-id',
    client_secret: 'your-client-secret',
    // ... other fields
  })
}).then(r => r.json());

// Test connection
const result = await fetch(`/api/v1/sso/providers/${provider.id}/test_connection/`, {
  method: 'POST'
}).then(r => r.json());

// Open authorization URL
window.open(result.authorization_url, '_blank');
```

### cURL

```bash
# List providers
curl -X GET http://localhost:8000/api/v1/sso/providers/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create provider
curl -X POST http://localhost:8000/api/v1/sso/providers/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "oauth2_google",
    "provider_name": "Google Workspace",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
    "token_url": "https://oauth2.googleapis.com/token",
    "user_info_url": "https://www.googleapis.com/oauth2/v1/userinfo",
    "scope": "openid profile email",
    "auto_create_users": true,
    "default_role": "member"
  }'

# Get statistics
curl -X GET http://localhost:8000/api/v1/sso/providers/{id}/statistics/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Activate provider
curl -X POST http://localhost:8000/api/v1/sso/providers/{id}/activate/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Support & Resources

- **Frontend UI**: http://localhost:3000/sso-settings
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Interface**: http://localhost:8000/admin/sso_integration/

For issues or questions, check the audit log and Django logs for error details.
