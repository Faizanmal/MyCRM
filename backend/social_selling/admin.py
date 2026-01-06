"""
Social Selling Admin Configuration
"""

from django.contrib import admin

from .models import (
    EngagementAnalytics,
    LinkedInIntegration,
    ProspectInSequence,
    SocialEngagement,
    SocialInsight,
    SocialPost,
    SocialProfile,
    SocialSellingSequence,
    SocialSellingStep,
)


@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display = ['contact', 'platform', 'username', 'followers_count', 'last_synced']
    list_filter = ['platform', 'is_verified']
    search_fields = ['contact__first_name', 'contact__last_name', 'username']
    raw_id_fields = ['contact']


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ['profile', 'post_type', 'likes_count', 'comments_count', 'posted_at']
    list_filter = ['post_type', 'we_liked', 'we_commented']
    raw_id_fields = ['profile']


@admin.register(SocialEngagement)
class SocialEngagementAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile', 'engagement_type', 'status', 'scheduled_for', 'completed_at']
    list_filter = ['engagement_type', 'status', 'ai_suggested']
    search_fields = ['profile__contact__first_name', 'profile__contact__last_name']
    raw_id_fields = ['user', 'profile', 'post']


@admin.register(LinkedInIntegration)
class LinkedInIntegrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'linkedin_id', 'is_active', 'token_expires_at']
    list_filter = ['is_active']
    search_fields = ['user__email', 'linkedin_id']


class SocialSellingStepInline(admin.TabularInline):
    model = SocialSellingStep
    extra = 1


@admin.register(SocialSellingSequence)
class SocialSellingSequenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_active', 'max_prospects_per_day', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'user__email']
    inlines = [SocialSellingStepInline]


@admin.register(ProspectInSequence)
class ProspectInSequenceAdmin(admin.ModelAdmin):
    list_display = ['profile', 'sequence', 'status', 'current_step', 'next_action_at']
    list_filter = ['status', 'sequence']
    raw_id_fields = ['profile', 'sequence']


@admin.register(SocialInsight)
class SocialInsightAdmin(admin.ModelAdmin):
    list_display = ['profile', 'insight_type', 'title', 'urgency', 'is_actioned', 'discovered_at']
    list_filter = ['insight_type', 'urgency', 'is_actioned']
    search_fields = ['title', 'profile__contact__first_name']
    raw_id_fields = ['profile', 'related_post']


@admin.register(EngagementAnalytics)
class EngagementAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'connections_sent', 'connections_accepted',
                    'messages_sent', 'meetings_booked', 'engagement_score']
    list_filter = ['date']
    search_fields = ['user__email']
    date_hierarchy = 'date'
