# Multi-Tenant Architecture - Complete Guide

## Overview

The Multi-Tenant Architecture feature enables MyCRM to support multiple organizations (tenants) with complete data isolation, perfect for SaaS deployment. Each organization has its own users, data, settings, and subscription plans.

## 🏗️ Architecture

### Key Concepts

1. **Organization (Tenant)**: A separate entity with its own data and users
2. **Organization Member**: A user's membership in an organization with specific roles
3. **Tenant Isolation**: Complete data separation between organizations
4. **Subscription Plans**: Different feature sets and limits per organization

### Tenant Identification Methods

The system supports 4 methods to identify the current tenant:

1. **HTTP Header**: `X-Organization-Slug: acme` (recommended for APIs)
2. **Subdomain**: `acme.mycrm.com`
3. **Custom Domain**: `crm.acme.com`
4. **Session**: Stored after organization switch (web interface)

## 📦 Installation

### 1. Run Setup Script

```bash
./setup_multi_tenant.sh
```

This will:
- Run migrations for multi_tenant app
- Create 3 sample organizations
- Set up admin user

### 2. Manual Installation

```bash
cd backend

# Run migrations
python manage.py makemigrations multi_tenant
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 🔧 Configuration

### Settings (already configured)

```python
# backend/backend/settings.py

INSTALLED_APPS = [
    # ...
    'multi_tenant',
]

MIDDLEWARE = [
    # ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'multi_tenant.middleware.TenantMiddleware',  # After auth
    # ...
]
```

### URL Configuration (already configured)

```python
# backend/backend/urls.py

urlpatterns = [
    # ...
    path('api/v1/multi-tenant/', include('multi_tenant.urls')),
]
```

## 📚 Database Models

### Organization

Main tenant model with subscription management.

**Fields:**
- `id` (UUID): Primary key
- `name`: Organization name
- `slug`: URL-friendly identifier
- `domain`: Custom domain (optional)
- `status`: active, suspended, trial, cancelled
- `plan`: free, starter, professional, enterprise
- `max_users`: User limit based on plan
- `max_contacts`: Contact limit
- `max_storage_mb`: Storage limit
- `stripe_customer_id`: Stripe integration
- `subscription_start/end`: Subscription dates
- `settings`: JSON field for custom settings

### OrganizationMember

User membership in an organization.

**Roles:**
- `owner`: Full control, billing access
- `admin`: User management, settings
- `manager`: Team management
- `member`: Standard access
- `guest`: Limited access

**Permissions:**
- `can_invite_users`
- `can_manage_billing`
- `can_manage_settings`

### OrganizationInvitation

Invitation system for adding new members.

**Status:**
- `pending`: Awaiting response
- `accepted`: User joined
- `declined`: User declined
- `expired`: Invitation expired (7 days)

## 🚀 API Endpoints

### Organizations

#### List Organizations
```http
GET /api/v1/multi-tenant/organizations/
```

Returns organizations the user is a member of.

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": "uuid",
      "name": "Acme Corporation",
      "slug": "acme",
      "domain": "acme.mycrm.com",
      "status": "active",
      "plan": "professional",
      "max_users": 50,
      "user_count": 15,
      "is_active": true
    }
  ]
}
```

#### Create Organization
```http
POST /api/v1/multi-tenant/organizations/
```

**Request:**
```json
{
  "name": "My Company",
  "email": "contact@mycompany.com",
  "plan": "starter"
}
```

Slug is auto-generated from name. Creator becomes owner.

#### Switch Organization
```http
POST /api/v1/multi-tenant/organizations/{id}/switch/
```

Switches user's active organization (sets session).

#### Get Statistics
```http
GET /api/v1/multi-tenant/organizations/{id}/statistics/
```

**Response:**
```json
{
  "total_members": 15,
  "members_by_role": {
    "owner": 1,
    "admin": 2,
    "manager": 5,
    "member": 7
  },
  "pending_invitations": 3,
  "storage_used_mb": 1250,
  "storage_limit_mb": 10000,
  "storage_percentage": 12.5,
  "subscription_status": "active",
  "plan": "professional"
}
```

#### Upgrade Plan
```http
POST /api/v1/multi-tenant/organizations/{id}/upgrade_plan/
```

**Request:**
```json
{
  "plan": "enterprise"
}
```

Owner-only action. Automatically updates limits.

### Members

#### List Members
```http
GET /api/v1/multi-tenant/members/?organization={org_id}
```

Returns members of organizations where user is admin.

#### Get My Memberships
```http
GET /api/v1/multi-tenant/members/my_memberships/
```

Returns all organizations the current user belongs to.

**Response:**
```json
[
  {
    "id": "uuid",
    "organization_name": "Acme Corporation",
    "user_email": "john@acme.com",
    "role": "admin",
    "joined_at": "2025-01-15T10:30:00Z"
  }
]
```

