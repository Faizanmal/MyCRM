from django.contrib import admin
from .models import (
    SalesRepProfile, RoutingRule, LeadAssignment, EscalationRule,
    RebalancingEvent, RoutingAnalytics, SkillCertification,
    RepSkillAssignment, TerritoryDefinition, LeadQualityScore
)


@admin.register(SalesRepProfile)
class SalesRepProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'expertise_level', 'is_available', 'current_lead_count', 'max_active_leads', 'win_rate', 'overall_performance_score']
    list_filter = ['expertise_level', 'is_available']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['current_lead_count', 'total_leads_assigned', 'total_leads_converted', 'win_rate', 'overall_performance_score']


@admin.register(RoutingRule)
class RoutingRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'priority', 'is_active', 'total_assignments']
    list_filter = ['rule_type', 'is_active', 'priority']
    search_fields = ['name', 'description']


@admin.register(LeadAssignment)
class LeadAssignmentAdmin(admin.ModelAdmin):
    list_display = ['lead', 'assigned_to', 'assignment_method', 'match_score', 'status', 'assigned_at']
    list_filter = ['assignment_method', 'status', 'assigned_at']
    search_fields = ['lead__first_name', 'lead__last_name', 'assigned_to__username']


@admin.register(EscalationRule)
class EscalationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'escalate_to', 'wait_hours', 'is_active', 'total_escalations']
    list_filter = ['trigger_type', 'is_active']
    search_fields = ['name']


@admin.register(RebalancingEvent)
class RebalancingEventAdmin(admin.ModelAdmin):
    list_display = ['trigger_reason', 'triggered_by', 'leads_moved', 'started_at', 'completed_at']
    list_filter = ['trigger_reason', 'started_at']


@admin.register(RoutingAnalytics)
class RoutingAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_leads_routed', 'auto_routed', 'escalations', 'avg_match_score']
    list_filter = ['date']


@admin.register(SkillCertification)
class SkillCertificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'skill_type', 'routing_weight', 'is_active']
    list_filter = ['skill_type', 'is_active']
    search_fields = ['name', 'code']


@admin.register(RepSkillAssignment)
class RepSkillAssignmentAdmin(admin.ModelAdmin):
    list_display = ['rep', 'skill', 'proficiency_level', 'verified', 'certified_date']
    list_filter = ['proficiency_level', 'verified']


@admin.register(TerritoryDefinition)
class TerritoryDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'primary_rep', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(LeadQualityScore)
class LeadQualityScoreAdmin(admin.ModelAdmin):
    list_display = ['lead', 'overall_score', 'fit_score', 'engagement_score', 'priority_tier', 'scored_at']
    list_filter = ['priority_tier', 'scored_at']
