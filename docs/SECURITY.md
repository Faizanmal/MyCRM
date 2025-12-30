# 🔐 MyCRM Security Guide

## Security Overview

MyCRM is built with security-first principles, implementing defense-in-depth across all layers. This document outlines our security architecture, policies, and best practices.

---

## 🛡️ Security Architecture

### Defense in Depth Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SECURITY LAYERS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 1: PERIMETER SECURITY                       │   │
│  │  • CloudFlare DDoS Protection                                       │   │
│  │  • Web Application Firewall (WAF)                                   │   │
│  │  • Rate Limiting (100-10000 req/hr by plan)                        │   │
│  │  • Bot Detection & CAPTCHA                                          │   │
│  │  • Geo-blocking (configurable)                                      │   │
│  │  • SSL/TLS 1.3 Termination                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 2: APPLICATION SECURITY                     │   │
│  │  • JWT Authentication (15min access, 7d refresh)                    │   │
│  │  • Multi-Factor Authentication (TOTP)                               │   │
│  │  • Role-Based Access Control (RBAC)                                 │   │
│  │  • Attribute-Based Access Control (ABAC)                            │   │
│  │  • Input Validation & Sanitization                                  │   │
│  │  • Output Encoding (XSS prevention)                                 │   │
│  │  • CSRF Protection                                                  │   │
│  │  • Security Headers (CSP, HSTS, X-Frame-Options)                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 3: NETWORK SECURITY                         │   │
│  │  • VPC Isolation                                                    │   │
│  │  • Private Subnets for Databases                                    │   │
│  │  • Network Policies (Kubernetes)                                    │   │
│  │  • Service Mesh mTLS (Istio)                                       │   │
│  │  • Internal Firewall Rules                                          │   │
│  │  • Network Segmentation                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 4: DATA SECURITY                            │   │
│  │  • Encryption at Rest (AES-256-GCM)                                │   │
│  │  • Encryption in Transit (TLS 1.3)                                 │   │
│  │  • Field-Level Encryption (PII)                                    │   │
│  │  • Key Management (HashiCorp Vault / AWS KMS)                      │   │
│  │  • Database Access Controls                                         │   │
│  │  • Backup Encryption                                                │   │
│  │  • Data Masking (non-prod environments)                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 5: MONITORING & AUDIT                       │   │
│  │  • Comprehensive Audit Logging                                      │   │
│  │  • Real-time Threat Detection                                       │   │
│  │  • SIEM Integration                                                 │   │
│  │  • Security Alerting (PagerDuty)                                   │   │
│  │  • Compliance Monitoring                                            │   │
│  │  • Vulnerability Scanning                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Authentication

### JWT Token Configuration

```python
# Token Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.environ.get('JWT_SECRET_KEY'),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}
```

### Multi-Factor Authentication

MyCRM supports TOTP-based MFA:

```python
# Enable MFA for user
POST /api/v1/auth/mfa/enable/
Response: {
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_code": "data:image/png;base64,...",
    "backup_codes": ["ABC123", "DEF456", ...]
}

# Verify MFA on login
POST /api/v1/auth/mfa/verify/
Body: { "code": "123456" }
```

### Password Policy

| Requirement | Value |
|-------------|-------|
| Minimum Length | 12 characters |
| Uppercase | At least 1 |
| Lowercase | At least 1 |
| Numbers | At least 1 |
| Special Characters | At least 1 |
| Password History | Last 10 passwords |
| Max Age | 90 days (enterprise) |
| Account Lockout | 5 failed attempts |
| Lockout Duration | 30 minutes |

### SSO Integration

Supported identity providers:
- **SAML 2.0:** Okta, OneLogin, Azure AD
- **OAuth 2.0:** Google, Microsoft, GitHub
- **OIDC:** Any OIDC-compliant provider

---

## 🔒 Authorization

### Role-Based Access Control (RBAC)

| Role | Description | Permissions |
|------|-------------|-------------|
| **Super Admin** | Platform administrator | Full access to all features |
| **Admin** | Organization administrator | Manage users, settings, all data |
| **Manager** | Team manager | Manage team members, view reports |
| **Sales Rep** | Standard user | CRUD own data, view team data |
| **Marketing** | Marketing user | Campaign management, analytics |
| **Read Only** | Viewer | View-only access |

