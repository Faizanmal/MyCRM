"""
Bulk Operations Tests

Test suite for bulk operation endpoints:
- Bulk update
- Bulk delete
- Bulk assign
"""

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
        username='bulkuser',
        email='bulk@example.com',
        password='TestPass123!',
        first_name='Bulk',
        last_name='User'
    )
    return user


@pytest.fixture
def another_user(db):
    """Create another test user."""
    return User.objects.create_user(
        username='assignee',
        email='assignee@example.com',
        password='TestPass123!',
        first_name='Assignee',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def sample_leads(db, test_user):
    """Create sample leads for testing."""
    from lead_management.models import Lead

    leads = []
    for i in range(10):
        lead = Lead.objects.create(
            first_name=f'Lead{i}',
            last_name=f'Test{i}',
            email=f'lead{i}@example.com',
            status='new',
            source='website',
            created_by=test_user
        )
        leads.append(lead)
    return leads


@pytest.fixture
def sample_tasks(db, test_user):
    """Create sample tasks for testing."""
    from task_management.models import Task

    tasks = []
    for i in range(10):
        task = Task.objects.create(
            title=f'Task{i}',
            status='pending',
            priority='medium',
            created_by=test_user
        )
        tasks.append(task)
    return tasks


class TestBulkUpdateLeads:
    """Test cases for bulk update leads endpoint."""

    @pytest.mark.django_db
    def test_bulk_update_leads_status(self, authenticated_client, sample_leads):
        """Test bulk updating lead status."""
        url = reverse('core:bulk-update-leads')
        lead_ids = [lead.id for lead in sample_leads[:5]]

        response = authenticated_client.post(url, {
            'ids': lead_ids,
            'data': {'status': 'qualified'}
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True
        assert response.data.get('data', {}).get('updated') == 5

    @pytest.mark.django_db
    def test_bulk_update_empty_ids(self, authenticated_client):
        """Test bulk update with empty IDs."""
        url = reverse('core:bulk-update-leads')

        response = authenticated_client.post(url, {
            'ids': [],
            'data': {'status': 'qualified'}
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_bulk_update_invalid_field(self, authenticated_client, sample_leads):
        """Test bulk update with invalid field is ignored."""
        url = reverse('core:bulk-update-leads')
        lead_ids = [lead.id for lead in sample_leads[:5]]

        response = authenticated_client.post(url, {
            'ids': lead_ids,
            'data': {'invalid_field': 'value', 'status': 'qualified'}
        }, format='json')

        # Should still succeed with valid fields
        assert response.status_code == status.HTTP_200_OK


class TestBulkDeleteLeads:
    """Test cases for bulk delete leads endpoint."""

    @pytest.mark.django_db
    def test_bulk_delete_leads(self, authenticated_client, sample_leads):
        """Test bulk deleting leads."""
        from lead_management.models import Lead

        url = reverse('core:bulk-delete-leads')
        lead_ids = [lead.id for lead in sample_leads[:5]]
        initial_count = Lead.objects.count()

        response = authenticated_client.post(url, {
            'ids': lead_ids
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True
        assert Lead.objects.count() == initial_count - 5

    @pytest.mark.django_db
    def test_bulk_delete_nonexistent_ids(self, authenticated_client):
        """Test bulk delete with non-existent IDs."""
        url = reverse('core:bulk-delete-leads')

        response = authenticated_client.post(url, {
            'ids': [99999, 99998, 99997]
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestBulkAssignLeads:
    """Test cases for bulk assign leads endpoint."""

    @pytest.mark.django_db
    def test_bulk_assign_leads(self, authenticated_client, sample_leads, another_user):
        """Test bulk assigning leads to a user."""
        url = reverse('core:bulk-assign-leads')
        lead_ids = [lead.id for lead in sample_leads[:5]]

        response = authenticated_client.post(url, {
            'ids': lead_ids,
            'assignee_id': another_user.id
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True
        assert response.data.get('data', {}).get('assigned') == 5

    @pytest.mark.django_db
    def test_bulk_assign_invalid_assignee(self, authenticated_client, sample_leads):
        """Test bulk assign with invalid assignee."""
        url = reverse('core:bulk-assign-leads')
        lead_ids = [lead.id for lead in sample_leads[:5]]

        response = authenticated_client.post(url, {
            'ids': lead_ids,
            'assignee_id': 99999  # Non-existent user
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestBulkUpdateTasks:
    """Test cases for bulk update tasks endpoint."""

    @pytest.mark.django_db
    def test_bulk_update_tasks_priority(self, authenticated_client, sample_tasks):
        """Test bulk updating task priority."""
        url = reverse('core:bulk-update-tasks')
        task_ids = [task.id for task in sample_tasks[:5]]

        response = authenticated_client.post(url, {
            'ids': task_ids,
            'data': {'priority': 'high'}
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True


class TestBulkCompleteTasks:
    """Test cases for bulk complete tasks endpoint."""

    @pytest.mark.django_db
    def test_bulk_complete_tasks(self, authenticated_client, sample_tasks):
        """Test bulk completing tasks."""
        from task_management.models import Task

        url = reverse('core:bulk-complete-tasks')
        task_ids = [task.id for task in sample_tasks[:5]]

        response = authenticated_client.post(url, {
            'ids': task_ids
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True

        # Verify tasks are completed
        completed_count = Task.objects.filter(
            id__in=task_ids,
            status='completed'
        ).count()
        assert completed_count == 5


class TestBulkOperationPermissions:
    """Test cases for bulk operation permissions."""

    @pytest.mark.django_db
    def test_unauthenticated_bulk_update(self, api_client):
        """Test bulk update requires authentication."""
        url = reverse('core:bulk-update-leads')

        response = api_client.post(url, {
            'ids': [1, 2, 3],
            'data': {'status': 'qualified'}
        }, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_user_cannot_bulk_update_others_leads(self, api_client, test_user):
        """Test user can only bulk update their own leads."""
        from lead_management.models import Lead

        # Create leads for another user
        other_user = User.objects.create_user(
            username='other', email='other@example.com', password='Pass123!'
        )
        lead = Lead.objects.create(
            first_name='Other', last_name='Lead',
            email='other@example.com', status='new',
            created_by=other_user
        )

        # Try to update as test_user
        api_client.force_authenticate(user=test_user)
        url = reverse('core:bulk-update-leads')

        response = api_client.post(url, {
            'ids': [lead.id],
            'data': {'status': 'qualified'}
        }, format='json')

        # Should fail because lead doesn't belong to test_user
        assert response.status_code == status.HTTP_400_BAD_REQUEST
