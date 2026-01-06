"""
AI Insights Tests
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import AIInsight, DataAnalysisJob, PredictionModel

User = get_user_model()


class AIInsightModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.insight = AIInsight.objects.create(
            title='Lead Conversion Trend',
            insight_type='trend',
            category='lead_conversion',
            description='Lead conversion rate is increasing',
            confidence_score=0.85,
            generated_by=self.user
        )

    def test_insight_creation(self):
        self.assertEqual(self.insight.title, 'Lead Conversion Trend')
        self.assertEqual(self.insight.confidence_score, 0.85)
        self.assertFalse(self.insight.is_dismissed)


class PredictionModelTest(TestCase):
    def setUp(self):
        self.model = PredictionModel.objects.create(
            name='Lead Scoring Model',
            model_type='lead_scoring',
            version='1.0',
            accuracy=0.92,
            status='active'
        )

    def test_model_creation(self):
        self.assertEqual(self.model.name, 'Lead Scoring Model')
        self.assertEqual(self.model.accuracy, 0.92)
        self.assertEqual(self.model.status, 'active')


class DataAnalysisJobTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.job = DataAnalysisJob.objects.create(
            name='Sales Forecast Analysis',
            job_type='forecast',
            status='pending',
            created_by=self.user
        )

    def test_job_creation(self):
        self.assertEqual(self.job.name, 'Sales Forecast Analysis')
        self.assertEqual(self.job.status, 'pending')
        self.assertEqual(self.job.progress, 0)