### Permission Matrix

| Resource | Super Admin | Admin | Manager | Sales Rep | Read Only |
|----------|:-----------:|:-----:|:-------:|:---------:|:---------:|
| Contacts | CRUD* | CRUD | CRUD | CRUD(own) | R |
| Leads | CRUD* | CRUD | CRUD | CRUD(own) | R |
| Opportunities | CRUD* | CRUD | CRUD | CRUD(own) | R |
| Reports | CRUD* | CRUD | R | R(own) | R |
| Users | CRUD* | CRUD | R | - | - |
| Settings | CRUD* | CRUD | R | - | - |
| Integrations | CRUD* | CRUD | - | - | - |
| Audit Logs | R* | R | - | - | - |

*Full cross-organization access

### Row-Level Security

```python
class ContactViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        
        # Super admins see everything
        if user.is_superuser:
            return Contact.objects.all()
        
        # Organization isolation
        queryset = Contact.objects.filter(
            organization=user.organization
        )
        
        # Role-based filtering
        if user.role == 'sales_rep':
            queryset = queryset.filter(
                Q(owner=user) | Q(assigned_to=user)
            )
        
        return queryset
```

---

## 🔐 Data Security

### Encryption at Rest

```python
# Field-level encryption for PII
from cryptography.fernet import Fernet

class EncryptedField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.fernet = Fernet(settings.ENCRYPTION_KEY)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.fernet.decrypt(value.encode()).decode()
    
    def get_prep_value(self, value):
        if value is None:
            return value
        return self.fernet.encrypt(value.encode()).decode()

# Encrypted fields
class Contact(models.Model):
    email = EncryptedField()  # PII - encrypted
    phone = EncryptedField()  # PII - encrypted
    ssn = EncryptedField(null=True)  # PII - encrypted
    first_name = models.CharField(max_length=100)  # Not PII
```

### Database Security

```sql
-- Row-level security (PostgreSQL)
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;

CREATE POLICY contact_isolation ON contacts
    USING (organization_id = current_setting('app.organization_id')::int);

-- Audit table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    record_id INT,
    action VARCHAR(10),
    old_values JSONB,
    new_values JSONB,
    user_id INT,
    ip_address INET,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Audit trigger
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user_id)
    VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(OLD), row_to_json(NEW), current_setting('app.user_id')::int);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Backup Security

- **Encryption:** All backups encrypted with AES-256
- **Retention:** 30 days for daily, 1 year for monthly
- **Geographic:** Cross-region backup replication
- **Testing:** Monthly backup restoration tests
- **Access:** Backup access requires MFA + approval

---

## 🌐 Network Security

### Security Headers

```nginx
# Nginx security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.mycrm.io wss://api.mycrm.io;" always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

### Rate Limiting

```python
# DRF throttling configuration
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/hour',
        'user': '1000/hour',
        'login': '5/minute',
        'password_reset': '3/hour',
        'api_key': '10000/hour',
    }
}
```

### CORS Configuration

```python
CORS_ALLOWED_ORIGINS = [
    "https://app.mycrm.io",
    "https://api.mycrm.io",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'x-api-key',
    'x-requested-with',
]
```

---

## 📝 Audit Logging

### Audit Events

| Event Category | Events |
|----------------|--------|
| **Authentication** | Login, Logout, MFA Enable/Disable, Password Change |
| **Authorization** | Permission Change, Role Assignment |
| **Data Access** | View, Create, Update, Delete |
| **Data Export** | Export Initiate, Export Complete |
| **Admin Actions** | User Create/Delete, Settings Change |
| **Security** | Failed Login, Account Lockout, Suspicious Activity |

### Audit Log Schema

```json
{
  "id": "audit_123abc",
  "timestamp": "2024-12-09T10:30:00Z",
  "event_type": "data.update",
  "actor": {
    "user_id": 5,
    "email": "jane@company.com",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "session_id": "sess_abc123"
  },
  "resource": {
    "type": "contact",
    "id": 42,
    "name": "John Doe"
  },
  "changes": {
    "email": {
      "old": "john@old.com",
      "new": "john@new.com"
    }
  },
  "metadata": {
    "organization_id": 1,
    "request_id": "req_xyz789"
  }
}
```

