"""
SSO Integration Tests
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import SSOProvider, SSOConnection, SSOSession

User = get_user_model()


class SSOProviderTest(TestCase):
    def setUp(self):
        self.provider = SSOProvider.objects.create(
            name='Google SSO',
            provider_type='saml',
            is_active=True,
            issuer_url='https://accounts.google.com',
            sso_url='https://accounts.google.com/o/saml2/idp',
            entity_id='google-sso'
        )
    
    def test_provider_creation(self):
        self.assertEqual(self.provider.name, 'Google SSO')
        self.assertEqual(self.provider.provider_type, 'saml')
        self.assertTrue(self.provider.is_active)


class SSOConnectionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.provider = SSOProvider.objects.create(
            name='Google SSO',
            provider_type='oauth2',
            is_active=True
        )
        self.connection = SSOConnection.objects.create(
            user=self.user,
            provider=self.provider,
            external_id='google-12345',
            email='test@example.com',
            is_active=True
        )
    
    def test_connection_creation(self):
        self.assertEqual(self.connection.user, self.user)
        self.assertEqual(self.connection.provider, self.provider)
        self.assertTrue(self.connection.is_active)


class SSOSessionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.provider = SSOProvider.objects.create(
            name='Azure AD',
            provider_type='saml',
            is_active=True
        )
        self.session = SSOSession.objects.create(
            user=self.user,
            provider=self.provider,
            session_token='test-token-123',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )
    
    def test_session_creation(self):
        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.session_token, 'test-token-123')
        self.assertTrue(self.session.is_active)
