from rest_framework import serializers
from .models import (
    SalesRepProfile, RoutingRule, LeadAssignment, EscalationRule,
    RebalancingEvent, RoutingAnalytics, SkillCertification,
    RepSkillAssignment, TerritoryDefinition, LeadQualityScore
)


class SalesRepProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    conversion_rate = serializers.ReadOnlyField()
    capacity_utilization = serializers.ReadOnlyField()
    is_at_capacity = serializers.ReadOnlyField()
    
    class Meta:
        model = SalesRepProfile
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'max_leads_per_day', 'max_active_leads', 'current_lead_count',
            'is_available', 'availability_schedule',
            'industries', 'certifications', 'languages', 'expertise_level',
            'regions', 'countries', 'timezones',
            'min_deal_size', 'max_deal_size', 'preferred_deal_size',
            'total_leads_assigned', 'total_leads_converted', 'avg_conversion_time_days',
            'win_rate', 'avg_deal_size', 'response_time_minutes', 'customer_satisfaction',
            'overall_performance_score', 'last_performance_update',
            'last_assignment_at', 'assignment_weight',
            'conversion_rate', 'capacity_utilization', 'is_at_capacity',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'current_lead_count', 'total_leads_assigned', 'total_leads_converted',
            'win_rate', 'avg_deal_size', 'response_time_minutes',
            'overall_performance_score', 'last_performance_update', 'last_assignment_at'
        ]


class SalesRepProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRepProfile
        fields = [
            'user', 'max_leads_per_day', 'max_active_leads',
            'is_available', 'availability_schedule',
            'industries', 'certifications', 'languages', 'expertise_level',
            'regions', 'countries', 'timezones',
            'min_deal_size', 'max_deal_size', 'preferred_deal_size',
            'assignment_weight'
        ]


class RoutingRuleSerializer(serializers.ModelSerializer):
    target_rep_names = serializers.SerializerMethodField()
    fallback_rep_name = serializers.CharField(source='fallback_rep.get_full_name', read_only=True)
    
    class Meta:
        model = RoutingRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'priority',
            'criteria', 'target_reps', 'target_rep_names', 'target_teams',
            'fallback_rep', 'fallback_rep_name',
            'is_active', 'respect_capacity', 'consider_availability',
            'total_matches', 'total_assignments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_matches', 'total_assignments']
    
    def get_target_rep_names(self, obj):
        return [rep.get_full_name() for rep in obj.target_reps.all()]


class LeadAssignmentSerializer(serializers.ModelSerializer):
    lead_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    previous_assignee_name = serializers.CharField(source='previous_assignee.get_full_name', read_only=True)
    response_time_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = LeadAssignment
        fields = [
            'id', 'lead', 'lead_name',
            'assigned_to', 'assigned_to_name',
            'assigned_by', 'assigned_by_name',
            'previous_assignee', 'previous_assignee_name',
            'assignment_method', 'routing_rule',
            'match_score', 'match_factors',
            'status', 'status_reason',
            'assigned_at', 'accepted_at', 'first_response_at',
            'response_time_minutes',
            'outcome', 'outcome_at'
        ]
        read_only_fields = ['id', 'assigned_at']
    
    def get_lead_name(self, obj):
        return f"{obj.lead.first_name} {obj.lead.last_name}"


class EscalationRuleSerializer(serializers.ModelSerializer):
    escalate_to_name = serializers.CharField(source='escalate_to.get_full_name', read_only=True)
    
    class Meta:
        model = EscalationRule
        fields = [
            'id', 'name', 'description',
            'trigger_type', 'trigger_config',
            'escalate_to', 'escalate_to_name', 'escalate_to_manager',
            'notify_original_rep', 'notify_manager',
            'wait_hours', 'is_active', 'priority',
            'total_escalations',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_escalations']


class RebalancingEventSerializer(serializers.ModelSerializer):
    triggered_by_name = serializers.CharField(source='triggered_by.get_full_name', read_only=True)
    
    class Meta:
        model = RebalancingEvent
        fields = [
            'id', 'trigger_reason',
            'triggered_by', 'triggered_by_name',
            'leads_moved', 'movements',
            'before_distribution', 'after_distribution',
            'started_at', 'completed_at'
        ]


class RoutingAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutingAnalytics
        fields = [
            'id', 'date',
            'total_leads_routed', 'auto_routed', 'manual_routed',
            'escalations', 'rebalanced',
            'avg_match_score', 'avg_response_time_minutes', 'conversion_rate',
            'routing_by_method', 'routing_by_rule', 'rep_distribution'
        ]


class SkillCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCertification
        fields = [
            'id', 'name', 'code', 'skill_type', 'description',
            'routing_weight', 'is_active', 'created_at'
        ]


class RepSkillAssignmentSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    rep_name = serializers.CharField(source='rep.user.get_full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = RepSkillAssignment
        fields = [
            'id', 'rep', 'rep_name', 'skill', 'skill_name',
            'proficiency_level', 'certified_date', 'expiry_date',
            'verified', 'verified_by', 'is_expired', 'created_at'
        ]


class TerritoryDefinitionSerializer(serializers.ModelSerializer):
    primary_rep_name = serializers.CharField(source='primary_rep.get_full_name', read_only=True)
    
    class Meta:
        model = TerritoryDefinition
        fields = [
            'id', 'name', 'code', 'description',
            'countries', 'states', 'cities', 'postal_codes',
            'primary_rep', 'primary_rep_name', 'backup_reps',
            'is_active', 'created_at', 'updated_at'
        ]


class LeadQualityScoreSerializer(serializers.ModelSerializer):
    lead_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LeadQualityScore
        fields = [
            'id', 'lead', 'lead_name',
            'overall_score', 'fit_score', 'engagement_score',
            'intent_score', 'timing_score',
            'scoring_factors',
            'recommended_rep_ids', 'recommended_rule_id', 'priority_tier',
            'model_version', 'scored_at'
        ]
    
    def get_lead_name(self, obj):
        return f"{obj.lead.first_name} {obj.lead.last_name}"


# Request serializers
class RouteLeadSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
    force_rule_id = serializers.UUIDField(required=False, allow_null=True)


class ReassignLeadSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
    new_assignee_id = serializers.IntegerField()
    reason = serializers.CharField(required=False, default='')


class TriggerRebalancingSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(
        choices=['overload', 'underperformance', 'availability', 'manual', 'scheduled'],
        default='manual'
    )


class GetRecommendationsSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
