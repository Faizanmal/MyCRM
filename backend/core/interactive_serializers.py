"""
Interactive Features Serializers
"""

from rest_framework import serializers

from .interactive_models import (
    AIRecommendation,
    OnboardingProgress,
    QuickAction,
    SearchQuery,
    SmartFilter,
    UserPreferences,
)


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user preferences"""

    class Meta:
        model = UserPreferences
        fields = [
            'id', 'dashboard_layout', 'sidebar_collapsed', 'theme',
            'accent_color', 'enable_sounds', 'enable_desktop_notifications',
            'pinned_actions', 'saved_filters', 'recent_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OnboardingProgressSerializer(serializers.ModelSerializer):
    """Serializer for onboarding progress"""
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = OnboardingProgress
        fields = [
            'completed_steps', 'tour_completed', 'tour_dismissed',
            'tour_completed_at', 'onboarding_xp', 'started_at',
            'completed_at', 'completion_percentage'
        ]
        read_only_fields = ['started_at', 'onboarding_xp']

    def get_completion_percentage(self, obj):
        total_steps = 8  # Total onboarding steps
        completed = len(obj.completed_steps) if obj.completed_steps else 0
        return round((completed / total_steps) * 100, 1)


class CompleteStepSerializer(serializers.Serializer):
    """Serializer for completing an onboarding step"""
    step_id = serializers.CharField(max_length=50)
    xp_reward = serializers.IntegerField(default=50, min_value=0, max_value=500)


class AIRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for AI recommendations"""
    recommendation_type_display = serializers.CharField(
        source='get_recommendation_type_display',
        read_only=True
    )
    impact_display = serializers.CharField(
        source='get_impact_display',
        read_only=True
    )

    class Meta:
        model = AIRecommendation
        fields = [
            'id', 'recommendation_type', 'recommendation_type_display',
            'title', 'description', 'impact', 'impact_display',
            'action_label', 'action_url', 'status', 'dismissable',
            'confidence_score', 'created_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'recommendation_type_display', 'impact_display',
            'confidence_score', 'created_at'
        ]


class SearchQuerySerializer(serializers.ModelSerializer):
    """Serializer for search queries"""

    class Meta:
        model = SearchQuery
        fields = [
            'id', 'query', 'results_count', 'clicked_result_type',
            'clicked_result_id', 'created_at'
        ]
        read_only_fields = ['created_at']


class SmartFilterSerializer(serializers.ModelSerializer):
    """Serializer for smart filters"""

    class Meta:
        model = SmartFilter
        fields = [
            'id', 'name', 'entity_type', 'filter_config', 'icon',
            'color', 'use_count', 'last_used_at', 'is_shared',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['use_count', 'last_used_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class QuickActionSerializer(serializers.ModelSerializer):
    """Serializer for quick actions"""

    class Meta:
        model = QuickAction
        fields = [
            'id', 'name', 'action_type', 'action_config', 'url',
            'icon', 'color', 'shortcut', 'order', 'is_pinned',
            'use_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['use_count', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class GlobalSearchSerializer(serializers.Serializer):
    """Serializer for global search request"""
    query = serializers.CharField(max_length=500)
    types = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=['contact', 'company', 'lead', 'opportunity', 'task']
    )
    limit = serializers.IntegerField(default=10, min_value=1, max_value=50)


class SearchResultSerializer(serializers.Serializer):
    """Serializer for individual search result"""
    id = serializers.CharField()
    type = serializers.CharField()
    title = serializers.CharField()
    subtitle = serializers.CharField(required=False, allow_null=True)
    metadata = serializers.CharField(required=False, allow_null=True)
    score = serializers.FloatField(required=False, allow_null=True)
    starred = serializers.BooleanField(default=False)
    url = serializers.CharField()


class DashboardWidgetConfigSerializer(serializers.Serializer):
    """Serializer for dashboard widget configuration"""
    widget_id = serializers.CharField(max_length=50)
    visible = serializers.BooleanField(default=True)
    order = serializers.IntegerField(default=0)
    size = serializers.ChoiceField(
        choices=['small', 'medium', 'large'],
        default='small'
    )


class SaveDashboardLayoutSerializer(serializers.Serializer):
    """Serializer for saving dashboard layout"""
    widgets = DashboardWidgetConfigSerializer(many=True)
