"""
SSO Integration Tests
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from multi_tenant.models import Organization
from .models import SSOProvider, SSOSession, SSOLoginAttempt

User = get_user_model()


class BaseSSOTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='SSO Org', slug='sso-org')
        self.user = User.objects.create_user(username='testuser', password='testpass')


class SSOProviderTest(BaseSSOTest):
    def setUp(self):
        super().setUp()
        self.provider = SSOProvider.objects.create(
            organization=self.org,
            provider_name='Google SSO',
            provider_type='saml_custom',
            status='active',
            sso_url='https://accounts.google.com/o/saml2/idp',
            entity_id='google-sso'
        )

    def test_provider_creation(self):
        self.assertEqual(self.provider.provider_name, 'Google SSO')
        self.assertEqual(self.provider.provider_type, 'saml_custom')
        self.assertTrue(self.provider.is_active)


class SSOSessionTest(BaseSSOTest):
    def setUp(self):
        super().setUp()
        self.provider = SSOProvider.objects.create(
            organization=self.org,
            provider_name='Azure AD',
            provider_type='saml_azure',
            status='active'
        )
        self.session = SSOSession.objects.create(
            provider=self.provider,
            user=self.user,
            session_index='session-12345',
            name_id='user@company.com'
        )

    def test_session_creation(self):
        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.provider, self.provider)
        self.assertEqual(self.session.session_index, 'session-12345')
        self.assertTrue(self.session.is_active)


class SSOLoginAttemptTest(BaseSSOTest):
    def setUp(self):
        super().setUp()
        self.provider = SSOProvider.objects.create(
            organization=self.org,
            provider_name='Okta',
            provider_type='oauth2_okta',
            status='active'
        )
        self.attempt = SSOLoginAttempt.objects.create(
            provider=self.provider,
            status='success',
            email='user@example.com'
        )

    def test_attempt_creation(self):
        self.assertEqual(self.attempt.provider, self.provider)
        self.assertEqual(self.attempt.status, 'success')
        self.assertEqual(self.attempt.email, 'user@example.com')
