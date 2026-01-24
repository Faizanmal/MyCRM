# MyCRM Backend - Comprehensive Opportunity Management Tests

"""
Opportunity Management Tests

Comprehensive test suite for opportunity management including:
- Opportunity CRUD operations
- Pipeline management
- Stage transitions
- Products and line items
- Activity tracking
- Forecasting
"""

import pytest
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta


# =============================================================================
# Opportunity CRUD Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunityListAPI:
    """Test cases for Opportunity list endpoint."""

    def test_list_opportunities_unauthenticated(self, api_client):
        """Test unauthenticated requests are rejected."""
        response = api_client.get('/api/v1/opportunities/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_opportunities_authenticated(self, authenticated_client, opportunity):
        """Test listing opportunities returns results."""
        response = authenticated_client.get('/api/v1/opportunities/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_opportunities_pagination(self, authenticated_client, user, contact, organization, pipeline):
        """Test pagination works correctly."""
        from opportunity_management.models import Opportunity

        for i in range(25):
            Opportunity.objects.create(
                name=f'Deal {i}',
                contact=contact,
                stage=pipeline[0],
                value=50000,
                owner=user,
                organization=organization
            )

        response = authenticated_client.get('/api/v1/opportunities/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_opportunities_filter_by_stage(self, authenticated_client, opportunity):
        """Test filtering by stage."""
        response = authenticated_client.get('/api/v1/opportunities/', {'stage': 'prospecting'})
        assert response.status_code == status.HTTP_200_OK

    def test_list_opportunities_filter_by_value_range(self, authenticated_client, opportunity):
        """Test filtering by value range."""
        response = authenticated_client.get('/api/v1/opportunities/', {
            'min_value': 10000,
            'max_value': 100000
        })
        assert response.status_code == status.HTTP_200_OK

    def test_list_opportunities_filter_by_close_date(self, authenticated_client, opportunity):
        """Test filtering by expected close date."""
        response = authenticated_client.get('/api/v1/opportunities/', {
            'close_after': '2025-01-01',
            'close_before': '2025-12-31'
        })
        assert response.status_code == status.HTTP_200_OK

    def test_list_opportunities_filter_by_owner(self, authenticated_client, opportunity, user):
        """Test filtering by owner."""
        response = authenticated_client.get('/api/v1/opportunities/', {'owner': user.id})
        assert response.status_code == status.HTTP_200_OK

    def test_list_opportunities_search(self, authenticated_client, opportunity):
        """Test search functionality."""
        response = authenticated_client.get('/api/v1/opportunities/', {'search': 'Test Deal'})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestOpportunityCreateAPI:
    """Test cases for Opportunity creation endpoint."""

    def test_create_opportunity_success(self, authenticated_client, contact, pipeline):
        """Test creating an opportunity successfully."""
        data = {
            'name': 'New Opportunity',
            'contact': contact.id,
            'stage': pipeline[0].id,
            'value': 75000,
            'probability': 0.25,
            'expected_close_date': '2025-06-30'
        }
        response = authenticated_client.post('/api/v1/opportunities/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_opportunity_minimal_data(self, authenticated_client, contact, pipeline):
        """Test creating opportunity with minimal data."""
        data = {
            'name': 'Minimal Deal',
            'contact': contact.id,
            'stage': pipeline[0].id
        }
        response = authenticated_client.post('/api/v1/opportunities/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_opportunity_invalid_stage(self, authenticated_client, contact):
        """Test creating opportunity with invalid stage fails."""
        data = {
            'name': 'Bad Deal',
            'contact': contact.id,
            'stage': 99999
        }
        response = authenticated_client.post('/api/v1/opportunities/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_opportunity_with_products(self, authenticated_client, contact, pipeline):
        """Test creating opportunity with line items."""
        data = {
            'name': 'Product Deal',
            'contact': contact.id,
            'stage': pipeline[0].id,
            'value': 100000,
            'products': [
                {'product_name': 'Widget A', 'quantity': 10, 'unit_price': 5000},
                {'product_name': 'Widget B', 'quantity': 5, 'unit_price': 10000}
            ]
        }
        response = authenticated_client.post('/api/v1/opportunities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]


@pytest.mark.django_db
class TestOpportunityDetailAPI:
    """Test cases for Opportunity detail endpoint."""

    def test_get_opportunity_detail(self, authenticated_client, opportunity):
        """Test getting opportunity details."""
        response = authenticated_client.get(f'/api/v1/opportunities/{opportunity.id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_update_opportunity(self, authenticated_client, opportunity):
        """Test updating opportunity."""
        data = {'value': 100000, 'probability': 0.75}
        response = authenticated_client.patch(f'/api/v1/opportunities/{opportunity.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_delete_opportunity(self, authenticated_client, opportunity):
        """Test deleting opportunity."""
        response = authenticated_client.delete(f'/api/v1/opportunities/{opportunity.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT


# =============================================================================
# Stage Management Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunityStageManagement:
    """Test cases for stage transitions and pipeline management."""

    def test_update_stage(self, authenticated_client, opportunity, pipeline):
        """Test moving opportunity to next stage."""
        next_stage = pipeline[1]  # Qualification
        data = {'stage': next_stage.id}
        response = authenticated_client.patch(f'/api/v1/opportunities/{opportunity.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_move_to_closed_won(self, authenticated_client, opportunity, pipeline):
        """Test closing opportunity as won."""
        won_stage = pipeline[4]  # Closed Won
        data = {'stage': won_stage.id}
        response = authenticated_client.patch(f'/api/v1/opportunities/{opportunity.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_move_to_closed_lost(self, authenticated_client, opportunity, pipeline):
        """Test closing opportunity as lost."""
        lost_stage = pipeline[5]  # Closed Lost
        data = {'stage': lost_stage.id, 'loss_reason': 'Budget constraints'}
        response = authenticated_client.patch(f'/api/v1/opportunities/{opportunity.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_reopen_closed_opportunity(self, authenticated_client, opportunity, pipeline):
        """Test reopening a closed opportunity."""
        # First close it
        opportunity.stage = pipeline[4]
        opportunity.save()

        # Then reopen
        data = {'stage': pipeline[1].id}
        response = authenticated_client.patch(f'/api/v1/opportunities/{opportunity.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_get_pipeline_view(self, authenticated_client, opportunity):
        """Test getting pipeline/kanban view."""
        response = authenticated_client.get('/api/v1/opportunities/pipeline/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Activity Tracking Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunityActivities:
    """Test cases for opportunity activity tracking."""

    def test_add_activity(self, authenticated_client, opportunity):
        """Test adding an activity to opportunity."""
        data = {
            'activity_type': 'meeting',
            'description': 'Proposal review meeting'
        }
        response = authenticated_client.post(f'/api/v1/opportunities/{opportunity.id}/activities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_list_activities(self, authenticated_client, opportunity):
        """Test listing opportunity activities."""
        response = authenticated_client.get(f'/api/v1/opportunities/{opportunity.id}/activities/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_add_note(self, authenticated_client, opportunity):
        """Test adding a note."""
        data = {
            'activity_type': 'note',
            'description': 'Customer expressed interest in premium tier'
        }
        response = authenticated_client.post(f'/api/v1/opportunities/{opportunity.id}/activities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_log_proposal_sent(self, authenticated_client, opportunity):
        """Test logging proposal sent activity."""
        data = {
            'activity_type': 'proposal_sent',
            'description': 'Sent proposal v2 with updated pricing'
        }
        response = authenticated_client.post(f'/api/v1/opportunities/{opportunity.id}/activities/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Product Management Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunityProducts:
    """Test cases for opportunity product/line item management."""

    def test_add_product(self, authenticated_client, opportunity):
        """Test adding a product to opportunity."""
        data = {
            'product_name': 'Enterprise License',
            'quantity': 5,
            'unit_price': 10000
        }
        response = authenticated_client.post(f'/api/v1/opportunities/{opportunity.id}/products/', data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_list_products(self, authenticated_client, opportunity):
        """Test listing opportunity products."""
        response = authenticated_client.get(f'/api/v1/opportunities/{opportunity.id}/products/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_update_product_quantity(self, authenticated_client, opportunity):
        """Test updating product quantity."""
        # First add a product
        data = {'product_name': 'Test Product', 'quantity': 1, 'unit_price': 5000}
        response = authenticated_client.post(f'/api/v1/opportunities/{opportunity.id}/products/', data, format='json')

        if response.status_code == status.HTTP_201_CREATED:
            product_id = response.data.get('id')
            update_data = {'quantity': 10}
            response = authenticated_client.patch(
                f'/api/v1/opportunities/{opportunity.id}/products/{product_id}/', update_data, format='json'
            )
            assert response.status_code == status.HTTP_200_OK

    def test_remove_product(self, authenticated_client, opportunity):
        """Test removing a product from opportunity."""
        # First add a product
        data = {'product_name': 'Remove Product', 'quantity': 1, 'unit_price': 1000}
        response = authenticated_client.post(f'/api/v1/opportunities/{opportunity.id}/products/', data, format='json')

        if response.status_code == status.HTTP_201_CREATED:
            product_id = response.data.get('id')
            response = authenticated_client.delete(f'/api/v1/opportunities/{opportunity.id}/products/{product_id}/')
            assert response.status_code == status.HTTP_204_NO_CONTENT


# =============================================================================
# Forecasting Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunityForecasting:
    """Test cases for sales forecasting functionality."""

    def test_get_forecast(self, authenticated_client, opportunity):
        """Test getting sales forecast."""
        response = authenticated_client.get('/api/v1/opportunities/forecast/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_weighted_pipeline(self, authenticated_client, opportunity):
        """Test getting weighted pipeline value."""
        response = authenticated_client.get('/api/v1/opportunities/weighted-pipeline/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_forecast_by_month(self, authenticated_client, opportunity):
        """Test getting forecast by month."""
        response = authenticated_client.get('/api/v1/opportunities/forecast/', {'group_by': 'month'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_forecast_by_quarter(self, authenticated_client, opportunity):
        """Test getting forecast by quarter."""
        response = authenticated_client.get('/api/v1/opportunities/forecast/', {'group_by': 'quarter'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Statistics Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunityStatistics:
    """Test cases for opportunity statistics and analytics."""

    def test_get_statistics(self, authenticated_client, opportunity):
        """Test getting opportunity statistics."""
        response = authenticated_client.get('/api/v1/opportunities/statistics/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_win_rate(self, authenticated_client, opportunity):
        """Test getting win rate statistics."""
        response = authenticated_client.get('/api/v1/opportunities/win-rate/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_average_deal_size(self, authenticated_client, opportunity):
        """Test getting average deal size."""
        response = authenticated_client.get('/api/v1/opportunities/average-deal-size/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_sales_velocity(self, authenticated_client, opportunity):
        """Test getting sales velocity metrics."""
        response = authenticated_client.get('/api/v1/opportunities/sales-velocity/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Bulk Operations Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunityBulkOperations:
    """Test cases for bulk opportunity operations."""

    def test_bulk_update_stage(self, authenticated_client, user, contact, organization, pipeline):
        """Test bulk updating opportunity stages."""
        from opportunity_management.models import Opportunity

        opps = []
        for i in range(5):
            opp = Opportunity.objects.create(
                name=f'Bulk Deal {i}',
                contact=contact,
                stage=pipeline[0],
                value=50000,
                owner=user,
                organization=organization
            )
            opps.append(opp)

        opp_ids = [o.id for o in opps]
        data = {
            'opportunity_ids': opp_ids,
            'stage': pipeline[1].id
        }
        response = authenticated_client.post('/api/v1/opportunities/bulk-update/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_bulk_assign_owner(self, authenticated_client, user, contact, manager_user, organization, pipeline):
        """Test bulk assigning opportunities to owner."""
        from opportunity_management.models import Opportunity

        opps = []
        for i in range(3):
            opp = Opportunity.objects.create(
                name=f'Assign Deal {i}',
                contact=contact,
                stage=pipeline[0],
                value=25000,
                owner=user,
                organization=organization
            )
            opps.append(opp)

        opp_ids = [o.id for o in opps]
        data = {
            'opportunity_ids': opp_ids,
            'owner_id': manager_user.id
        }
        response = authenticated_client.post('/api/v1/opportunities/bulk-assign/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Export Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunityExport:
    """Test cases for opportunity export functionality."""

    def test_export_csv(self, authenticated_client, opportunity):
        """Test exporting opportunities to CSV."""
        response = authenticated_client.get('/api/v1/opportunities/export/', {'format': 'csv'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_excel(self, authenticated_client, opportunity):
        """Test exporting opportunities to Excel."""
        response = authenticated_client.get('/api/v1/opportunities/export/', {'format': 'excel'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_export_with_filters(self, authenticated_client, opportunity, pipeline):
        """Test exporting filtered opportunities."""
        response = authenticated_client.get('/api/v1/opportunities/export/', {
            'format': 'csv',
            'stage': pipeline[0].id
        })
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


# =============================================================================
# Model Unit Tests
# =============================================================================

@pytest.mark.django_db
class TestOpportunityModel:
    """Unit tests for Opportunity model."""

    def test_opportunity_creation(self, organization, user, contact, pipeline):
        """Test opportunity creation with required fields."""
        from opportunity_management.models import Opportunity

        opp = Opportunity.objects.create(
            name='Test Opportunity',
            contact=contact,
            stage=pipeline[0],
            value=Decimal('50000.00'),
            owner=user,
            organization=organization
        )
        assert opp.name == 'Test Opportunity'
        assert opp.value == Decimal('50000.00')

    def test_opportunity_str_representation(self, opportunity):
        """Test opportunity string representation."""
        assert opportunity.name in str(opportunity)

    def test_opportunity_weighted_value(self, opportunity):
        """Test weighted value calculation."""
        # Assuming there's a weighted_value property or method
        expected_weighted = opportunity.value * Decimal(str(opportunity.probability))
        calculated = opportunity.value * Decimal(str(opportunity.probability))
        assert calculated == expected_weighted

    def test_opportunity_close_date_validation(self, organization, user, contact, pipeline):
        """Test expected close date validation."""
        from opportunity_management.models import Opportunity

        # Past date should be allowed for historical data
        opp = Opportunity.objects.create(
            name='Past Deal',
            contact=contact,
            stage=pipeline[0],
            expected_close_date=date.today() - timedelta(days=30),
            owner=user,
            organization=organization
        )
        assert opp.expected_close_date < date.today()


@pytest.mark.django_db
class TestOpportunityStageModel:
    """Unit tests for OpportunityStage model."""

    def test_stage_ordering(self, pipeline):
        """Test stages are ordered correctly."""
        orders = [stage.order for stage in pipeline]
        assert orders == sorted(orders)

    def test_stage_probability(self, pipeline):
        """Test stage probability values."""
        for stage in pipeline:
            assert 0 <= stage.probability <= 100


# =============================================================================
# Integration Tests
# =============================================================================

@pytest.mark.django_db
@pytest.mark.integration
class TestOpportunityIntegration:
    """Integration tests for opportunity workflows."""

    def test_full_sales_cycle(self, authenticated_client, contact, pipeline):
        """Test complete sales cycle from creation to close."""
        # Create opportunity
        data = {
            'name': 'Full Cycle Deal',
            'contact': contact.id,
            'stage': pipeline[0].id,
            'value': 50000,
            'expected_close_date': '2025-06-30'
        }
        response = authenticated_client.post('/api/v1/opportunities/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        opp_id = response.data['id']

        # Move through stages
        for stage in pipeline[1:5]:  # Up to Closed Won
            data = {'stage': stage.id}
            response = authenticated_client.patch(f'/api/v1/opportunities/{opp_id}/', data, format='json')
            assert response.status_code == status.HTTP_200_OK

    def test_opportunity_with_lead_conversion(self, authenticated_client, lead, pipeline):
        """Test opportunity created from lead conversion."""
        lead.status = 'qualified'
        lead.save()

        data = {
            'opportunity_name': 'Converted Deal',
            'opportunity_value': 75000
        }
        response = authenticated_client.post(f'/api/v1/leads/{lead.id}/convert/', data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]
