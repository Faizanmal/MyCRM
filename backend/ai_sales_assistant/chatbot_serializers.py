"""
AI Sales Assistant - Chatbot Serializers
"""

from rest_framework import serializers
from .chatbot_models import (
    ConversationSession, ChatMessage, ChatIntent,
    QuickAction, PredictiveDealIntelligence, SmartContent
)


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'role', 'message_type', 'content', 'metadata',
            'attachments', 'action_taken', 'action_result',
            'was_helpful', 'feedback', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationSessionSerializer(serializers.ModelSerializer):
    """Serializer for conversation sessions"""
    
    messages = ChatMessageSerializer(many=True, read_only=True)
    recent_messages = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationSession
        fields = [
            'id', 'title', 'session_type', 'status', 'context',
            'pinned_entities', 'message_count', 'last_activity',
            'is_starred', 'created_at', 'messages', 'recent_messages'
        ]
        read_only_fields = ['id', 'message_count', 'last_activity', 'created_at']
    
    def get_recent_messages(self, obj):
        """Get last 10 messages for preview"""
        messages = obj.messages.order_by('-created_at')[:10]
        return ChatMessageSerializer(reversed(list(messages)), many=True).data


class ConversationSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for session lists"""
    
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationSession
        fields = [
            'id', 'title', 'session_type', 'status', 'message_count',
            'last_activity', 'is_starred', 'last_message'
        ]
    
    def get_last_message(self, obj):
        last = obj.messages.order_by('-created_at').first()
        if last:
            return {
                'content': last.content[:100],
                'role': last.role,
                'created_at': last.created_at,
            }
        return None


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending a message"""
    
    message = serializers.CharField(required=True)
    session_id = serializers.UUIDField(required=False, allow_null=True)
    context = serializers.DictField(required=False, default=dict)


class ChatIntentSerializer(serializers.ModelSerializer):
    """Serializer for chat intents"""
    
    class Meta:
        model = ChatIntent
        fields = [
            'id', 'name', 'category', 'description', 'example_phrases',
            'keywords', 'handler_function', 'requires_entities', 'is_active'
        ]


class QuickActionSerializer(serializers.ModelSerializer):
    """Serializer for quick actions"""
    
    entity_name = serializers.SerializerMethodField()
    
    class Meta:
        model = QuickAction
        fields = [
            'id', 'action_type', 'title', 'description', 'entity_type',
            'entity_id', 'entity_name', 'priority', 'reason', 'expected_impact',
            'is_dismissed', 'is_completed', 'completed_at', 'source_insight',
            'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_entity_name(self, obj):
        """Get the name of the referenced entity"""
        try:
            if obj.entity_type == 'contact':
                from contact_management.models import Contact
                entity = Contact.objects.get(id=obj.entity_id)
                return f"{entity.first_name} {entity.last_name}"
            elif obj.entity_type == 'opportunity':
                from opportunity_management.models import Opportunity
                entity = Opportunity.objects.get(id=obj.entity_id)
                return entity.name
            elif obj.entity_type == 'lead':
                from lead_management.models import Lead
                entity = Lead.objects.get(id=obj.entity_id)
                return f"{entity.first_name} {entity.last_name}"
        except Exception:
            pass
        return None


class PredictiveDealIntelligenceSerializer(serializers.ModelSerializer):
    """Serializer for predictive deal intelligence"""
    
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    opportunity_amount = serializers.DecimalField(
        source='opportunity.amount',
        max_digits=15, decimal_places=2,
        read_only=True
    )
    opportunity_stage = serializers.CharField(source='opportunity.stage', read_only=True)
    
    class Meta:
        model = PredictiveDealIntelligence
        fields = [
            'id', 'opportunity', 'opportunity_name', 'opportunity_amount',
            'opportunity_stage', 'win_probability', 'probability_trend',
            'probability_factors', 'expected_close_date', 'velocity_score',
            'velocity_comparison', 'days_to_close_prediction', 'risk_level',
            'risk_factors', 'risk_mitigation_actions', 'deal_health_score',
            'health_breakdown', 'engagement_score', 'stakeholder_engagement',
            'communication_frequency', 'recommended_actions',
            'competitive_threat_level', 'competitor_signals',
            'model_version', 'confidence_score', 'analyzed_at', 'created_at'
        ]
        read_only_fields = ['id', 'analyzed_at', 'created_at']


class SmartContentSerializer(serializers.ModelSerializer):
    """Serializer for smart content"""
    
    contact_name = serializers.SerializerMethodField()
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    
    class Meta:
        model = SmartContent
        fields = [
            'id', 'content_type', 'tone', 'contact', 'contact_name',
            'opportunity', 'opportunity_name', 'prompt', 'context_data',
            'title', 'content', 'variations', 'personalization_score',
            'personalization_elements', 'was_used', 'used_at',
            'rating', 'feedback', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_contact_name(self, obj):
        if obj.contact:
            return f"{obj.contact.first_name} {obj.contact.last_name}"
        return None


class GenerateSmartContentSerializer(serializers.Serializer):
    """Serializer for generating smart content"""
    
    content_type = serializers.ChoiceField(choices=[
        ('email', 'Email'),
        ('call_script', 'Call Script'),
        ('objection_response', 'Objection Response'),
        ('social_post', 'Social Media Post'),
        ('linkedin_message', 'LinkedIn Message'),
        ('sms', 'SMS Message'),
    ])
    tone = serializers.ChoiceField(choices=[
        ('professional', 'Professional'),
        ('friendly', 'Friendly'),
        ('casual', 'Casual'),
        ('formal', 'Formal'),
        ('urgent', 'Urgent'),
        ('enthusiastic', 'Enthusiastic'),
    ], default='professional')
    contact_id = serializers.UUIDField(required=False, allow_null=True)
    opportunity_id = serializers.UUIDField(required=False, allow_null=True)
    prompt = serializers.CharField(required=False, default='')
    context = serializers.DictField(required=False, default=dict)


class AnalyzeDealSerializer(serializers.Serializer):
    """Serializer for deal analysis request"""
    
    opportunity_id = serializers.UUIDField(required=True)


class MessageFeedbackSerializer(serializers.Serializer):
    """Serializer for message feedback"""
    
    was_helpful = serializers.BooleanField(required=True)
    feedback = serializers.CharField(required=False, default='')


class ActionCompleteSerializer(serializers.Serializer):
    """Serializer for completing an action"""
    
    result = serializers.CharField(required=False, default='')
