from django.contrib import admin

from .models import (
    LeadEnrichmentData,
    LeadScore,
    QualificationCriteria,
    QualificationWorkflow,
    ScoringRule,
    WorkflowExecution,
)


@admin.register(ScoringRule)
class ScoringRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'field_name', 'operator', 'points', 'is_active', 'priority', 'created_at']
    list_filter = ['rule_type', 'is_active', 'operator']
    search_fields = ['name', 'description', 'field_name']
    ordering = ['-priority', 'name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'rule_type', 'is_active')
        }),
        ('Rule Configuration', {
            'fields': ('field_name', 'operator', 'value', 'points', 'priority')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(QualificationCriteria)
class QualificationCriteriaAdmin(admin.ModelAdmin):
    list_display = ['name', 'stage', 'minimum_score', 'time_constraint_days', 'is_active', 'created_at']
    list_filter = ['stage', 'is_active']
    search_fields = ['name']
    ordering = ['stage', 'minimum_score']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'stage', 'is_active')
        }),
        ('Requirements', {
            'fields': ('minimum_score', 'required_fields', 'required_actions', 'time_constraint_days')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LeadScore)
class LeadScoreAdmin(admin.ModelAdmin):
    list_display = ['lead', 'score', 'previous_score', 'qualification_stage', 'calculated_at']
    list_filter = ['qualification_stage', 'calculated_at']
    search_fields = ['lead__name', 'lead__email']
    ordering = ['-calculated_at']
    readonly_fields = ['lead', 'score', 'previous_score', 'score_breakdown', 'qualification_stage',
                       'demographic_score', 'behavioral_score', 'firmographic_score', 'engagement_score',
                       'calculated_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(QualificationWorkflow)
class QualificationWorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'action_type', 'is_active', 'priority', 'execution_count', 'last_executed_at']
    list_filter = ['trigger_type', 'action_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-priority', 'name']
    readonly_fields = ['execution_count', 'last_executed_at', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active', 'priority')
        }),
        ('Trigger Configuration', {
            'fields': ('trigger_type', 'trigger_config')
        }),
        ('Action Configuration', {
            'fields': ('action_type', 'action_config')
        }),
        ('Conditions', {
            'fields': ('conditions',),
            'classes': ('collapse',)
        }),
        ('Execution Statistics', {
            'fields': ('execution_count', 'last_executed_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'lead', 'status', 'started_at', 'completed_at']
    list_filter = ['status', 'started_at', 'workflow']
    search_fields = ['workflow__name', 'lead__name', 'lead__email']
    ordering = ['-started_at']
    readonly_fields = ['workflow', 'lead', 'status', 'trigger_data', 'result_data',
                       'error_message', 'started_at', 'completed_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LeadEnrichmentData)
class LeadEnrichmentDataAdmin(admin.ModelAdmin):
    list_display = ['lead', 'source', 'company_size', 'company_industry', 'is_verified', 'confidence_score', 'enriched_at']
    list_filter = ['source', 'is_verified', 'enriched_at']
    search_fields = ['lead__name', 'lead__email', 'company_industry', 'job_title']
    ordering = ['-enriched_at']
    readonly_fields = ['enriched_at']

    fieldsets = (
        ('Lead Information', {
            'fields': ('lead', 'source', 'is_verified', 'confidence_score')
        }),
        ('Company Information', {
            'fields': ('company_size', 'company_revenue', 'company_industry', 'company_location')
        }),
        ('Contact Information', {
            'fields': ('job_title', 'job_level', 'social_profiles')
        }),
        ('Additional Data', {
            'fields': ('technologies', 'data'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('enriched_at',),
            'classes': ('collapse',)
        }),
    )
