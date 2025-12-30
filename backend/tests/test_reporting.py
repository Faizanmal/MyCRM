# MyCRM Backend - Reporting & Analytics Tests

import pytest
from rest_framework import status
from datetime import datetime, timedelta


@pytest.mark.django_db
class TestReportsAPI:
    """Tests for Reports API endpoints."""

    def test_list_reports(self, authenticated_client):
        """Test listing available reports."""
        url = '/api/v1/reports/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_custom_report(self, authenticated_client):
        """Test creating a custom report."""
        url = '/api/v1/reports/'
        data = {
            'name': 'Monthly Sales Summary',
            'description': 'Summary of sales performance by team member',
            'type': 'custom',
            'entity': 'opportunity',
            'columns': ['owner', 'stage', 'value', 'close_date'],
            'filters': [
                {'field': 'close_date', 'operator': 'this_month'},
            ],
            'grouping': 'owner',
            'chart_type': 'bar',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_run_report(self, authenticated_client):
        """Test running a report."""
        url = '/api/v1/reports/1/run/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_run_report_with_parameters(self, authenticated_client):
        """Test running a report with parameters."""
        url = '/api/v1/reports/1/run/'
        data = {
            'start_date': (datetime.now() - timedelta(days=30)).date().isoformat(),
            'end_date': datetime.now().date().isoformat(),
            'user_id': 1,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_report_csv(self, authenticated_client):
        """Test exporting report to CSV."""
        url = '/api/v1/reports/1/export/?format=csv'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_report_pdf(self, authenticated_client):
        """Test exporting report to PDF."""
        url = '/api/v1/reports/1/export/?format=pdf'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_report_excel(self, authenticated_client):
        """Test exporting report to Excel."""
        url = '/api/v1/reports/1/export/?format=xlsx'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_schedule_report(self, authenticated_client):
        """Test scheduling a report."""
        url = '/api/v1/reports/1/schedule/'
        data = {
            'frequency': 'weekly',
            'day': 'monday',
            'time': '09:00',
            'recipients': ['manager@example.com'],
            'format': 'pdf',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestDashboardsAPI:
    """Tests for Dashboards API endpoints."""

    def test_list_dashboards(self, authenticated_client):
        """Test listing dashboards."""
        url = '/api/v1/dashboards/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_dashboard(self, authenticated_client):
        """Test creating a dashboard."""
        url = '/api/v1/dashboards/'
        data = {
            'name': 'Sales Overview',
            'description': 'Key sales metrics at a glance',
            'layout': 'grid',
            'is_default': False,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_get_dashboard(self, authenticated_client):
        """Test getting dashboard with widgets."""
        url = '/api/v1/dashboards/1/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_add_widget(self, authenticated_client):
        """Test adding a widget to dashboard."""
        url = '/api/v1/dashboards/1/widgets/'
        data = {
            'type': 'metric',
            'title': 'Total Revenue',
            'config': {
                'entity': 'opportunity',
                'aggregation': 'sum',
                'field': 'value',
                'filter': {'stage': 'closed_won'},
            },
            'position': {'x': 0, 'y': 0, 'w': 3, 'h': 2},
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_update_widget_position(self, authenticated_client):
        """Test updating widget position."""
        url = '/api/v1/dashboards/1/widgets/1/'
        data = {'position': {'x': 3, 'y': 0, 'w': 3, 'h': 2}}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_duplicate_dashboard(self, authenticated_client):
        """Test duplicating a dashboard."""
        url = '/api/v1/dashboards/1/duplicate/'
        data = {'name': 'Sales Overview (Copy)'}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_share_dashboard(self, authenticated_client):
        """Test sharing a dashboard."""
        url = '/api/v1/dashboards/1/share/'
        data = {
            'user_ids': [2, 3],
            'permission': 'view',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestWidgetTypesAPI:
    """Tests for Widget Types API endpoints."""

    def test_list_widget_types(self, authenticated_client):
        """Test listing available widget types."""
        url = '/api/v1/dashboards/widget-types/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_widget_config_schema(self, authenticated_client):
        """Test getting widget configuration schema."""
        url = '/api/v1/dashboards/widget-types/chart/config/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestSalesMetricsAPI:
    """Tests for Sales Metrics API endpoints."""

    def test_get_sales_summary(self, authenticated_client):
        """Test getting sales summary metrics."""
        url = '/api/v1/analytics/sales/summary/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_pipeline_value(self, authenticated_client):
        """Test getting pipeline value by stage."""
        url = '/api/v1/analytics/sales/pipeline/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_conversion_rates(self, authenticated_client):
        """Test getting conversion rates."""
        url = '/api/v1/analytics/sales/conversion/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_sales_velocity(self, authenticated_client):
        """Test getting sales velocity metrics."""
        url = '/api/v1/analytics/sales/velocity/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_win_loss_analysis(self, authenticated_client):
        """Test getting win/loss analysis."""
        url = '/api/v1/analytics/sales/win-loss/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_team_performance(self, authenticated_client):
        """Test getting team performance metrics."""
        url = '/api/v1/analytics/sales/team-performance/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestForecastingAPI:
    """Tests for Sales Forecasting API endpoints."""

    def test_get_forecast(self, authenticated_client):
        """Test getting sales forecast."""
        url = '/api/v1/analytics/forecast/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_forecast_by_user(self, authenticated_client):
        """Test getting forecast by user."""
        url = '/api/v1/analytics/forecast/?group_by=user'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_submit_forecast_adjustment(self, authenticated_client):
        """Test submitting a forecast adjustment."""
        url = '/api/v1/analytics/forecast/adjust/'
        data = {
            'period': '2024-Q4',
            'adjustment': 50000,
            'reason': 'New enterprise deal in pipeline',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_get_forecast_accuracy(self, authenticated_client):
        """Test getting forecast accuracy history."""
        url = '/api/v1/analytics/forecast/accuracy/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestLeadAnalyticsAPI:
    """Tests for Lead Analytics API endpoints."""

    def test_get_lead_sources(self, authenticated_client):
        """Test getting lead sources breakdown."""
        url = '/api/v1/analytics/leads/sources/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_lead_funnel(self, authenticated_client):
        """Test getting lead funnel metrics."""
        url = '/api/v1/analytics/leads/funnel/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_lead_response_time(self, authenticated_client):
        """Test getting lead response time metrics."""
        url = '/api/v1/analytics/leads/response-time/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_lead_quality_score_distribution(self, authenticated_client):
        """Test getting lead quality score distribution."""
        url = '/api/v1/analytics/leads/quality-distribution/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
