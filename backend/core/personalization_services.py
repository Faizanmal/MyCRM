"""
Personalization Services - Adaptive UI, smart defaults, and user experience management.
"""

import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class PreferenceService:
    """Service for managing user preferences."""

    def get_user_preferences(self, user_id: str) -> dict[str, Any]:
        """Get all preferences for a user."""
        # In production, query UserPreferenceProfile
        return {
            'dashboard': {
                'default_dashboard': 'overview',
                'layout': {},
                'pinned_widgets': ['revenue_chart', 'pipeline', 'tasks'],
                'hidden_widgets': [],
            },
            'navigation': {
                'favorite_pages': ['/deals', '/contacts', '/reports'],
                'sidebar_collapsed': False,
                'sidebar_favorites': ['deals', 'contacts', 'tasks'],
            },
            'display': {
                'list_density': 'comfortable',
                'default_list_view': 'table',
                'items_per_page': 25,
            },
            'notifications': {
                'channels': {
                    'email': True,
                    'push': True,
                    'in_app': True,
                    'sms': False,
                },
                'quiet_hours': {'start': '22:00', 'end': '08:00', 'enabled': False},
                'digest': 'realtime',
            },
            'smart_features': {
                'suggestions_enabled': True,
                'predictive_actions_enabled': True,
                'auto_complete_enabled': True,
            },
        }

    def update_preferences(self, user_id: str, section: str, updates: dict) -> dict:
        """Update a section of user preferences."""
        # In production, update UserPreferenceProfile
        return {'success': True, 'section': section, 'updates': updates}

    def reset_preferences(self, user_id: str, section: str | None = None) -> dict:
        """Reset preferences to defaults."""
        return {'success': True, 'reset_section': section or 'all'}


class BehaviorTrackingService:
    """Service for tracking and analyzing user behavior."""

    def track_event(
        self,
        user_id: str,
        event_type: str,
        event_category: str,
        event_target: str,
        event_data: dict = None,
        page_path: str = '',
        session_id: str = '',
        device_type: str = 'desktop',
        duration_ms: int = None,
    ) -> dict:
        """Track a user behavior event."""
        event = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'event_type': event_type,
            'event_category': event_category,
            'event_target': event_target,
            'event_data': event_data or {},
            'page_path': page_path,
            'session_id': session_id,
            'device_type': device_type,
            'duration_ms': duration_ms,
            'timestamp': timezone.now().isoformat(),
        }

        # In production, save to UserBehaviorEvent
        return event

    def get_behavior_summary(self, user_id: str, days: int = 30) -> dict:
        """Get summary of user behavior."""
        # In production, aggregate from UserBehaviorEvent
        return {
            'total_sessions': 45,
            'avg_session_duration_minutes': 23,
            'most_visited_pages': [
                {'path': '/deals', 'visits': 120},
                {'path': '/contacts', 'visits': 85},
                {'path': '/tasks', 'visits': 62},
            ],
            'most_used_features': [
                {'feature': 'search', 'uses': 230},
                {'feature': 'filters', 'uses': 180},
                {'feature': 'exports', 'uses': 45},
            ],
            'peak_usage_hours': [9, 10, 11, 14, 15],
            'device_breakdown': {'desktop': 85, 'mobile': 12, 'tablet': 3},
        }

    def get_page_analytics(self, user_id: str, page_path: str) -> dict:
        """Get analytics for a specific page."""
        return {
            'page_path': page_path,
            'total_visits': 45,
            'avg_time_on_page_seconds': 120,
            'common_actions': ['filter', 'search', 'create'],
            'common_next_pages': ['/deals/detail', '/contacts'],
        }


