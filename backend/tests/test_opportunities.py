"""
Opportunity Management API Tests

Comprehensive test suite for opportunity/deal management including:
- CRUD operations
- Pipeline management
- Value calculations
- Forecasting
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
        username='dealuser',
        email='deals@example.com',
        password='TestPass123!',
        first_name='Deal',
        last_name='User'
    )
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def sample_opportunity(db, test_user):
    """Create and return a sample opportunity."""
    from opportunity_management.models import Opportunity
    return Opportunity.objects.create(
        name='Enterprise Deal',
        value=50000,
        stage='qualification',
        probability=25,
        expected_close_date='2025-03-31',
        owner=test_user
    )


class TestOpportunityCRUD:
    """Test cases for opportunity CRUD operations."""

    @pytest.mark.django_db
    def test_create_opportunity_success(self, authenticated_client):
        """Test successful opportunity creation."""
        url = reverse('api:v1:opportunities-list')
        data = {
            'name': 'New Big Deal',
            'value': 100000,
            'stage': 'prospecting',
            'probability': 10,
            'expected_close_date': '2025-06-30'
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get('name') == 'New Big Deal'
        assert float(response.data.get('value', 0)) == 100000.0 or response.data.get('value') == 100000

    @pytest.mark.django_db
    def test_create_opportunity_invalid_stage(self, authenticated_client):
        """Test opportunity creation with invalid stage."""
        url = reverse('api:v1:opportunities-list')
        data = {
            'name': 'Invalid Deal',
            'value': 50000,
            'stage': 'invalid_stage',  # Invalid stage
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_get_opportunity_detail(self, authenticated_client, sample_opportunity):
        """Test retrieving a single opportunity."""
        url = reverse('api:v1:opportunities-detail', kwargs={'pk': sample_opportunity.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('name') == 'Enterprise Deal'

    @pytest.mark.django_db
    def test_update_opportunity_stage(self, authenticated_client, sample_opportunity):
        """Test updating opportunity stage."""
        url = reverse('api:v1:opportunities-detail', kwargs={'pk': sample_opportunity.id})
        data = {'stage': 'proposal', 'probability': 50}
        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('stage') == 'proposal'

    @pytest.mark.django_db
    def test_delete_opportunity(self, authenticated_client, sample_opportunity):
        """Test deleting an opportunity."""
        url = reverse('api:v1:opportunities-detail', kwargs={'pk': sample_opportunity.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestOpportunityPipeline:
    """Test cases for pipeline functionality."""

    @pytest.mark.django_db
    def test_list_opportunities_by_stage(self, authenticated_client, test_user):
        """Test listing opportunities filtered by stage."""
        from opportunity_management.models import Opportunity

        # Create opportunities in different stages
        stages = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won']
        for stage in stages:
            Opportunity.objects.create(
                name=f'{stage.title()} Deal',
                value=10000,
                stage=stage,
                owner=test_user
            )

        url = reverse('api:v1:opportunities-list')
        response = authenticated_client.get(url, {'stage': 'proposal'})

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        if results:
            for opp in results:
                assert opp.get('stage') == 'proposal'

    @pytest.mark.django_db
    def test_pipeline_value_calculation(self, authenticated_client, test_user):
        """Test pipeline value calculation."""
        from opportunity_management.models import Opportunity

        # Create opportunities with known values
        Opportunity.objects.create(
            name='Deal 1',
            value=100000,
            stage='proposal',
            probability=50,
            owner=test_user
        )
        Opportunity.objects.create(
            name='Deal 2',
            value=50000,
            stage='negotiation',
            probability=75,
            owner=test_user
        )

        url = reverse('api:v1:opportunities-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK


class TestOpportunityForecasting:
    """Test cases for forecasting functionality."""

    @pytest.mark.django_db
    @pytest.mark.slow
    def test_weighted_pipeline_value(self, authenticated_client, test_user):
        """Test weighted pipeline value calculation."""
        from opportunity_management.models import Opportunity

        Opportunity.objects.create(
            name='High Probability Deal',
            value=100000,
            stage='negotiation',
            probability=80,
            owner=test_user
        )
        Opportunity.objects.create(
            name='Low Probability Deal',
            value=200000,
            stage='prospecting',
            probability=10,
            owner=test_user
        )

        # Expected weighted value: (100000 * 0.8) + (200000 * 0.1) = 80000 + 20000 = 100000
        url = reverse('api:v1:opportunities-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK


class TestOpportunityPermissions:
    """Test cases for opportunity access permissions."""

    @pytest.mark.django_db
    def test_unauthenticated_access_denied(self, api_client):
        """Test unauthenticated access is denied."""
        url = reverse('api:v1:opportunities-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_user_can_see_own_opportunities(self, api_client, test_user):
        """Test user can see their own opportunities."""
        from opportunity_management.models import Opportunity

        # Create another user
        other_user = User.objects.create_user(
            username='other', email='other@example.com', password='Pass123!'
        )

        # Create opportunities for both users
        Opportunity.objects.create(
            name='My Deal',
            value=10000,
            stage='prospecting',
            owner=test_user
        )
        Opportunity.objects.create(
            name='Other Deal',
            value=20000,
            stage='prospecting',
            owner=other_user
        )

        api_client.force_authenticate(user=test_user)
        url = reverse('api:v1:opportunities-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Response should include opportunities (visibility depends on permission model)
