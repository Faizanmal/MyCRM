from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Organization, OrganizationMember

User = get_user_model()


class MultiTenantTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )

        # Create organizations
        self.org1 = Organization.objects.create(
            name='Test Org 1',
            slug='test-org-1',
            email='org1@test.com',
            created_by=self.user1
        )
        self.org2 = Organization.objects.create(
            name='Test Org 2',
            slug='test-org-2',
            email='org2@test.com',
            created_by=self.user2
        )

    def test_organization_creation(self):
        """Test that organization is created with owner membership."""
        self.assertEqual(Organization.objects.count(), 2)
        self.assertTrue(
            OrganizationMember.objects.filter(
                organization=self.org1,
                user=self.user1,
                role='owner'
            ).exists()
        )

    def test_user_organizations(self):
        """Test that user can only see their organizations."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/multi-tenant/organizations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_switch_organization(self):
        """Test switching between organizations."""
        # Add user1 to org2
        OrganizationMember.objects.create(
            organization=self.org2,
            user=self.user1,
            role='member'
        )

        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/v1/multi-tenant/organizations/{self.org2.id}/switch/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('organization', response.data)
