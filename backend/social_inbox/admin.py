"""
Social Inbox Admin Configuration
"""

from django.contrib import admin
from .models import (
    SocialAccount, SocialConversation, SocialMessage,
    SocialMonitoringRule, SocialPost, SocialAnalytics
)


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ['account_name', 'platform', 'account_handle', 'status', 'last_sync_at']
    list_filter = ['platform', 'status', 'auto_sync_enabled']
    search_fields = ['account_name', 'account_handle']
    readonly_fields = ['created_at', 'updated_at', 'last_sync_at']


class SocialMessageInline(admin.TabularInline):
    model = SocialMessage
    extra = 0
    readonly_fields = ['platform_created_at', 'created_at']
    fields = ['direction', 'content', 'is_read', 'platform_created_at']


@admin.register(SocialConversation)
class SocialConversationAdmin(admin.ModelAdmin):
    list_display = ['participant_name', 'social_account', 'conversation_type', 'status', 'priority', 'last_message_at']
    list_filter = ['status', 'priority', 'conversation_type', 'sentiment_label']
    search_fields = ['participant_name', 'participant_handle']
    readonly_fields = ['created_at', 'updated_at', 'first_message_at', 'last_message_at']
    inlines = [SocialMessageInline]


@admin.register(SocialMonitoringRule)
class SocialMonitoringRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'is_active', 'matches_count', 'last_matched_at']
    list_filter = ['rule_type', 'is_active']
    search_fields = ['name', 'keywords']
    readonly_fields = ['matches_count', 'last_matched_at', 'created_at']


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ['content_preview', 'status', 'scheduled_at', 'published_at']
    list_filter = ['status']
    readonly_fields = ['published_at', 'created_at', 'updated_at']
    filter_horizontal = ['social_accounts']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(SocialAnalytics)
class SocialAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['social_account', 'date', 'followers_count', 'impressions', 'engagement_rate']
    list_filter = ['social_account__platform', 'date']
    date_hierarchy = 'date'
