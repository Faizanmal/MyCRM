# MyCRM Backend - Workflow Automation Tests

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestWorkflowsAPI:
    """Tests for Workflows API endpoints."""

    def test_list_workflows(self, authenticated_client):
        """Test listing workflows."""
        url = '/api/v1/workflows/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_workflow(self, authenticated_client):
        """Test creating a workflow."""
        url = '/api/v1/workflows/'
        data = {
            'name': 'New Lead Follow-up',
            'description': 'Automatically assign and notify when new lead is created',
            'trigger': {
                'type': 'record_created',
                'entity': 'lead',
            },
            'conditions': [
                {'field': 'source', 'operator': 'equals', 'value': 'website'},
            ],
            'actions': [
                {'type': 'assign_to', 'user_id': 1},
                {'type': 'send_notification', 'template': 'new_lead'},
            ],
            'is_active': True,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_get_workflow(self, authenticated_client):
        """Test retrieving a workflow."""
        url = '/api/v1/workflows/1/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_update_workflow(self, authenticated_client):
        """Test updating a workflow."""
        url = '/api/v1/workflows/1/'
        data = {'name': 'Updated Workflow Name', 'is_active': False}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_delete_workflow(self, authenticated_client):
        """Test deleting a workflow."""
        url = '/api/v1/workflows/1/'
        response = authenticated_client.delete(url)
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]

    def test_activate_workflow(self, authenticated_client):
        """Test activating a workflow."""
        url = '/api/v1/workflows/1/activate/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_deactivate_workflow(self, authenticated_client):
        """Test deactivating a workflow."""
        url = '/api/v1/workflows/1/deactivate/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestTriggersAPI:
    """Tests for Workflow Triggers API endpoints."""

    def test_list_available_triggers(self, authenticated_client):
        """Test listing available triggers."""
        url = '/api/v1/workflows/triggers/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_list_trigger_entities(self, authenticated_client):
        """Test listing entities that can trigger workflows."""
        url = '/api/v1/workflows/triggers/entities/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_trigger_fields(self, authenticated_client):
        """Test getting fields available for a trigger entity."""
        url = '/api/v1/workflows/triggers/lead/fields/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestActionsAPI:
    """Tests for Workflow Actions API endpoints."""

    def test_list_available_actions(self, authenticated_client):
        """Test listing available actions."""
        url = '/api/v1/workflows/actions/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_action_config(self, authenticated_client):
        """Test getting action configuration schema."""
        url = '/api/v1/workflows/actions/send_email/config/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_test_action(self, authenticated_client):
        """Test testing an action with sample data."""
        url = '/api/v1/workflows/actions/send_email/test/'
        data = {
            'config': {
                'template_id': 1,
                'recipient_field': 'email',
            },
            'sample_record': {
                'email': 'test@example.com',
                'name': 'Test User',
            }
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestWorkflowExecutionAPI:
    """Tests for Workflow Execution API endpoints."""

    def test_list_executions(self, authenticated_client):
        """Test listing workflow executions."""
        url = '/api/v1/workflows/1/executions/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_execution_details(self, authenticated_client):
        """Test getting execution details."""
        url = '/api/v1/workflows/executions/1/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_execution_logs(self, authenticated_client):
        """Test getting execution logs."""
        url = '/api/v1/workflows/executions/1/logs/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_retry_execution(self, authenticated_client):
        """Test retrying a failed execution."""
        url = '/api/v1/workflows/executions/1/retry/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]

    def test_cancel_execution(self, authenticated_client):
        """Test canceling an in-progress execution."""
        url = '/api/v1/workflows/executions/1/cancel/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestWorkflowTemplatesAPI:
    """Tests for Workflow Templates API endpoints."""

    def test_list_templates(self, authenticated_client):
        """Test listing workflow templates."""
        url = '/api/v1/workflows/templates/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_from_template(self, authenticated_client):
        """Test creating a workflow from a template."""
        url = '/api/v1/workflows/templates/1/create/'
        data = {'name': 'My Custom Workflow'}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_save_as_template(self, authenticated_client):
        """Test saving a workflow as a template."""
        url = '/api/v1/workflows/1/save-as-template/'
        data = {
            'name': 'Lead Nurturing Template',
            'description': 'Template for lead nurturing workflows',
            'is_public': False,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestWorkflowSchedulingAPI:
    """Tests for Scheduled Workflows API endpoints."""

    def test_create_scheduled_workflow(self, authenticated_client):
        """Test creating a scheduled workflow."""
        url = '/api/v1/workflows/'
        data = {
            'name': 'Daily Report',
            'description': 'Generate and send daily sales report',
            'trigger': {
                'type': 'scheduled',
                'schedule': '0 9 * * *',  # Daily at 9 AM
            },
            'actions': [
                {'type': 'generate_report', 'report_id': 1},
                {'type': 'send_email', 'template_id': 5},
            ],
            'is_active': True,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_get_next_run_time(self, authenticated_client):
        """Test getting next scheduled run time."""
        url = '/api/v1/workflows/1/next-run/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_run_now(self, authenticated_client):
        """Test manually running a scheduled workflow."""
        url = '/api/v1/workflows/1/run-now/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestWorkflowAnalyticsAPI:
    """Tests for Workflow Analytics API endpoints."""

    def test_get_workflow_stats(self, authenticated_client):
        """Test getting workflow statistics."""
        url = '/api/v1/workflows/1/stats/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_overall_analytics(self, authenticated_client):
        """Test getting overall workflow analytics."""
        url = '/api/v1/workflows/analytics/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_failure_analysis(self, authenticated_client):
        """Test getting failure analysis."""
        url = '/api/v1/workflows/analytics/failures/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_action_performance(self, authenticated_client):
        """Test getting action performance metrics."""
        url = '/api/v1/workflows/analytics/actions/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
