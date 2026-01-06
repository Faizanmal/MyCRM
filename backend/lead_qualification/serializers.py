from rest_framework import serializers

from .models import (
    LeadEnrichmentData,
    LeadScore,
    QualificationCriteria,
    QualificationWorkflow,
    ScoringRule,
    WorkflowExecution,
)


class ScoringRuleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ScoringRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'field_name',
            'operator', 'value', 'points', 'is_active', 'priority',
            'created_at', 'updated_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['created_at', 'updated_at']


class QualificationCriteriaSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)

    class Meta:
        model = QualificationCriteria
        fields = [
            'id', 'name', 'stage', 'stage_display', 'minimum_score',
            'required_fields', 'required_actions', 'time_constraint_days',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LeadScoreSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source='lead.name', read_only=True)
    score_change = serializers.SerializerMethodField()

    class Meta:
        model = LeadScore
        fields = [
            'id', 'lead', 'lead_name', 'score', 'previous_score',
            'score_change', 'score_breakdown', 'qualification_stage',
            'demographic_score', 'behavioral_score', 'firmographic_score',
            'engagement_score', 'calculated_at'
        ]
        read_only_fields = ['calculated_at']

    def get_score_change(self, obj):
        if obj.previous_score is not None:
            return obj.score - obj.previous_score
        return 0


class QualificationWorkflowSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)

    class Meta:
        model = QualificationWorkflow
        fields = [
            'id', 'name', 'description', 'trigger_type', 'trigger_type_display',
            'trigger_config', 'action_type', 'action_type_display', 'action_config',
            'conditions', 'is_active', 'priority', 'execution_count',
            'last_executed_at', 'created_at', 'updated_at', 'created_by',
            'created_by_name'
        ]
        read_only_fields = ['created_at', 'updated_at', 'execution_count', 'last_executed_at']


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    lead_name = serializers.CharField(source='lead.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'workflow_name', 'lead', 'lead_name',
            'status', 'status_display', 'trigger_data', 'result_data',
            'error_message', 'started_at', 'completed_at', 'duration'
        ]
        read_only_fields = ['started_at', 'completed_at']

    def get_duration(self, obj):
        if obj.completed_at:
            delta = obj.completed_at - obj.started_at
            return delta.total_seconds()
        return None


class LeadEnrichmentDataSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source='lead.name', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = LeadEnrichmentData
        fields = [
            'id', 'lead', 'lead_name', 'source', 'source_display', 'data',
            'company_size', 'company_revenue', 'company_industry',
            'company_location', 'job_title', 'job_level', 'social_profiles',
            'technologies', 'enriched_at', 'is_verified', 'confidence_score'
        ]
        read_only_fields = ['enriched_at']


class LeadScoreCalculationSerializer(serializers.Serializer):
    """Serializer for triggering score calculation"""
    lead_id = serializers.IntegerField()

    def validate_lead_id(self, value):
        from lead_management.models import Lead
        if not Lead.objects.filter(id=value).exists():
            raise serializers.ValidationError("Lead not found")
        return value


class BulkScoreCalculationSerializer(serializers.Serializer):
    """Serializer for bulk score calculation"""
    lead_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    recalculate_all = serializers.BooleanField(default=False)
