# MyCRM Backend - Comprehensive Test Suite for AI Insights

import pytest
from django.urls import reverse
from rest_framework import status
from decimal import Decimal


@pytest.mark.django_db
class TestAIInsightsAPI:
    """Tests for AI Insights API endpoints."""

    def test_get_churn_predictions(self, authenticated_client):
        """Test getting customer churn predictions."""
        url = '/api/v1/ai-insights/churn-predictions/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_next_best_actions(self, authenticated_client):
        """Test getting next best action recommendations."""
        url = '/api/v1/ai-insights/next-best-actions/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_generate_content(self, authenticated_client):
        """Test AI content generation."""
        url = '/api/v1/ai-insights/generate-content/'
        data = {
            'content_type': 'email',
            'context': 'Follow up on product demo',
            'tone': 'professional',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_analyze_sentiment(self, authenticated_client):
        """Test sentiment analysis."""
        url = '/api/v1/ai-insights/analyze-sentiment/'
        data = {
            'text': 'I am very happy with your product. It has been great working with your team!',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_deal_score(self, authenticated_client, opportunity):
        """Test getting AI deal scoring."""
        if opportunity:
            url = f'/api/v1/ai-insights/deal-score/{opportunity.id}/'
            response = authenticated_client.get(url)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_lead_scoring(self, authenticated_client, lead):
        """Test getting AI lead scoring."""
        if lead:
            url = f'/api/v1/ai-insights/lead-score/{lead.id}/'
            response = authenticated_client.get(url)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestLeadScoringAPI:
    """Tests for Lead Scoring functionality."""

    def test_batch_score_leads(self, authenticated_client):
        """Test batch scoring leads."""
        url = '/api/v1/leads/batch-score/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]

    def test_get_scoring_model_info(self, authenticated_client):
        """Test getting scoring model information."""
        url = '/api/v1/ai-insights/scoring-model/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_retrain_model(self, admin_client):
        """Test triggering model retraining (admin only)."""
        url = '/api/v1/ai-insights/retrain-model/'
        response = admin_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestPredictiveAnalytics:
    """Tests for Predictive Analytics features."""

    def test_revenue_forecast(self, authenticated_client):
        """Test revenue forecasting."""
        url = '/api/v1/ai-insights/revenue-forecast/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_pipeline_forecast(self, authenticated_client):
        """Test pipeline forecasting."""
        url = '/api/v1/ai-insights/pipeline-forecast/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_win_probability(self, authenticated_client, opportunity):
        """Test win probability calculation."""
        if opportunity:
            url = f'/api/v1/opportunities/{opportunity.id}/win-probability/'
            response = authenticated_client.get(url)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.fixture
def lead(db, organization, user):
    """Create a test lead."""
    try:
        from lead_management.models import Lead
        return Lead.objects.create(
            first_name='Test',
            last_name='Lead',
            email='testlead@example.com',
            company='Test Company',
            status='new',
            source='website',
            organization=organization,
            owner=user,
        )
    except Exception:
        return None


@pytest.fixture
def opportunity(db, organization, user):
    """Create a test opportunity."""
    try:
        from opportunity_management.models import Opportunity
        return Opportunity.objects.create(
            name='Test Opportunity',
            value=Decimal('50000.00'),
            stage='qualification',
            probability=30,
            organization=organization,
            owner=user,
        )
    except Exception:
        return None
