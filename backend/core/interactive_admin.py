"""
Interactive Features Admin Configuration
"""

from django.contrib import admin
from .interactive_models import (
    UserPreferences,
    OnboardingProgress,
    AIRecommendation,
    SearchQuery,
    SmartFilter,
    QuickAction,
)


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'sidebar_collapsed', 'updated_at']
    list_filter = ['theme', 'sidebar_collapsed']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OnboardingProgress)
class OnboardingProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'tour_completed', 'onboarding_xp', 'started_at', 'completed_at']
    list_filter = ['tour_completed', 'tour_dismissed']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['started_at', 'completed_at', 'tour_completed_at']


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'recommendation_type', 'impact', 'status', 'created_at']
    list_filter = ['recommendation_type', 'impact', 'status', 'dismissable']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'dismissed_at', 'completed_at']
    date_hierarchy = 'created_at'


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'results_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(SmartFilter)
class SmartFilterAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'entity_type', 'use_count', 'is_shared', 'is_default']
    list_filter = ['entity_type', 'is_shared', 'is_default']
    search_fields = ['name', 'user__username']
    readonly_fields = ['use_count', 'last_used_at', 'created_at', 'updated_at']


@admin.register(QuickAction)
class QuickActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'action_type', 'is_pinned', 'use_count', 'order']
    list_filter = ['action_type', 'is_pinned']
    search_fields = ['name', 'user__username']
    readonly_fields = ['use_count', 'created_at', 'updated_at']
