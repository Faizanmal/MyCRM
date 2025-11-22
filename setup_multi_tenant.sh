#!/bin/bash

# Multi-Tenant Architecture Setup Script
# This script sets up the multi-tenant system for MyCRM

echo "========================================="
echo "Multi-Tenant Architecture Setup"
echo "========================================="
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend"

echo "Step 1: Installing dependencies..."
# No additional dependencies needed for multi-tenant

echo "Step 2: Running migrations..."
python manage.py makemigrations multi_tenant
python manage.py migrate multi_tenant

echo ""
echo "Step 3: Creating sample organizations..."

# Create sample organizations using Django shell
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
from multi_tenant.models import Organization, OrganizationMember
from datetime import date, timedelta

User = get_user_model()

# Create or get admin user
admin, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@mycrm.com',
        'is_staff': True,
        'is_superuser': True,
    }
)
if _:
    admin.set_password('admin123')
    admin.save()
    print(f'✓ Created admin user: {admin.email}')
else:
    print(f'✓ Admin user already exists: {admin.email}')

# Create sample organizations
orgs_data = [
    {
        'name': 'Acme Corporation',
        'slug': 'acme',
        'email': 'contact@acme.com',
        'domain': 'acme.mycrm.com',
        'plan': 'professional',
        'status': 'active',
        'max_users': 50,
        'max_contacts': 25000,
        'max_storage_mb': 10000,
    },
    {
        'name': 'TechStart Inc',
        'slug': 'techstart',
        'email': 'info@techstart.com',
        'domain': 'techstart.mycrm.com',
        'plan': 'starter',
        'status': 'active',
        'max_users': 10,
        'max_contacts': 5000,
        'max_storage_mb': 2000,
    },
    {
        'name': 'Demo Organization',
        'slug': 'demo',
        'email': 'demo@demo.com',
        'domain': 'demo.mycrm.com',
        'plan': 'trial',
        'status': 'trial',
        'trial_ends_at': date.today() + timedelta(days=14),
        'max_users': 5,
        'max_contacts': 1000,
        'max_storage_mb': 500,
    },
]

for org_data in orgs_data:
    org, created = Organization.objects.get_or_create(
        slug=org_data['slug'],
        defaults={**org_data, 'created_by': admin}
    )
    if created:
        print(f'✓ Created organization: {org.name} ({org.slug})')
    else:
        print(f'✓ Organization already exists: {org.name} ({org.slug})')

print('\n✓ Sample organizations created successfully!')

EOF

echo ""
echo "========================================="
echo "✅ Multi-Tenant Setup Complete!"
echo "========================================="
echo ""
echo "Sample Organizations Created:"
echo "  1. Acme Corporation (slug: acme)"
echo "     - Plan: Professional"
echo "     - Domain: acme.mycrm.com"
echo "     - Max Users: 50"
echo ""
echo "  2. TechStart Inc (slug: techstart)"
echo "     - Plan: Starter"
echo "     - Domain: techstart.mycrm.com"
echo "     - Max Users: 10"
echo ""
echo "  3. Demo Organization (slug: demo)"
echo "     - Plan: Trial (14 days)"
echo "     - Domain: demo.mycrm.com"
echo "     - Max Users: 5"
echo ""
echo "API Endpoints:"
echo "  - Organizations: http://localhost:8000/api/v1/multi-tenant/organizations/"
echo "  - Members: http://localhost:8000/api/v1/multi-tenant/members/"
echo "  - Invitations: http://localhost:8000/api/v1/multi-tenant/invitations/"
echo ""
echo "Testing with Postman/cURL:"
echo "  Add header: X-Organization-Slug: acme"
echo "  Or use subdomain: acme.mycrm.com"
echo ""
echo "Next Steps:"
echo "  1. Start server: python manage.py runserver"
echo "  2. Access API: http://localhost:8000/api/v1/multi-tenant/organizations/"
echo "  3. View docs: http://localhost:8000/api/docs/"
echo ""
