"""
Tests for Interactive Features API Endpoints
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .ai_recommendation_service import RecommendationEngine, generate_recommendations
from .interactive_models import (
    AIRecommendation,
    OnboardingProgress,
    QuickAction,
    SearchQuery,
    SmartFilter,
    UserPreferences,
)

User = get_user_model()


class UserPreferencesAPITestCase(APITestCase):
    """Test cases for User Preferences API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_preferences_creates_if_not_exists(self):
        """Test that getting preferences creates a new record if none exists"""
        url = '/api/v1/interactive/preferences/me/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserPreferences.objects.filter(user=self.user).exists())

    def test_update_preferences(self):
        """Test updating user preferences"""
        UserPreferences.objects.create(user=self.user)

        url = '/api/v1/interactive/preferences/me/'
        data = {
            'theme': 'dark',
            'sidebar_collapsed': True,
            'enable_sounds': False,
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'dark')
        self.assertTrue(response.data['sidebar_collapsed'])
        self.assertFalse(response.data['enable_sounds'])

    def test_save_dashboard_layout(self):
        """Test saving dashboard widget layout"""
        UserPreferences.objects.create(user=self.user)

        url = '/api/v1/interactive/preferences/dashboard/'
        data = {
            'widgets': [
                {'widget_id': 'stats', 'visible': True, 'order': 0, 'size': 'large'},
                {'widget_id': 'pipeline', 'visible': True, 'order': 1, 'size': 'medium'},
                {'widget_id': 'tasks', 'visible': False, 'order': 2, 'size': 'small'},
            ]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'saved')

    def test_add_recent_item(self):
        """Test adding a recent item"""
        prefs = UserPreferences.objects.create(user=self.user)

        url = '/api/v1/interactive/preferences/recent-item/'
        data = {
            'type': 'contact',
            'id': '123',
            'title': 'John Smith'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prefs.refresh_from_db()
        self.assertEqual(len(prefs.recent_items), 1)
        self.assertEqual(prefs.recent_items[0]['title'], 'John Smith')


class OnboardingAPITestCase(APITestCase):
    """Test cases for Onboarding API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_onboarding_status(self):
        """Test getting onboarding status"""
        url = '/api/v1/interactive/onboarding/status/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('completed_steps', response.data)
        self.assertIn('tour_completed', response.data)
        self.assertIn('completion_percentage', response.data)

    def test_complete_step(self):
        """Test completing an onboarding step"""
        OnboardingProgress.objects.create(user=self.user)

        url = '/api/v1/interactive/onboarding/step/'
        data = {'step_id': 'first_contact', 'xp_reward': 100}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('first_contact', response.data['completed_steps'])
        self.assertEqual(response.data['total_xp'], 100)

    def test_complete_step_idempotent(self):
        """Test that completing the same step twice doesn't duplicate"""
        OnboardingProgress.objects.create(
            user=self.user,
            completed_steps=['first_contact'],
            onboarding_xp=100
        )

        url = '/api/v1/interactive/onboarding/step/'
        data = {'step_id': 'first_contact', 'xp_reward': 100}
        response = self.client.post(url, data, format='json')

        # XP should not increase
        self.assertEqual(response.data['total_xp'], 100)

    def test_complete_tour(self):
        """Test completing the product tour"""
        OnboardingProgress.objects.create(user=self.user)

        url = '/api/v1/interactive/onboarding/tour/complete/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        progress = OnboardingProgress.objects.get(user=self.user)
        self.assertTrue(progress.tour_completed)
        self.assertIsNotNone(progress.tour_completed_at)

    def test_dismiss_tour(self):
        """Test dismissing the product tour"""
        OnboardingProgress.objects.create(user=self.user)

        url = '/api/v1/interactive/onboarding/tour/dismiss/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        progress = OnboardingProgress.objects.get(user=self.user)
        self.assertTrue(progress.tour_dismissed)


class AIRecommendationsAPITestCase(APITestCase):
    """Test cases for AI Recommendations API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_active_recommendations(self):
        """Test getting active recommendations"""
        # Create test recommendations
        AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='action',
            title='Test Recommendation',
            description='Test description',
            impact='high',
            status='active'
        )

        url = '/api/v1/interactive/recommendations/active/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_recommendations_by_type(self):
        """Test filtering recommendations by type"""
        AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='action',
            title='Action Rec',
            description='Test',
            impact='high',
            status='active'
        )
        AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='insight',
            title='Insight Rec',
            description='Test',
            impact='medium',
            status='active'
        )

        url = '/api/v1/interactive/recommendations/active/?type=action'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['recommendation_type'], 'action')

    def test_dismiss_recommendation(self):
        """Test dismissing a recommendation"""
        rec = AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='insight',
            title='Test',
            description='Test',
            impact='low',
            status='active',
            dismissable=True
        )

        url = f'/api/v1/interactive/recommendations/{rec.id}/dismiss/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rec.refresh_from_db()
        self.assertEqual(rec.status, 'dismissed')

    def test_cannot_dismiss_non_dismissable(self):
        """Test that non-dismissable recommendations cannot be dismissed"""
        rec = AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='warning',
            title='Important Warning',
            description='Test',
            impact='high',
            status='active',
            dismissable=False
        )

        url = f'/api/v1/interactive/recommendations/{rec.id}/dismiss/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_recommendations_excluded(self):
        """Test that expired recommendations are not returned"""
        AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='action',
            title='Expired Rec',
            description='Test',
            impact='high',
            status='active',
            expires_at=timezone.now() - timedelta(days=1)
        )

        url = '/api/v1/interactive/recommendations/active/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class GlobalSearchAPITestCase(APITestCase):
    """Test cases for Global Search API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_search_creates_query_record(self):
        """Test that search creates a query record for analytics"""
        url = '/api/v1/interactive/search/'
        data = {
            'query': 'Test Search',
            'types': ['contact', 'lead'],
            'limit': 10
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(SearchQuery.objects.filter(
            user=self.user,
            query='Test Search'
        ).exists())

    def test_get_recent_searches(self):
        """Test getting recent searches"""
        SearchQuery.objects.create(user=self.user, query='Search 1')
        SearchQuery.objects.create(user=self.user, query='Search 2')
        SearchQuery.objects.create(user=self.user, query='Search 3')

        url = '/api/v1/interactive/search/recent/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recent_searches', response.data)

    def test_clear_search_history(self):
        """Test clearing search history"""
        SearchQuery.objects.create(user=self.user, query='Search 1')
        SearchQuery.objects.create(user=self.user, query='Search 2')

        url = '/api/v1/interactive/search/recent/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(SearchQuery.objects.filter(user=self.user).exists())


class SmartFiltersAPITestCase(APITestCase):
    """Test cases for Smart Filters API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_filter(self):
        """Test creating a smart filter"""
        url = '/api/v1/interactive/smart-filters/'
        data = {
            'name': 'Hot Leads',
            'entity_type': 'lead',
            'filter_config': {'score__gte': 80, 'status': 'qualified'},
            'icon': 'fire',
            'color': 'red'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SmartFilter.objects.filter(name='Hot Leads').exists())

    def test_record_filter_use(self):
        """Test recording filter usage"""
        filter_obj = SmartFilter.objects.create(
            user=self.user,
            name='Test Filter',
            entity_type='contact',
            filter_config={}
        )

        url = f'/api/v1/interactive/smart-filters/{filter_obj.id}/use/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filter_obj.refresh_from_db()
        self.assertEqual(filter_obj.use_count, 1)


class QuickActionsAPITestCase(APITestCase):
    """Test cases for Quick Actions API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_quick_action(self):
        """Test creating a quick action"""
        url = '/api/v1/interactive/quick-actions/'
        data = {
            'name': 'New Contact',
            'action_type': 'create',
            'url': '/contacts/new',
            'icon': 'user-plus',
            'color': 'blue',
            'shortcut': 'Ctrl+Shift+C'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_toggle_pin(self):
        """Test toggling pin status"""
        action = QuickAction.objects.create(
            user=self.user,
            name='Test Action',
            action_type='navigation',
            url='/test',
            is_pinned=False
        )

        url = f'/api/v1/interactive/quick-actions/{action.id}/toggle_pin/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        action.refresh_from_db()
        self.assertTrue(action.is_pinned)

    def test_get_pinned_actions(self):
        """Test getting only pinned actions"""
        QuickAction.objects.create(
            user=self.user,
            name='Pinned',
            action_type='navigation',
            url='/test1',
            is_pinned=True
        )
        QuickAction.objects.create(
            user=self.user,
            name='Not Pinned',
            action_type='navigation',
            url='/test2',
            is_pinned=False
        )

        url = '/api/v1/interactive/quick-actions/pinned/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Pinned')


class RecommendationEngineTestCase(TestCase):
    """Test cases for the AI Recommendation Engine"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_engine_initialization(self):
        """Test recommendation engine initializes correctly"""
        engine = RecommendationEngine(self.user)
        self.assertEqual(engine.user, self.user)
        self.assertEqual(engine.max_recommendations, 10)

    def test_generate_recommendations_returns_list(self):
        """Test that generate_recommendations returns a list"""
        result = generate_recommendations(self.user)
        self.assertIsInstance(result, list)

    def test_recommendations_capped_at_max(self):
        """Test that recommendations are capped at max_recommendations"""
        engine = RecommendationEngine(self.user)
        engine.max_recommendations = 3

        # Even if many are generated, only 3 should be returned
        result = engine.generate_all()
        self.assertLessEqual(len(result), 3)

    def test_expired_recommendations_cleared(self):
        """Test that expired recommendations are marked as expired"""
        AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='action',
            title='Expired',
            description='Test',
            impact='low',
            status='active',
            expires_at=timezone.now() - timedelta(days=1)
        )

        engine = RecommendationEngine(self.user)
        engine._clear_expired()

        rec = AIRecommendation.objects.get(title='Expired')
        self.assertEqual(rec.status, 'expired')
