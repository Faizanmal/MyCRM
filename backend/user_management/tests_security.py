from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.test import APIClient
from datetime import timedelta

User = get_user_model()


class SettingsSecurityTests(TestCase):
    def test_jwt_lifetimes_and_cookie_defaults(self):
        # Access token lifetime default is 15 minutes
        access_td = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')
        refresh_td = settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME')
        self.assertIsInstance(access_td, timedelta)
        self.assertIsInstance(refresh_td, timedelta)
        self.assertEqual(int(access_td.total_seconds()), 15 * 60)
        # refresh default is 7 days (10080 minutes)
        self.assertEqual(int(refresh_td.total_seconds()), 10080 * 60)

    def test_session_cookie_settings(self):
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertIn(settings.SESSION_COOKIE_SAMESITE, ('Lax', 'Strict', 'None'))


class LoginProtectionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_admin_login_requires_2fa(self):
        User.objects.create_user(username='adminx', email='adminx@example.com', password='adminpass', role='admin')
        # admin doesn't have 2FA enabled by default
        resp = self.client.post('/api/auth/login/', {'username': 'adminx', 'password': 'adminpass'}, format='json')
        self.assertEqual(resp.status_code, 403)
        self.assertIn('2FA', str(resp.data.get('error', '')))

    def test_login_rate_limit(self):
        User.objects.create_user(username='ratetest', email='ratetest@example.com', password='testpass')
        # Hit login 11 times to exceed the 10/h limit
        last_resp = None
        for i in range(11):
            last_resp = self.client.post('/api/auth/login/', {'username': 'ratetest', 'password': 'testpass'}, format='json')
        # Expect at least the last request to be rate limited (429)
        self.assertEqual(last_resp.status_code, 429)