#### Update Member Role
```http
POST /api/v1/multi-tenant/members/{id}/update_role/
```

**Request:**
```json
{
  "role": "manager"
}
```

Owner-only action. Cannot change own role.

#### Deactivate Member
```http
POST /api/v1/multi-tenant/members/{id}/deactivate/
```

Admin-only action. Cannot deactivate self or last owner.

### Invitations

#### Create Invitation
```http
POST /api/v1/multi-tenant/invitations/
```

**Request:**
```json
{
  "organization": "org-uuid",
  "email": "newuser@example.com",
  "role": "member"
}
```

Admin-only. Invitation expires in 7 days.

#### Accept Invitation
```http
POST /api/v1/multi-tenant/invitations/accept/
```

**Request:**
```json
{
  "token": "invitation-token-uuid"
}
```

User email must match invitation email.

#### Decline Invitation
```http
POST /api/v1/multi-tenant/invitations/decline/
```

**Request:**
```json
{
  "token": "invitation-token-uuid"
}
```

#### Resend Invitation
```http
POST /api/v1/multi-tenant/invitations/{id}/resend/
```

Admin-only. Extends expiration by 7 days.

## 💻 Usage Examples

### Python/Requests

```python
import requests

# Base setup
API_URL = "http://localhost:8000/api/v1/multi-tenant"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "X-Organization-Slug": "acme"  # Tenant identification
}

# Create organization
response = requests.post(
    f"{API_URL}/organizations/",
    headers=headers,
    json={
        "name": "My Startup",
        "email": "info@mystartup.com",
        "plan": "starter"
    }
)
org = response.json()
print(f"Created organization: {org['name']}")

# Invite user
response = requests.post(
    f"{API_URL}/invitations/",
    headers=headers,
    json={
        "organization": org["id"],
        "email": "colleague@example.com",
        "role": "member"
    }
)
invitation = response.json()
print(f"Invitation sent to: {invitation['email']}")

# Get organization stats
response = requests.get(
    f"{API_URL}/organizations/{org['id']}/statistics/",
    headers=headers
)
stats = response.json()
print(f"Members: {stats['total_members']}")
print(f"Storage: {stats['storage_percentage']}%")
```

### cURL

```bash
# Set variables
TOKEN="your-jwt-token"
ORG_SLUG="acme"

# List organizations
curl -X GET \
  "http://localhost:8000/api/v1/multi-tenant/organizations/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Organization-Slug: $ORG_SLUG"

# Create organization
curl -X POST \
  "http://localhost:8000/api/v1/multi-tenant/organizations/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Company",
    "email": "info@newco.com",
    "plan": "professional"
  }'

# Invite user
curl -X POST \
  "http://localhost:8000/api/v1/multi-tenant/invitations/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Organization-Slug: $ORG_SLUG" \
  -H "Content-Type: application/json" \
  -d '{
    "organization": "org-uuid",
    "email": "user@example.com",
    "role": "member"
  }'
```

### JavaScript/Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/multi-tenant',
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-Organization-Slug': 'acme'
  }
});

// Create organization
const createOrganization = async () => {
  const response = await api.post('/organizations/', {
    name: 'My Company',
    email: 'info@mycompany.com',
    plan: 'starter'
  });
  return response.data;
};

// Get my memberships
const getMyOrganizations = async () => {
  const response = await api.get('/members/my_memberships/');
  return response.data;
};

// Switch organization
const switchOrganization = async (orgId) => {
  const response = await api.post(`/organizations/${orgId}/switch/`);
  // Update header for future requests
  api.defaults.headers['X-Organization-Slug'] = response.data.organization.slug;
  return response.data;
};
```

## 🔒 Security & Permissions

### Permission Classes

```python
from multi_tenant.permissions import (
    IsOrganizationMember,
    IsOrganizationAdmin,
    IsOrganizationOwner,
    CanInviteUsers
)

# In your views
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrganizationMember]
```

### Role Hierarchy

```
Owner > Admin > Manager > Member > Guest
```

**Owner Permissions:**
- All admin permissions
- Manage billing
- Upgrade/downgrade plan
- Delete organization
- Transfer ownership

**Admin Permissions:**
- Invite/remove users
- Manage settings
- View all data
- Assign roles (except owner)

**Manager Permissions:**
- Manage team members
- View team data
- Limited settings access

**Member Permissions:**
- Access own data
- Collaborate with team
- Standard CRM features

**Guest Permissions:**
- Read-only access
- Limited to assigned items

## 🔄 Making Models Tenant-Aware

### Method 1: Inherit from TenantAwareModel

```python
from multi_tenant.models import TenantAwareModel