class SmartDefaultsService:
    """Service for AI-learned default values."""

    def get_smart_defaults(
        self,
        user_id: str,
        entity_type: str,
        context: dict = None,
    ) -> dict[str, Any]:
        """Get smart defaults for a form/entity."""
        # In production, query SmartDefault and apply ML model
        defaults = {}

        if entity_type == 'opportunity':
            defaults = {
                'stage': 'qualification',
                'probability': 20,
                'expected_close_days': 30,
                'owner': user_id,
            }
        elif entity_type == 'task':
            defaults = {
                'priority': 'medium',
                'due_days_from_now': 3,
                'assignee': user_id,
            }
        elif entity_type == 'contact':
            defaults = {
                'status': 'active',
                'source': 'direct',
            }

        return {
            'entity_type': entity_type,
            'defaults': defaults,
            'confidence_scores': dict.fromkeys(defaults.keys(), 0.85),
        }

    def learn_from_input(
        self,
        user_id: str,
        entity_type: str,
        field_name: str,
        value: Any,
        context: dict = None,
        was_default_used: bool = False,
    ) -> None:
        """Learn from user input to improve defaults."""
        # In production, update SmartDefault model
        # Track if user accepted or overrode the default
        pass

    def get_suggestions(
        self,
        user_id: str,
        entity_type: str,
        field_name: str,
        partial_value: str = '',
        limit: int = 5,
    ) -> list[dict]:
        """Get smart suggestions for a field."""
        # In production, use ML to generate suggestions
        return [
            {'value': f'Suggestion {i}', 'confidence': 0.9 - (i * 0.1), 'source': 'history'}
            for i in range(1, limit + 1)
        ]


class ContextualHelpService:
    """Service for managing contextual help content."""

    def get_help_for_page(
        self,
        user_id: str,
        page_path: str,
        user_segment: str = 'all',
    ) -> list[dict]:
        """Get relevant help content for a page."""
        # In production, query ContextualHelp and filter by user progress
        return [
            {
                'id': '1',
                'title': 'Quick Tip: Filtering',
                'content': 'Use the filter button to narrow down your results.',
                'type': 'tooltip',
                'element_selector': '[data-filter-button]',
                'position': 'bottom',
                'trigger': 'auto',
            }
        ]

    def mark_help_seen(self, user_id: str, help_id: str) -> None:
        """Mark help content as seen by user."""
        # In production, create/update UserHelpProgress
        pass

    def dismiss_help(self, user_id: str, help_id: str) -> None:
        """Dismiss help content."""
        # In production, update UserHelpProgress
        pass

    def rate_help(self, user_id: str, help_id: str, helpful: bool) -> None:
        """Rate help content as helpful or not."""
        # In production, update UserHelpProgress
        pass


class OnboardingService:
    """Service for managing onboarding tours."""

    def get_user_tours(self, user_id: str) -> list[dict]:
        """Get all tours relevant to a user."""
        # In production, query OnboardingTour and UserTourProgress
        return [
            {
                'id': '1',
                'name': 'Getting Started',
                'slug': 'getting-started',
                'description': 'Learn the basics of the CRM',
                'total_steps': 5,
                'current_step': 2,
                'status': 'in_progress',
                'progress_percent': 40,
            },
            {
                'id': '2',
                'name': 'Advanced Features',
                'slug': 'advanced-features',
                'description': 'Discover power user features',
                'total_steps': 8,
                'current_step': 0,
                'status': 'not_started',
                'progress_percent': 0,
            },
        ]

    def get_tour_steps(self, tour_slug: str) -> list[dict]:
        """Get all steps for a tour."""
        # In production, query OnboardingStep
        return [
            {
                'order': 1,
                'title': 'Welcome to MyCRM',
                'content': 'Let\'s take a quick tour of the main features.',
                'page_path': '/',
                'element_selector': '.dashboard',
                'position': 'center',
            },
            {
                'order': 2,
                'title': 'Navigation',
                'content': 'Use the sidebar to navigate between different sections.',
                'page_path': '/',
                'element_selector': '.sidebar',
                'position': 'right',
            },
        ]

    def start_tour(self, user_id: str, tour_slug: str) -> dict:
        """Start a tour for a user."""
        return {
            'tour_slug': tour_slug,
            'status': 'in_progress',
            'current_step': 1,
            'started_at': timezone.now().isoformat(),
        }

    def complete_step(self, user_id: str, tour_slug: str, step: int) -> dict:
        """Complete a tour step."""
        return {
            'tour_slug': tour_slug,
            'completed_step': step,
            'next_step': step + 1,
        }

    def skip_tour(self, user_id: str, tour_slug: str) -> dict:
        """Skip a tour."""
        return {
            'tour_slug': tour_slug,
            'status': 'skipped',
            'skipped_at': timezone.now().isoformat(),
        }


