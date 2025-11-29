#!/usr/bin/env python
import os
import django
from user_management.models import User
from multi_tenant.models import Organization, OrganizationMember

# Setup Django
os.chdir('e:/SaaS_Tools/MyCRM/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def setup_dev_data():
    # Create superuser
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_superuser': True,
            'is_staff': True,
            'role': 'admin'
        }
    )
    if created or not user.check_password(os.getenv('ADMIN_PASSWORD', 'ChangeThisSecurePassword123!')):
        user.set_password(os.getenv('ADMIN_PASSWORD', 'ChangeThisSecurePassword123!'))
        user.save()

    # Create default org
    org, _ = Organization.objects.get_or_create(
        slug='default',
        defaults={
            'name': 'Default Organization',
            'domain': '127.0.0.1',
            'email': 'admin@example.com',
            'status': 'active'
        }
    )

    # Add user to organization
    member, created = OrganizationMember.objects.get_or_create(
        organization=org,
        user=user,
        defaults={'role': 'admin'}
    )

    print('User and organization created successfully')
    print('Username: admin')
    print(f'Password: {os.getenv("ADMIN_PASSWORD", "ChangeThisSecurePassword123!")}')
    print(f'Organization: {org.name}')

if __name__ == '__main__':
    setup_dev_data()