class Contact(TenantAwareModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    # organization field is automatically added
```

### Method 2: Manual Implementation

```python
from multi_tenant.models import Organization
from multi_tenant.managers import TenantManager

class Lead(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='leads'
    )
    name = models.CharField(max_length=255)
    
    objects = TenantManager()  # Automatically filters by organization
    all_objects = models.Manager()  # Access all data
```

### Using Tenant-Aware Queries

```python
# Automatic filtering (uses current organization from middleware)
contacts = Contact.objects.all()  # Only current organization's contacts

# Explicit organization
contacts = Contact.objects.for_organization(org)

# Bypass filtering (admin only)
all_contacts = Contact.objects.all_organizations()
```

## 📊 Subscription Plans

### Plan Limits

| Plan | Users | Contacts | Storage | Price/Month |
|------|-------|----------|---------|-------------|
| Free | 5 | 1,000 | 500 MB | $0 |
| Starter | 10 | 5,000 | 2 GB | $29 |
| Professional | 50 | 25,000 | 10 GB | $99 |
| Enterprise | Unlimited | Unlimited | 100 GB | $299 |

### Enforcing Limits

```python
from multi_tenant.middleware import get_current_organization

def create_contact(request):
    org = get_current_organization()
    
    # Check contact limit
    current_count = Contact.objects.count()
    if current_count >= org.max_contacts:
        return Response({
            'error': f'Contact limit reached ({org.max_contacts})',
            'upgrade_url': f'/billing/upgrade?org={org.id}'
        }, status=402)  # Payment Required
    
    # Create contact...
```

## 🧪 Testing

### Run Tests

```bash
python manage.py test multi_tenant
```

### Test Organization Isolation

```python
from multi_tenant.models import Organization, OrganizationMember
from django.test import TestCase

class TenantIsolationTest(TestCase):
    def test_data_isolation(self):
        # Create two organizations
        org1 = Organization.objects.create(name="Org 1")
        org2 = Organization.objects.create(name="Org 2")
        
        # Create contacts for each
        contact1 = Contact.objects.create(
            organization=org1,
            name="Contact 1"
        )
        contact2 = Contact.objects.create(
            organization=org2,
            name="Contact 2"
        )
        
        # Verify isolation
        self.assertEqual(
            Contact.objects.for_organization(org1).count(),
            1
        )
        self.assertEqual(
            Contact.objects.for_organization(org2).count(),
            1
        )
```

## 🚨 Troubleshooting

### Issue: "No organization found"

**Solution:**
```python
# Add header to request
headers = {"X-Organization-Slug": "your-org-slug"}

# Or set in session
request.session['organization_id'] = str(org.id)
```

### Issue: "User not member of organization"

**Solution:**
```python
# Verify membership
OrganizationMember.objects.filter(
    organization=org,
    user=user,
    is_active=True
).exists()
```

### Issue: "Cannot delete last owner"

This is intentional. Transfer ownership first:
```python
# Make another member owner
other_member.role = 'owner'
other_member.save()

# Then remove old owner
old_owner.delete()
```

## 🔄 Migration from Single-Tenant

### 1. Create Default Organization

```python
from multi_tenant.models import Organization

default_org = Organization.objects.create(
    name="Main Organization",
    slug="main",
    email="admin@mycrm.com",
    status="active",
    plan="enterprise"
)
```

### 2. Add Organization to Existing Data

```python
# Add organization field to existing models
class Contact(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True  # Temporary
    )

# Migrate data
Contact.objects.filter(organization__isnull=True).update(
    organization=default_org
)

# Make field required
class Contact(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE
    )
```

### 3. Update Views

```python
# Before
contacts = Contact.objects.all()

# After
from multi_tenant.middleware import get_current_organization

org = get_current_organization()
contacts = Contact.objects.filter(organization=org)

# Or use TenantManager
contacts = Contact.objects.all()  # Auto-filtered
```

## 📈 Best Practices

1. **Always use TenantManager** for automatic filtering
2. **Validate organization membership** before allowing actions
3. **Enforce plan limits** at the application level
4. **Use subdomain/header** for tenant identification
5. **Regular backup** per organization
6. **Monitor usage** for billing purposes
7. **Implement soft deletes** for data recovery
8. **Audit trail** for compliance

## 🔗 Integration with Other Features

### With AI Insights

```python
# Churn predictions per organization
predictions = ChurnPrediction.objects.all()  # Auto-filtered by tenant
```

### With Gamification

```python
# Leaderboards per organization
leaderboard = Leaderboard.objects.get(name="Sales Leaders")
rankings = leaderboard.get_rankings()  # Only current org's users
```

### With Integration Hub

```python
# Integrations per organization
integrations = Integration.objects.filter(is_active=True)
```

## 📚 Additional Resources

- [API Documentation](http://localhost:8000/api/docs/)
- [Admin Panel](http://localhost:8000/admin/multi_tenant/)
- [Django Multi-Tenant Patterns](https://django-multitenant.readthedocs.io/)
- [SaaS Best Practices](https://www.saasmetrics.co/)

---

**Version:** 1.0.0
**Status:** ✅ Production Ready
**Last Updated:** November 2025