class AdaptiveUIService:
    """Service for adaptive UI based on user behavior."""

    def get_ui_adaptations(self, user_id: str) -> dict[str, Any]:
        """Get UI adaptations for a user based on behavior."""
        behavior = self._analyze_behavior(user_id)

        adaptations = {
            'dashboard_widgets': self._get_recommended_widgets(behavior),
            'sidebar_order': self._get_recommended_sidebar_order(behavior),
            'quick_actions': self._get_recommended_quick_actions(behavior),
            'feature_highlights': self._get_unused_features(behavior),
        }

        return adaptations

    def apply_rule(self, user_id: str, rule_id: str) -> dict:
        """Apply a specific adaptive UI rule."""
        # In production, get rule from AdaptiveUIRule and apply actions
        return {'applied': True, 'rule_id': rule_id}

    def _analyze_behavior(self, user_id: str) -> dict:
        """Analyze user behavior patterns."""
        return {
            'primary_focus': 'sales',  # sales, support, marketing
            'experience_level': 'intermediate',  # new, intermediate, advanced
            'feature_usage': {
                'deals': 0.8,
                'contacts': 0.6,
                'reports': 0.3,
                'automation': 0.1,
            },
            'time_patterns': {
                'peak_hours': [9, 10, 11, 14, 15],
                'avg_session_minutes': 25,
            },
        }

    def _get_recommended_widgets(self, behavior: dict) -> list[str]:
        """Get recommended dashboard widgets."""
        focus = behavior.get('primary_focus', 'sales')

        widget_map = {
            'sales': ['pipeline', 'revenue_chart', 'deals_by_stage', 'top_deals'],
            'support': ['tickets', 'response_time', 'satisfaction', 'queue'],
            'marketing': ['campaigns', 'leads_chart', 'conversion_funnel', 'sources'],
        }

        return widget_map.get(focus, ['overview', 'tasks', 'activities'])

    def _get_recommended_sidebar_order(self, behavior: dict) -> list[str]:
        """Get recommended sidebar order."""
        usage = behavior.get('feature_usage', {})

        # Sort by usage frequency
        sorted_items = sorted(usage.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_items]

    def _get_recommended_quick_actions(self, behavior: dict) -> list[dict]:
        """Get recommended quick actions."""
        focus = behavior.get('primary_focus', 'sales')

        actions = {
            'sales': [
                {'action': 'create_deal', 'label': 'New Deal', 'icon': 'plus'},
                {'action': 'log_call', 'label': 'Log Call', 'icon': 'phone'},
            ],
            'support': [
                {'action': 'create_ticket', 'label': 'New Ticket', 'icon': 'plus'},
                {'action': 'view_queue', 'label': 'View Queue', 'icon': 'list'},
            ],
        }

        return actions.get(focus, [])

    def _get_unused_features(self, behavior: dict) -> list[dict]:
        """Get features user hasn't discovered yet."""
        usage = behavior.get('feature_usage', {})

        # Features with low or no usage
        unused = [k for k, v in usage.items() if v < 0.2]

        return [
            {'feature': f, 'description': f'Discover {f} to boost productivity'}
            for f in unused
        ]


class InsightService:
    """Service for generating personalized insights."""

    def get_user_insights(self, user_id: str, limit: int = 5) -> list[dict]:
        """Get AI-generated insights for a user."""
        # In production, query UserInsight and generate new ones
        return [
            {
                'id': '1',
                'type': 'productivity_tip',
                'title': 'Optimize Your Morning Routine',
                'description': 'You\'re most productive between 9-11 AM. Consider scheduling important calls during this time.',
                'recommendation': 'Block 9-11 AM for high-priority tasks',
                'confidence': 0.85,
                'status': 'new',
            },
            {
                'id': '2',
                'type': 'unused_feature',
                'title': 'Try Email Sequences',
                'description': 'You send a lot of follow-up emails manually. Email sequences could save you 2+ hours per week.',
                'recommendation': 'Set up your first email sequence',
                'confidence': 0.92,
                'status': 'new',
            },
        ]

    def generate_insights(self, user_id: str) -> list[dict]:
        """Generate new insights based on recent behavior."""
        BehaviorTrackingService().get_behavior_summary(user_id)
        insights = []

        # Analyze patterns and generate insights
        # In production, use ML models for this

        return insights

    def act_on_insight(self, user_id: str, insight_id: str, action: str) -> dict:
        """Record user action on an insight."""
        return {
            'insight_id': insight_id,
            'action': action,  # viewed, acted, dismissed
            'timestamp': timezone.now().isoformat(),
        }


