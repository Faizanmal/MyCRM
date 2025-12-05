from rest_framework import serializers
from .models import (
    EmailSequence, SequenceStep, SequenceEmail, SequenceEnrollment,
    SequenceActivity, ABTest, AutomatedTrigger, EmailPersonalizationToken,
    SequenceAnalytics
)


class SequenceEmailSerializer(serializers.ModelSerializer):
    open_rate = serializers.ReadOnlyField()
    click_rate = serializers.ReadOnlyField()
    reply_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = SequenceEmail
        fields = [
            'id', 'step', 'subject', 'preview_text', 'body_html', 'body_text',
            'ai_generated', 'ai_prompt', 'variant_name', 'variant_weight', 'is_winner',
            'personalization_tokens', 'total_sent', 'total_delivered', 'total_opened',
            'total_clicked', 'total_replied', 'total_bounced', 'open_rate', 'click_rate',
            'reply_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_sent', 'total_delivered', 'total_opened',
                          'total_clicked', 'total_replied', 'total_bounced']


class ABTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ABTest
        fields = [
            'id', 'step', 'name', 'test_metric', 'sample_size', 'confidence_level',
            'status', 'winning_variant', 'winner_selected_at', 'auto_select_winner',
            'results', 'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = ['id', 'winning_variant', 'winner_selected_at', 'results',
                          'started_at', 'completed_at']


class SequenceStepSerializer(serializers.ModelSerializer):
    emails = SequenceEmailSerializer(many=True, read_only=True)
    ab_test = ABTestSerializer(read_only=True)
    wait_total_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = SequenceStep
        fields = [
            'id', 'sequence', 'step_type', 'step_number', 'name',
            'wait_days', 'wait_hours', 'wait_minutes', 'wait_total_minutes',
            'condition_type', 'condition_config', 'branch_yes_step', 'branch_no_step',
            'config', 'ab_test_enabled', 'total_executed', 'total_completed',
            'is_active', 'emails', 'ab_test', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_executed', 'total_completed']


class SequenceStepCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceStep
        fields = [
            'sequence', 'step_type', 'step_number', 'name',
            'wait_days', 'wait_hours', 'wait_minutes',
            'condition_type', 'condition_config', 'config',
            'ab_test_enabled', 'is_active'
        ]


class EmailSequenceSerializer(serializers.ModelSerializer):
    steps = SequenceStepSerializer(many=True, read_only=True)
    conversion_rate = serializers.ReadOnlyField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = EmailSequence
        fields = [
            'id', 'name', 'description', 'owner', 'owner_name', 'shared_with_team',
            'status', 'trigger_type', 'trigger_config', 'settings', 'exit_conditions',
            'personalization_enabled', 'ai_optimization_enabled',
            'total_enrolled', 'total_completed', 'total_converted',
            'avg_open_rate', 'avg_click_rate', 'avg_reply_rate', 'conversion_rate',
            'steps', 'created_at', 'updated_at', 'activated_at'
        ]
        read_only_fields = ['id', 'owner', 'total_enrolled', 'total_completed',
                          'total_converted', 'avg_open_rate', 'avg_click_rate',
                          'avg_reply_rate', 'activated_at']


class EmailSequenceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSequence
        fields = [
            'name', 'description', 'shared_with_team', 'trigger_type',
            'trigger_config', 'settings', 'exit_conditions',
            'personalization_enabled', 'ai_optimization_enabled'
        ]


class SequenceActivitySerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='enrollment.contact.full_name', read_only=True)
    step_name = serializers.CharField(source='step.name', read_only=True)
    
    class Meta:
        model = SequenceActivity
        fields = [
            'id', 'enrollment', 'step', 'step_name', 'activity_type',
            'description', 'metadata', 'contact_name', 'timestamp'
        ]


class SequenceEnrollmentSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    contact_email = serializers.CharField(source='contact.email', read_only=True)
    sequence_name = serializers.CharField(source='sequence.name', read_only=True)
    current_step_name = serializers.CharField(source='current_step.name', read_only=True)
    activities = SequenceActivitySerializer(many=True, read_only=True)
    
    class Meta:
        model = SequenceEnrollment
        fields = [
            'id', 'sequence', 'sequence_name', 'contact', 'contact_name',
            'contact_email', 'lead', 'current_step', 'current_step_name',
            'status', 'next_action_at', 'enrolled_by', 'enrollment_trigger',
            'exit_reason', 'exited_at', 'emails_sent', 'emails_opened',
            'emails_clicked', 'emails_replied', 'personalization_data',
            'enrolled_at', 'completed_at', 'activities'
        ]
        read_only_fields = ['id', 'enrolled_at', 'completed_at', 'emails_sent',
                          'emails_opened', 'emails_clicked', 'emails_replied']


class EnrollContactSerializer(serializers.Serializer):
    sequence_id = serializers.UUIDField()
    contact_id = serializers.IntegerField()
    lead_id = serializers.IntegerField(required=False, allow_null=True)
    personalization_data = serializers.JSONField(required=False, default=dict)


class AutomatedTriggerSerializer(serializers.ModelSerializer):
    sequence_name = serializers.CharField(source='sequence.name', read_only=True)
    
    class Meta:
        model = AutomatedTrigger
        fields = [
            'id', 'name', 'description', 'trigger_type', 'trigger_config',
            'sequence', 'sequence_name', 'conditions', 'is_active',
            'prevent_re_enrollment', 'total_triggered', 'total_enrolled',
            'created_at', 'last_triggered_at'
        ]
        read_only_fields = ['id', 'total_triggered', 'total_enrolled', 'last_triggered_at']


class EmailPersonalizationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailPersonalizationToken
        fields = [
            'id', 'name', 'display_name', 'description', 'token_type',
            'source_field', 'default_value', 'formula', 'ai_prompt',
            'is_system', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'is_system']


class SequenceAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceAnalytics
        fields = [
            'id', 'sequence', 'date', 'new_enrollments', 'active_enrollments',
            'completed_enrollments', 'exited_enrollments', 'emails_sent',
            'emails_delivered', 'emails_opened', 'emails_clicked', 'emails_replied',
            'emails_bounced', 'conversions', 'conversion_value',
            'open_rate', 'click_rate', 'reply_rate', 'conversion_rate', 'bounce_rate'
        ]


class GenerateEmailContentSerializer(serializers.Serializer):
    template_type = serializers.ChoiceField(choices=['outreach', 'follow_up', 'nurture', 'deal'])
    template_subtype = serializers.CharField()
    context = serializers.JSONField()
    tone = serializers.ChoiceField(
        choices=['professional', 'friendly', 'casual', 'urgent', 'empathetic', 'authoritative'],
        default='professional'
    )
    length = serializers.ChoiceField(choices=['short', 'medium', 'long'], default='medium')
    personalization_data = serializers.JSONField(required=False, default=dict)


class GenerateSubjectVariantsSerializer(serializers.Serializer):
    context = serializers.JSONField()
    num_variants = serializers.IntegerField(min_value=2, max_value=5, default=3)


class AnalyzeEmailQualitySerializer(serializers.Serializer):
    subject = serializers.CharField()
    body = serializers.CharField()


class OptimizeSendTimeSerializer(serializers.Serializer):
    contact_id = serializers.IntegerField()
