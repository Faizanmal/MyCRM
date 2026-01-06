"""
Analytics API Tests

Test suite for analytics endpoints:
- Dashboard metrics
- Revenue analytics
- Pipeline analytics
- Team performance
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create and return a test user."""
    user = User.objects.create_user(
        username='analyticsuser',
        email='analytics@example.com',
        password='TestPass123!',
        first_name='Analytics',
        last_name='User'
    )
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def sample_data(db, test_user):
    """Create sample data for analytics testing."""
    from lead_management.models import Lead
    from opportunity_management.models import Opportunity
    from task_management.models import Task

    # Create leads
    leads = []
    for i in range(10):
        lead = Lead.objects.create(
            first_name=f'Lead{i}',
            last_name=f'Test{i}',
            email=f'lead{i}@example.com',
            status='new' if i % 2 == 0 else 'qualified',
            source='website',
            created_by=test_user
        )
        leads.append(lead)

    # Create opportunities
    opportunities = []
    stages = ['prospecting', 'qualification', 'proposal', 'closed_won', 'closed_lost']
    for i in range(10):
        opp = Opportunity.objects.create(
            name=f'Deal{i}',
            value=Decimal(str((i + 1) * 10000)),
            stage=stages[i % len(stages)],
            probability=20 * (i % 5 + 1),
            owner=test_user
        )
        opportunities.append(opp)

    # Create tasks
    tasks = []
    for i in range(10):
        task = Task.objects.create(
            title=f'Task{i}',
            status='completed' if i % 2 == 0 else 'pending',
            priority='high' if i % 3 == 0 else 'medium',
            due_date=date.today() + timedelta(days=i - 5),
            created_by=test_user
        )
        tasks.append(task)

    return {
        'leads': leads,
        'opportunities': opportunities,
        'tasks': tasks,
    }


class TestDashboardMetrics:
    """Test cases for dashboard metrics endpoint."""

    @pytest.mark.django_db
    def test_get_dashboard_metrics(self, authenticated_client, sample_data):
        """Test getting dashboard metrics."""
        url = reverse('core:analytics-dashboard')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True

        data = response.data.get('data', {})
        assert 'leads' in data
        assert 'revenue' in data

    @pytest.mark.django_db
    def test_dashboard_metrics_with_period(self, authenticated_client, sample_data):
        """Test dashboard metrics with different periods."""
        url = reverse('core:analytics-dashboard')

        for period in ['today', 'week', 'month', 'quarter', 'year']:
            response = authenticated_client.get(url, {'period': period})
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_dashboard_metrics_unauthenticated(self, api_client):
        """Test dashboard metrics requires authentication."""
        url = reverse('core:analytics-dashboard')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRevenueAnalytics:
    """Test cases for revenue analytics endpoint."""

    @pytest.mark.django_db
    def test_get_revenue_analytics(self, authenticated_client, sample_data):
        """Test getting revenue analytics."""
        url = reverse('core:analytics-revenue')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True

        data = response.data.get('data', {})
        assert 'trend' in data
        assert 'pipeline' in data

    @pytest.mark.django_db
    def test_revenue_analytics_grouping(self, authenticated_client, sample_data):
        """Test revenue analytics with different grouping."""
        url = reverse('core:analytics-revenue')

        response = authenticated_client.get(url, {'group_by': 'week'})
        assert response.status_code == status.HTTP_200_OK


class TestPipelineAnalytics:
    """Test cases for pipeline analytics endpoint."""

    @pytest.mark.django_db
    def test_get_pipeline_analytics(self, authenticated_client, sample_data):
        """Test getting pipeline analytics."""
        url = reverse('core:analytics-pipeline')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True

        data = response.data.get('data', {})
        assert 'stages' in data
        assert 'metrics' in data

    @pytest.mark.django_db
    def test_pipeline_metrics_content(self, authenticated_client, sample_data):
        """Test pipeline metrics contains expected data."""
        url = reverse('core:analytics-pipeline')
        response = authenticated_client.get(url)

        metrics = response.data.get('data', {}).get('metrics', {})
        assert 'conversionRate' in metrics
        assert 'avgDealSize' in metrics


class TestActivityAnalytics:
    """Test cases for activity analytics endpoint."""

    @pytest.mark.django_db
    def test_get_activity_analytics(self, authenticated_client, sample_data):
        """Test getting activity analytics."""
        url = reverse('core:analytics-activity')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True

        data = response.data.get('data', {})
        assert 'byStatus' in data or 'dailyActivity' in data


class TestTeamPerformance:
    """Test cases for team performance endpoint."""

    @pytest.mark.django_db
    def test_get_team_performance(self, authenticated_client, sample_data):
        """Test getting team performance metrics."""
        url = reverse('core:analytics-team')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True


class TestLeadSourceAnalytics:
    """Test cases for lead source analytics endpoint."""

    @pytest.mark.django_db
    def test_get_lead_source_analytics(self, authenticated_client, sample_data):
        """Test getting lead source analytics."""
        url = reverse('core:analytics-lead-sources')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True

        # Should return list of sources
        data = response.data.get('data', [])
        assert isinstance(data, list)
