"""
AI Chatbot Serializers
"""

from rest_framework import serializers
from .models import ChatSession, ChatMessage, QuickAction, EmailTemplate


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'role', 'message_type', 'content', 'structured_data',
            'is_helpful', 'feedback', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ChatSessionListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'context_type', 'context_id',
            'message_count', 'last_message', 'created_at', 'updated_at'
        ]

    def get_last_message(self, obj):
        last = obj.messages.order_by('-created_at').first()
        if last:
            return {
                'content': last.content[:100],
                'role': last.role,
                'created_at': last.created_at
            }
        return None


class ChatSessionDetailSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'context_type', 'context_id',
            'message_count', 'messages', 'created_at', 'updated_at'
        ]


class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    context_type = serializers.CharField(required=False, allow_blank=True)
    context_id = serializers.CharField(required=False, allow_blank=True)


class QuickActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickAction
        fields = [
            'id', 'name', 'description', 'icon', 'prompt_template',
            'requires_context', 'context_types', 'category'
        ]


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'purpose', 'tone', 'subject_template',
            'body_template', 'variables', 'usage_count',
            'avg_open_rate', 'avg_response_rate', 'created_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at']


class GenerateEmailSerializer(serializers.Serializer):
    purpose = serializers.ChoiceField(choices=[
        'follow_up', 'introduction', 'proposal', 'thank_you',
        'meeting_request', 'closing', 'nurture'
    ])
    tone = serializers.ChoiceField(choices=[
        'professional', 'friendly', 'formal', 'casual', 'persuasive'
    ], default='professional')
    context = serializers.DictField(required=False, default=dict)
    recipient_name = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    additional_context = serializers.CharField(required=False, allow_blank=True)


class QueryDataSerializer(serializers.Serializer):
    query = serializers.CharField()
    entity_type = serializers.ChoiceField(
        choices=['leads', 'contacts', 'opportunities', 'tasks', 'all'],
        default='all'
    )


class MessageFeedbackSerializer(serializers.Serializer):
    is_helpful = serializers.BooleanField()
    feedback = serializers.CharField(required=False, allow_blank=True)
