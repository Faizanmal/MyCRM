"""
Customer Success Admin Configuration
"""

from django.contrib import admin

from .models import (
    CustomerAccount,
    CustomerMilestone,
    CustomerNote,
    CustomerSuccessAnalytics,
    ExpansionOpportunity,
    HealthScore,
    HealthScoreConfig,
    NPSSurvey,
    PlaybookExecution,
    PlaybookStep,
    RenewalOpportunity,
    SuccessPlaybook,
)


class HealthScoreInline(admin.TabularInline):
    model = HealthScore
    extra = 0
    readonly_fields = ['calculated_at']
    max_num = 5


class CustomerMilestoneInline(admin.TabularInline):
    model = CustomerMilestone
    extra = 1


@admin.register(CustomerAccount)
class CustomerAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'arr', 'customer_success_manager', 'is_active', 'contract_end']
    list_filter = ['tier', 'is_active', 'onboarding_complete']
    search_fields = ['name']
    inlines = [HealthScoreInline, CustomerMilestoneInline]
    raw_id_fields = ['primary_contact', 'customer_success_manager']


@admin.register(HealthScore)
class HealthScoreAdmin(admin.ModelAdmin):
    list_display = ['account', 'score', 'status', 'usage_score', 'engagement_score', 'calculated_at']
    list_filter = ['status', 'calculated_at']
    search_fields = ['account__name']


@admin.register(HealthScoreConfig)
class HealthScoreConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'healthy_threshold', 'critical_threshold', 'is_active']


class PlaybookStepInline(admin.TabularInline):
    model = PlaybookStep
    extra = 1


@admin.register(SuccessPlaybook)
class SuccessPlaybookAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'is_active', 'created_at']
    list_filter = ['trigger_type', 'is_active']
    inlines = [PlaybookStepInline]


@admin.register(PlaybookExecution)
class PlaybookExecutionAdmin(admin.ModelAdmin):
    list_display = ['account', 'playbook', 'status', 'current_step', 'started_at']
    list_filter = ['status', 'playbook']
    search_fields = ['account__name']


@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ['account', 'note_type', 'title', 'created_by', 'is_pinned', 'created_at']
    list_filter = ['note_type', 'is_pinned']
    search_fields = ['account__name', 'title', 'content']


@admin.register(RenewalOpportunity)
class RenewalOpportunityAdmin(admin.ModelAdmin):
    list_display = ['account', 'renewal_date', 'status', 'risk_level', 'current_arr', 'projected_arr']
    list_filter = ['status', 'risk_level']
    search_fields = ['account__name']


@admin.register(ExpansionOpportunity)
class ExpansionOpportunityAdmin(admin.ModelAdmin):
    list_display = ['account', 'name', 'expansion_type', 'status', 'potential_arr_increase', 'probability']
    list_filter = ['expansion_type', 'status']
    search_fields = ['account__name', 'name']


@admin.register(NPSSurvey)
class NPSSurveyAdmin(admin.ModelAdmin):
    list_display = ['account', 'contact', 'score', 'classification', 'sent_at', 'responded_at']
    list_filter = ['classification', 'sent_at']
    search_fields = ['account__name']


@admin.register(CustomerSuccessAnalytics)
class CustomerSuccessAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_accounts', 'total_arr', 'healthy_accounts', 'at_risk_accounts', 'nps_score']
    date_hierarchy = 'date'