### Audit Log Retention

| Log Type | Retention |
|----------|-----------|
| Authentication Events | 2 years |
| Data Access Events | 1 year |
| Admin Actions | 5 years |
| Security Events | 5 years |
| API Requests | 90 days |

---

## 🚨 Incident Response

### Security Incident Classification

| Severity | Description | Response Time | Examples |
|----------|-------------|---------------|----------|
| **Critical (P1)** | Active data breach | 15 minutes | Data exfiltration, ransomware |
| **High (P2)** | Potential breach | 1 hour | Unauthorized access attempt |
| **Medium (P3)** | Security weakness | 4 hours | Vulnerability discovered |
| **Low (P4)** | Minor issue | 24 hours | Failed login spike |

### Incident Response Process

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Detection  │────▶│ Containment │────▶│ Eradication │────▶│  Recovery   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
   Monitoring         Isolate threat      Remove cause        Restore
   Alerting           Preserve evidence   Patch systems       Verify
   Triage             Notify stakeholders Update defenses     Monitor
                                                              Post-mortem
```

### Contact Information

| Role | Contact |
|------|---------|
| Security Team | security@mycrm.io |
| CISO | ciso@mycrm.io |
| Emergency Hotline | +1-800-SEC-URTY |

---

## ✅ Compliance

### Standards & Certifications

| Standard | Status | Next Audit |
|----------|--------|------------|
| **SOC 2 Type II** | Certified | Q2 2025 |
| **ISO 27001** | In Progress | Q3 2025 |
| **GDPR** | Compliant | Ongoing |
| **CCPA** | Compliant | Ongoing |
| **HIPAA** | Ready (upon request) | - |

### GDPR Compliance

| Right | Implementation |
|-------|----------------|
| Right to Access | Data export API |
| Right to Rectification | Edit endpoints |
| Right to Erasure | Deletion API + 30-day retention |
| Right to Portability | JSON/CSV export |
| Right to Restrict Processing | Processing flags |
| Right to Object | Opt-out mechanisms |

### Data Processing Agreements

- **Subprocessors:** AWS, CloudFlare, SendGrid, OpenAI
- **DPA:** Available upon request
- **SCC:** Standard Contractual Clauses for EU transfers

---

## 🔍 Vulnerability Management

### Security Testing Schedule

| Test Type | Frequency | Provider |
|-----------|-----------|----------|
| Automated SAST | Every commit | SonarQube |
| Dependency Scanning | Daily | Snyk |
| Container Scanning | Every build | Trivy |
| DAST | Weekly | OWASP ZAP |
| Penetration Testing | Annually | Third-party |
| Red Team Exercise | Annually | Third-party |

### Bug Bounty Program

We maintain a responsible disclosure program:

- **Scope:** *.mycrm.io
- **Rewards:** $100 - $10,000 based on severity
- **Response Time:** 24 hours acknowledgment
- **Safe Harbor:** Good faith researchers protected

Report vulnerabilities to: security@mycrm.io

---

## 📋 Security Checklist

### Development

- [ ] Input validation on all endpoints
- [ ] Parameterized queries (no SQL injection)
- [ ] Output encoding (XSS prevention)
- [ ] CSRF tokens on state-changing operations
- [ ] Secure session management
- [ ] No secrets in code or logs
- [ ] Dependency vulnerability check

### Deployment

- [ ] TLS 1.3 enabled
- [ ] Security headers configured
- [ ] Non-root container execution
- [ ] Secrets in vault/KMS
- [ ] Network policies applied
- [ ] Logging enabled
- [ ] Monitoring configured

### Operations

- [ ] Access reviews quarterly
- [ ] Security training annually
- [ ] Incident response tested
- [ ] Backups verified
- [ ] Patches applied within SLA
- [ ] Audit logs reviewed

---

*Last Updated: December 2024*
*Security Team Review: Quarterly*
*Document Classification: Internal*
