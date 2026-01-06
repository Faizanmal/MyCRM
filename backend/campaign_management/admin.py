from django.contrib import admin

from .models import Campaign, CampaignRecipient, CampaignSegment, EmailTemplate


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'campaign_type', 'sent_count', 'open_rate', 'created_at']
    list_filter = ['status', 'campaign_type', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']


@admin.register(CampaignSegment)
class CampaignSegmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_count', 'created_at']
    search_fields = ['name', 'description']


@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    list_display = ['email', 'campaign', 'status', 'open_count', 'click_count']
    list_filter = ['status', 'campaign']
    search_fields = ['email']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
