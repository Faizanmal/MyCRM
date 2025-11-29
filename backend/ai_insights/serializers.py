from rest_framework import serializers
from .models import (
    ChurnPrediction, NextBestAction, AIGeneratedContent,
    SentimentAnalysis, AIModelMetrics
)


class ChurnPredictionSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    contact_email = serializers.EmailField(source='contact.email', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ChurnPrediction
        fields = [
            'id', 'contact', 'contact_name', 'contact_email',
            'churn_probability', 'risk_level', 'factors',
            'confidence_score', 'recommended_actions',
            'model_version', 'predicted_at', 'expires_at', 'is_expired'
        ]
        read_only_fields = ['predicted_at']


class NextBestActionSerializer(serializers.ModelSerializer):
    entity_name = serializers.SerializerMethodField()
    
    class Meta:
        model = NextBestAction
        fields = [
            'id', 'user', 'entity_type', 'entity_id', 'entity_name',
            'action_type', 'title', 'description', 'reasoning',
            'priority_score', 'expected_impact', 'suggested_timing',
            'status', 'model_version', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'completed_at']
    
    def get_entity_name(self, obj):
        """Get name of the entity"""
        try:
            if obj.entity_type == 'lead':
                from lead_management.models import Lead
                entity = Lead.objects.get(id=obj.entity_id)
                return f"{entity.first_name} {entity.last_name}"
            elif obj.entity_type == 'contact':
                from contact_management.models import Contact
                entity = Contact.objects.get(id=obj.entity_id)
                return f"{entity.first_name} {entity.last_name}"
            elif obj.entity_type == 'opportunity':
                from opportunity_management.models import Opportunity
                entity = Opportunity.objects.get(id=obj.entity_id)
                return entity.name
        except Exception:
            return ''
        return ''


class AIGeneratedContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIGeneratedContent
        fields = [
            'id', 'user', 'content_type', 'prompt', 'context_data',
            'subject', 'body', 'tone', 'language',
            'quality_score', 'readability_score',
            'was_used', 'was_edited', 'user_rating',
            'model_used', 'tokens_used', 'created_at'
        ]
        read_only_fields = ['user', 'created_at', 'model_used', 'tokens_used']


class AIContentGenerationRequestSerializer(serializers.Serializer):
    """Request serializer for content generation"""
    content_type = serializers.ChoiceField(
        choices=['email', 'sms', 'social', 'proposal']
    )
    context = serializers.JSONField()
    tone = serializers.ChoiceField(
        choices=['professional', 'friendly', 'formal', 'casual'],
        default='professional'
    )
    custom_prompt = serializers.CharField(required=False, allow_blank=True)


class SentimentAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentimentAnalysis
        fields = [
            'id', 'entity_type', 'entity_id', 'text_content',
            'sentiment', 'sentiment_score', 'confidence',
            'emotions', 'keywords', 'topics',
            'requires_attention', 'alert_reason', 'analyzed_at'
        ]
        read_only_fields = ['analyzed_at']


class AIModelMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModelMetrics
        fields = [
            'id', 'model_name', 'model_version', 'metric_type',
            'metric_value', 'sample_size', 'measured_at', 'notes'
        ]
        read_only_fields = ['measured_at']
