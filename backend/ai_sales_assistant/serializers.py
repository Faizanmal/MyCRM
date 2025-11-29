"""
AI Sales Assistant Serializers
"""

from rest_framework import serializers
from .models import (
    AIEmailDraft, SalesCoachAdvice, ObjectionResponse,
    CallScript, DealInsight, WinLossAnalysis, PersonaProfile, ContactPersonaMatch
)


class AIEmailDraftSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    
    class Meta:
        model = AIEmailDraft
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at']


class GenerateEmailSerializer(serializers.Serializer):
    """Input for email generation"""
    contact_id = serializers.IntegerField()
    opportunity_id = serializers.IntegerField(required=False, allow_null=True)
    email_type = serializers.ChoiceField(choices=AIEmailDraft.EMAIL_TYPES)
    tone = serializers.ChoiceField(choices=AIEmailDraft.TONE_CHOICES, default='professional')
    context = serializers.CharField(required=False, allow_blank=True)
    key_points = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )


class SalesCoachAdviceSerializer(serializers.ModelSerializer):
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    
    class Meta:
        model = SalesCoachAdvice
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at']


class ObjectionResponseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = ObjectionResponse
        fields = '__all__'
        read_only_fields = ['id', 'times_used', 'success_rate', 'created_at', 'updated_at']


class HandleObjectionSerializer(serializers.Serializer):
    """Input for objection handling"""
    objection = serializers.CharField()
    contact_id = serializers.IntegerField(required=False, allow_null=True)
    opportunity_id = serializers.IntegerField(required=False, allow_null=True)


class CallScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallScript
        fields = '__all__'
        read_only_fields = ['id', 'user', 'times_used', 'avg_call_duration', 
                           'success_rate', 'created_at', 'updated_at']


class DealInsightSerializer(serializers.ModelSerializer):
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    
    class Meta:
        model = DealInsight
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class WinLossAnalysisSerializer(serializers.ModelSerializer):
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    
    class Meta:
        model = WinLossAnalysis
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PersonaProfileSerializer(serializers.ModelSerializer):
    win_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = PersonaProfile
        fields = '__all__'
        read_only_fields = ['id', 'contacts_matched', 'deals_won', 'deals_lost', 
                           'avg_deal_size', 'created_at', 'updated_at']


class ContactPersonaMatchSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    persona_name = serializers.CharField(source='persona.name', read_only=True)
    
    class Meta:
        model = ContactPersonaMatch
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AICoachDashboardSerializer(serializers.Serializer):
    """Dashboard for AI coaching"""
    pending_advice_count = serializers.IntegerField()
    high_priority_advice = serializers.ListField()
    emails_generated_today = serializers.IntegerField()
    deals_needing_attention = serializers.IntegerField()
    top_insights = serializers.ListField()
