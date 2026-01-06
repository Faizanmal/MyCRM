"""
Customer Success Serializers
"""

from rest_framework import serializers

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


class HealthScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthScore
        fields = '__all__'


class CustomerMilestoneSerializer(serializers.ModelSerializer):
    milestone_type_display = serializers.CharField(source='get_milestone_type_display', read_only=True)

    class Meta:
        model = CustomerMilestone
        fields = '__all__'


class CustomerNoteSerializer(serializers.ModelSerializer):
    note_type_display = serializers.CharField(source='get_note_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = CustomerNote
        fields = '__all__'
        read_only_fields = ['created_by']


class CustomerAccountListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    csm_name = serializers.CharField(source='customer_success_manager.get_full_name', read_only=True)
    days_until_renewal = serializers.ReadOnlyField()
    health_status = serializers.SerializerMethodField()
    health_score = serializers.SerializerMethodField()

    class Meta:
        model = CustomerAccount
        fields = [
            'id', 'uuid', 'name', 'tier', 'tier_display', 'arr', 'mrr',
            'customer_success_manager', 'csm_name', 'is_active',
            'contract_end', 'days_until_renewal', 'health_status', 'health_score'
        ]

    def get_health_status(self, obj):
        latest = obj.health_scores.first()
        return latest.status if latest else None

    def get_health_score(self, obj):
        latest = obj.health_scores.first()
        return latest.score if latest else None


class CustomerAccountDetailSerializer(serializers.ModelSerializer):
    """Full serializer with related data"""
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    csm_name = serializers.CharField(source='customer_success_manager.get_full_name', read_only=True)
    days_until_renewal = serializers.ReadOnlyField()

    health_scores = HealthScoreSerializer(many=True, read_only=True)
    milestones = CustomerMilestoneSerializer(many=True, read_only=True)
    recent_notes = serializers.SerializerMethodField()

    class Meta:
        model = CustomerAccount
        fields = '__all__'

    def get_recent_notes(self, obj):
        notes = obj.notes.all()[:5]
        return CustomerNoteSerializer(notes, many=True).data


class PlaybookStepSerializer(serializers.ModelSerializer):
    step_type_display = serializers.CharField(source='get_step_type_display', read_only=True)

    class Meta:
        model = PlaybookStep
        fields = '__all__'


class SuccessPlaybookSerializer(serializers.ModelSerializer):
    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    steps = PlaybookStepSerializer(many=True, read_only=True)

    class Meta:
        model = SuccessPlaybook
        fields = '__all__'
        read_only_fields = ['created_by']


class PlaybookExecutionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    playbook_name = serializers.CharField(source='playbook.name', read_only=True)

    class Meta:
        model = PlaybookExecution
        fields = '__all__'


class RenewalOpportunitySerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    projected_change = serializers.ReadOnlyField()
    projected_change_percent = serializers.ReadOnlyField()

    class Meta:
        model = RenewalOpportunity
        fields = '__all__'


class ExpansionOpportunitySerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    expansion_type_display = serializers.CharField(source='get_expansion_type_display', read_only=True)

    class Meta:
        model = ExpansionOpportunity
        fields = '__all__'


class NPSSurveySerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = NPSSurvey
        fields = '__all__'


class HealthScoreConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthScoreConfig
        fields = '__all__'


class CustomerSuccessAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSuccessAnalytics
        fields = '__all__'


# Action serializers
class RecalculateHealthSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=False)
    all_accounts = serializers.BooleanField(default=False)


class TriggerPlaybookSerializer(serializers.Serializer):
    playbook_id = serializers.IntegerField()
    account_id = serializers.IntegerField()


class SendNPSSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    contact_ids = serializers.ListField(child=serializers.IntegerField())
