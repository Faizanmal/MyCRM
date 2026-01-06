"""
Task Management API Tests

Comprehensive test suite for task management including:
- CRUD operations
- Task assignment
- Due dates and priorities
- Task completion tracking
"""

from datetime import date, timedelta

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
        username='taskuser',
        email='tasks@example.com',
        password='TestPass123!',
        first_name='Task',
        last_name='User'
    )
    return user


@pytest.fixture
def another_user(db):
    """Create another test user."""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='TestPass123!',
        first_name='Another',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def sample_task(db, test_user):
    """Create and return a sample task."""
    from task_management.models import Task
    return Task.objects.create(
        title='Sample Task',
        description='This is a sample task for testing',
        priority='high',
        status='pending',
        due_date=date.today() + timedelta(days=7),
        assigned_to=test_user,
        created_by=test_user
    )


class TestTaskCRUD:
    """Test cases for task CRUD operations."""

    @pytest.mark.django_db
    def test_create_task_success(self, authenticated_client):
        """Test successful task creation."""
        url = reverse('api:v1:tasks-list')
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'priority': 'medium',
            'status': 'pending',
            'due_date': (date.today() + timedelta(days=5)).isoformat()
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get('title') == 'New Task'

    @pytest.mark.django_db
    def test_create_task_without_title(self, authenticated_client):
        """Test task creation without required title."""
        url = reverse('api:v1:tasks-list')
        data = {
            'description': 'Task without title',
            'priority': 'low'
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_get_task_detail(self, authenticated_client, sample_task):
        """Test retrieving a single task."""
        url = reverse('api:v1:tasks-detail', kwargs={'pk': sample_task.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('title') == 'Sample Task'

    @pytest.mark.django_db
    def test_update_task(self, authenticated_client, sample_task):
        """Test updating a task."""
        url = reverse('api:v1:tasks-detail', kwargs={'pk': sample_task.id})
        data = {
            'title': 'Updated Task',
            'priority': 'low',
            'status': 'in_progress'
        }
        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('title') == 'Updated Task'

    @pytest.mark.django_db
    def test_delete_task(self, authenticated_client, sample_task):
        """Test deleting a task."""
        url = reverse('api:v1:tasks-detail', kwargs={'pk': sample_task.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestTaskFiltering:
    """Test cases for task filtering."""

    @pytest.mark.django_db
    def test_filter_by_status(self, authenticated_client, test_user):
        """Test filtering tasks by status."""
        from task_management.models import Task

        # Create tasks with different statuses
        Task.objects.create(title='Pending Task', status='pending', created_by=test_user)
        Task.objects.create(title='In Progress Task', status='in_progress', created_by=test_user)
        Task.objects.create(title='Completed Task', status='completed', created_by=test_user)

        url = reverse('api:v1:tasks-list')
        response = authenticated_client.get(url, {'status': 'pending'})

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_filter_by_priority(self, authenticated_client, test_user):
        """Test filtering tasks by priority."""
        from task_management.models import Task

        Task.objects.create(title='High Priority', priority='high', status='pending', created_by=test_user)
        Task.objects.create(title='Low Priority', priority='low', status='pending', created_by=test_user)

        url = reverse('api:v1:tasks-list')
        response = authenticated_client.get(url, {'priority': 'high'})

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_filter_overdue_tasks(self, authenticated_client, test_user):
        """Test filtering overdue tasks."""
        from task_management.models import Task

        # Create overdue task
        Task.objects.create(
            title='Overdue Task',
            status='pending',
            due_date=date.today() - timedelta(days=1),
            created_by=test_user
        )

        # Create future task
        Task.objects.create(
            title='Future Task',
            status='pending',
            due_date=date.today() + timedelta(days=7),
            created_by=test_user
        )

        url = reverse('api:v1:tasks-list')
        # Assuming there's an overdue filter
        response = authenticated_client.get(url, {'overdue': 'true'})

        assert response.status_code == status.HTTP_200_OK


class TestTaskCompletion:
    """Test cases for task completion functionality."""

    @pytest.mark.django_db
    def test_mark_task_complete(self, authenticated_client, sample_task):
        """Test marking a task as complete."""
        url = reverse('api:v1:tasks-detail', kwargs={'pk': sample_task.id})
        data = {'status': 'completed'}
        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('status') == 'completed'

    @pytest.mark.django_db
    def test_reopen_completed_task(self, authenticated_client, test_user):
        """Test reopening a completed task."""
        from task_management.models import Task

        task = Task.objects.create(
            title='Completed Task',
            status='completed',
            created_by=test_user
        )

        url = reverse('api:v1:tasks-detail', kwargs={'pk': task.id})
        data = {'status': 'pending'}
        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('status') == 'pending'


class TestTaskAssignment:
    """Test cases for task assignment."""

    @pytest.mark.django_db
    def test_assign_task_to_user(self, authenticated_client, sample_task, another_user):
        """Test assigning a task to another user."""
        url = reverse('api:v1:tasks-detail', kwargs={'pk': sample_task.id})
        data = {'assigned_to': another_user.id}
        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_filter_my_tasks(self, authenticated_client, test_user, another_user):
        """Test filtering tasks assigned to current user."""
        from task_management.models import Task

        # Create tasks assigned to different users
        Task.objects.create(title='My Task', assigned_to=test_user, status='pending', created_by=test_user)
        Task.objects.create(title='Other Task', assigned_to=another_user, status='pending', created_by=test_user)

        url = reverse('api:v1:tasks-list')
        response = authenticated_client.get(url, {'assigned_to': 'me'})

        assert response.status_code == status.HTTP_200_OK


class TestTaskPermissions:
    """Test cases for task permissions."""

    @pytest.mark.django_db
    def test_unauthenticated_access_denied(self, api_client):
        """Test unauthenticated access is denied."""
        url = reverse('api:v1:tasks-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_access_nonexistent_task(self, authenticated_client):
        """Test accessing non-existent task."""
        url = reverse('api:v1:tasks-detail', kwargs={'pk': 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTaskOrdering:
    """Test cases for task ordering."""

    @pytest.mark.django_db
    def test_order_by_due_date(self, authenticated_client, test_user):
        """Test ordering tasks by due date."""
        from task_management.models import Task

        Task.objects.create(title='Task 1', due_date=date.today() + timedelta(days=5), status='pending', created_by=test_user)
        Task.objects.create(title='Task 2', due_date=date.today() + timedelta(days=1), status='pending', created_by=test_user)
        Task.objects.create(title='Task 3', due_date=date.today() + timedelta(days=10), status='pending', created_by=test_user)

        url = reverse('api:v1:tasks-list')
        response = authenticated_client.get(url, {'ordering': 'due_date'})

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_order_by_priority(self, authenticated_client, test_user):
        """Test ordering tasks by priority."""
        from task_management.models import Task

        Task.objects.create(title='Low', priority='low', status='pending', created_by=test_user)
        Task.objects.create(title='High', priority='high', status='pending', created_by=test_user)
        Task.objects.create(title='Medium', priority='medium', status='pending', created_by=test_user)

        url = reverse('api:v1:tasks-list')
        response = authenticated_client.get(url, {'ordering': '-priority'})

        assert response.status_code == status.HTTP_200_OK
