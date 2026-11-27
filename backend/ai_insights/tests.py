"""
AI Insights Tests
"""
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from contact_management.models import Contact
from .models import ChurnPrediction, NextBestAction

User = get_user_model()


class ChurnPredictionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            created_by=self.user
        )
        self.prediction = ChurnPrediction.objects.create(
            contact=self.contact,
            churn_probability=0.75,
            risk_level='high',
            factors={'inactivity_days': 30},
            confidence_score=0.88,
            model_version='v1.0',
            expires_at=timezone.now() + timedelta(days=30)
        )

    def test_churn_prediction_creation(self):
        self.assertEqual(self.prediction.contact, self.contact)
        self.assertEqual(self.prediction.risk_level, 'high')
        self.assertAlmostEqual(self.prediction.churn_probability, 0.75)


class NextBestActionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='actionuser', password='testpass')
        self.action = NextBestAction.objects.create(
            user=self.user,
            entity_type='contact',
            entity_id=1,
            action_type='call',
            title='Follow up call',
            description='Discuss renewal',
            reasoning='High churn risk detected',
            priority_score=85.0
        )

    def test_next_best_action_creation(self):
        self.assertEqual(self.action.title, 'Follow up call')
        self.assertEqual(self.action.action_type, 'call')
        self.assertEqual(self.action.priority_score, 85.0)