class QuickActionService:
    """Service for managing user quick actions."""

    def get_user_quick_actions(self, user_id: str) -> list[dict]:
        """Get user's configured quick actions."""
        # In production, query QuickAction
        return [
            {
                'id': '1',
                'name': 'New Deal',
                'icon': 'plus-circle',
                'color': 'blue',
                'action_type': 'create',
                'action_config': {'entity': 'deal'},
                'keyboard_shortcut': 'Ctrl+Shift+D',
            },
            {
                'id': '2',
                'name': 'Search Contacts',
                'icon': 'search',
                'color': 'green',
                'action_type': 'search',
                'action_config': {'entity': 'contact'},
                'keyboard_shortcut': 'Ctrl+Shift+C',
            },
        ]

    def create_quick_action(self, user_id: str, action_data: dict) -> dict:
        """Create a new quick action."""
        return {
            'id': str(uuid.uuid4()),
            **action_data,
            'created_at': timezone.now().isoformat(),
        }

    def update_quick_action(self, user_id: str, action_id: str, updates: dict) -> dict:
        """Update a quick action."""
        return {'id': action_id, **updates}

    def delete_quick_action(self, user_id: str, action_id: str) -> bool:
        """Delete a quick action."""
        return True

    def reorder_quick_actions(self, user_id: str, action_ids: list[str]) -> list[dict]:
        """Reorder quick actions."""
        return [{'id': aid, 'order': i} for i, aid in enumerate(action_ids)]


class PersonalizationEngine:
    """Main engine orchestrating all personalization features."""

    def __init__(self):
        self.preference_service = PreferenceService()
        self.behavior_service = BehaviorTrackingService()
        self.defaults_service = SmartDefaultsService()
        self.help_service = ContextualHelpService()
        self.onboarding_service = OnboardingService()
        self.adaptive_service = AdaptiveUIService()
        self.insight_service = InsightService()

    def get_personalized_experience(self, user_id: str, page_path: str) -> dict[str, Any]:
        """Get complete personalized experience for current context."""
        return {
            'preferences': self.preference_service.get_user_preferences(user_id),
            'ui_adaptations': self.adaptive_service.get_ui_adaptations(user_id),
            'contextual_help': self.help_service.get_help_for_page(user_id, page_path),
            'active_tours': [
                t for t in self.onboarding_service.get_user_tours(user_id)
                if t['status'] == 'in_progress'
            ],
            'insights': self.insight_service.get_user_insights(user_id, limit=3),
        }

    def track_and_learn(
        self,
        user_id: str,
        event_type: str,
        event_data: dict,
        page_path: str,
        session_id: str,
    ) -> None:
        """Track user behavior and trigger learning."""
        # Track the event
        self.behavior_service.track_event(
            user_id=user_id,
            event_type=event_type,
            event_category=self._categorize_event(event_type),
            event_target=event_data.get('target', ''),
            event_data=event_data,
            page_path=page_path,
            session_id=session_id,
        )

        # Trigger learning for smart defaults
        if event_type == 'form_submit':
            for field, value in event_data.get('fields', {}).items():
                self.defaults_service.learn_from_input(
                    user_id=user_id,
                    entity_type=event_data.get('entity_type', ''),
                    field_name=field,
                    value=value,
                )

    def _categorize_event(self, event_type: str) -> str:
        """Categorize an event type."""
        categories = {
            'page_view': 'navigation',
            'click': 'action',
            'search': 'action',
            'filter': 'action',
            'form_submit': 'action',
            'preference_change': 'preference',
        }
        return categories.get(event_type, 'other')
