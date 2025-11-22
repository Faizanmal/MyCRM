#!/bin/bash

# SSO Integration Setup Script
# This script sets up the SSO Integration feature with sample data

set -e

echo "==========================================="
echo "SSO Integration Setup"
echo "==========================================="
echo ""

cd /workspaces/MyCRM/backend

# 1. Create migrations
echo "1. Creating database migrations..."
python manage.py makemigrations sso_integration

# 2. Apply migrations
echo "2. Applying migrations..."
python manage.py migrate sso_integration

# 3. Create sample SSO providers using Django shell
echo "3. Creating sample SSO providers..."
python manage.py shell << EOF
from sso_integration.models import SSOProvider
from multi_tenant.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()

# Get existing data
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    print("Error: No admin user found. Please create a superuser first.")
    exit(1)

# Get first organization
org = Organization.objects.first()
if not org:
    print("Error: No organization found. Please run setup_multi_tenant.sh first.")
    exit(1)

print(f"Using organization: {org.name}")
print(f"Using admin user: {admin_user.email}")

# Create Google OAuth2 Provider
google_provider, created = SSOProvider.objects.get_or_create(
    organization=org,
    provider_name='Google Workspace',
    defaults={
        'provider_type': 'oauth2_google',
        'status': 'testing',
        'client_id': 'your-google-client-id.apps.googleusercontent.com',
        'client_secret': 'your-google-client-secret',
        'authorization_url': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'user_info_url': 'https://www.googleapis.com/oauth2/v1/userinfo',
        'scope': 'openid profile email',
        'auto_create_users': True,
        'auto_update_user_info': True,
        'default_role': 'member',
        'required_domains': ['company.com'],
        'created_by': admin_user,
    }
)
if created:
    print(f"✓ Created Google OAuth2 provider (ID: {google_provider.id})")
else:
    print(f"✓ Google OAuth2 provider already exists (ID: {google_provider.id})")

# Create Microsoft OAuth2 Provider
microsoft_provider, created = SSOProvider.objects.get_or_create(
    organization=org,
    provider_name='Microsoft Azure AD',
    defaults={
        'provider_type': 'oauth2_microsoft',
        'status': 'inactive',
        'client_id': 'your-azure-client-id',
        'client_secret': 'your-azure-client-secret',
        'authorization_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'user_info_url': 'https://graph.microsoft.com/v1.0/me',
        'scope': 'openid profile email',
        'auto_create_users': True,
        'auto_update_user_info': True,
        'default_role': 'member',
        'created_by': admin_user,
    }
)
if created:
    print(f"✓ Created Microsoft OAuth2 provider (ID: {microsoft_provider.id})")
else:
    print(f"✓ Microsoft OAuth2 provider already exists (ID: {microsoft_provider.id})")

# Create Okta SAML Provider
okta_provider, created = SSOProvider.objects.get_or_create(
    organization=org,
    provider_name='Okta SAML',
    defaults={
        'provider_type': 'saml_okta',
        'status': 'inactive',
        'entity_id': 'https://mycrm.com/saml/metadata',
        'sso_url': 'https://your-domain.okta.com/app/appid/sso/saml',
        'slo_url': 'https://your-domain.okta.com/app/appid/slo/saml',
        'x509_cert': '''-----BEGIN CERTIFICATE-----
MIIDpDCCAoygAwIBAgIGAXoTivr8MA0GCSqGSIb3DQEBCwUAMIGSMQswCQYDVQQG
EwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNj
bzENMAsGA1UECgwET2t0YTEUMBIGA1UECwwLU1NPUHJvdmlkZXIxEzARBgNVBAMM
Cmludm9pY2UuaW8xHDAaBgkqhkiG9w0BCQEWDWluZm9Ab2t0YS5jb20wHhcNMjAw
OTA5MTgyMzQ3WhcNMzAwOTA5MTgyNDQ3WjCBkjELMAkGA1UEBhMCVVMxEzARBgNV
BAgMCkNhbGlmb3JuaWExFjAUBgNVBAcMDVNhbiBGcmFuY2lzY28xDTALBgNVBAoM
BE9rdGExFDASBgNVBAsMC1NTT1Byb3ZpZGVyMRMwEQYDVQQDDAppbnZvaWNlLmlv
MRwwGgYJKoZIhvcNAQkBFg1pbmZvQG9rdGEuY29tMIIBIjANBgkqhkiG9w0BAQEF
AAOCAQ8AMIIBCgKCAQEAk7WGRRYT5Gw7AHxYLPFkVRcJMDqN4KV1Wp8YPPPiPPPa
pJK... (example certificate)
-----END CERTIFICATE-----''',
        'attribute_mapping': {
            'email': 'mail',
            'first_name': 'givenName',
            'last_name': 'sn',
        },
        'auto_create_users': True,
        'auto_update_user_info': True,
        'default_role': 'member',
        'created_by': admin_user,
    }
)
if created:
    print(f"✓ Created Okta SAML provider (ID: {okta_provider.id})")
else:
    print(f"✓ Okta SAML provider already exists (ID: {okta_provider.id})")

print("")
print("Sample SSO providers created successfully!")
print("")
print("Provider Summary:")
print(f"  - Google OAuth2: {google_provider.status}")
print(f"  - Microsoft Azure: {microsoft_provider.status}")
print(f"  - Okta SAML: {okta_provider.status}")

EOF

echo ""
echo "==========================================="
echo "SSO Integration Setup Complete!"
echo "==========================================="
echo ""
echo "Next Steps:"
echo "1. Configure OAuth2 credentials in provider settings"
echo "2. Set up redirect URIs in your OAuth2 providers:"
echo "   http://localhost:8000/api/v1/sso/callback/{provider-id}/"
echo ""
echo "3. For SAML providers, upload your IdP metadata"
echo "4. Test connections using the 'Test Connection' button"
echo "5. Activate providers when ready for production use"
echo ""
echo "Access SSO settings at: http://localhost:3000/sso-settings"
echo ""
