from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    ConsentType, UserConsent, DataExportRequest, DataDeletionRequest,
    DataBreachIncident, UserPrivacyPreference
)


class ConsentTypeModelTest(TestCase):
    def test_consent_type_creation(self):
        """Test creating a consent type"""
        consent_type = ConsentType.objects.create(
            name='Marketing Communications',
            description='Consent for marketing emails',
            category='marketing',
            legal_basis='consent'
        )
        self.assertEqual(consent_type.name, 'Marketing Communications')
        self.assertTrue(consent_type.is_active)


class UserConsentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.consent_type = ConsentType.objects.create(
            name='Test Consent',
            description='Test',
            category='functional'
        )

    def test_user_consent_creation(self):
        """Test creating a user consent"""
        consent = UserConsent.objects.create(
            user=self.user,
            consent_type=self.consent_type,
            is_granted=True
        )
        self.assertTrue(consent.is_granted)
        self.assertIsNone(consent.withdrawn_at)


class DataExportRequestTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_export_request_creation(self):
        """Test creating a data export request"""
        request = DataExportRequest.objects.create(
            user=self.user,
            request_type='full_export',
            format='json'
        )
        self.assertEqual(request.status, 'pending')
        self.assertEqual(request.format, 'json')


class DataDeletionRequestTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_deletion_request_creation(self):
        """Test creating a data deletion request"""
        request = DataDeletionRequest.objects.create(
            user=self.user,
            deletion_type='full_deletion',
            reason='No longer needed'
        )
        self.assertEqual(request.status, 'pending')
        self.assertFalse(request.backup_created)


class DataBreachIncidentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_breach_creation(self):
        """Test creating a breach incident"""
        breach = DataBreachIncident.objects.create(
            incident_id='BR-2024-001',
            title='Test Breach',
            description='Test breach description',
            severity='medium',
            breach_type='confidentiality',
            discovered_at=timezone.now(),
            reported_by=self.user
        )
        self.assertEqual(breach.incident_id, 'BR-2024-001')
        self.assertEqual(breach.status, 'identified')
        self.assertFalse(breach.authority_notified)


class UserPrivacyPreferenceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_privacy_preferences_creation(self):
        """Test creating privacy preferences"""
        prefs = UserPrivacyPreference.objects.create(
            user=self.user,
            allow_data_processing=True,
            allow_marketing_emails=False
        )
        self.assertTrue(prefs.allow_data_processing)
        self.assertFalse(prefs.allow_marketing_emails)
