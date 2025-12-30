"""
Voice & Conversation Intelligence - Advanced Serializers
"""

from rest_framework import serializers
from .advanced_models import (
    RealTimeCoachingSession, RealTimeCoachingSuggestion,
    SentimentTimeline, SentimentDashboard, MeetingSummary,
    MeetingActionItem, CallCoachingMetrics, KeyMoment
)


class RealTimeCoachingSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for coaching suggestions"""
    
    class Meta:
        model = RealTimeCoachingSuggestion
        fields = [
            'id', 'suggestion_type', 'priority', 'title', 'content',
            'context', 'timestamp_seconds', 'was_viewed', 'was_applied',
            'was_helpful', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RealTimeCoachingSessionSerializer(serializers.ModelSerializer):
    """Serializer for coaching sessions"""
    
    suggestions = RealTimeCoachingSuggestionSerializer(many=True, read_only=True)
    recording_title = serializers.CharField(source='recording.title', read_only=True)
    
    class Meta:
        model = RealTimeCoachingSession
        fields = [
            'id', 'recording', 'recording_title', 'status',
            'coaching_enabled', 'audio_enabled', 'suggestions_enabled',
            'current_talk_ratio', 'question_count', 'objection_count',
            'current_sentiment', 'engagement_level', 'started_at',
            'ended_at', 'suggestions'
        ]
        read_only_fields = ['id', 'started_at']


class SentimentTimelineSerializer(serializers.ModelSerializer):
    """Serializer for sentiment timeline"""
    
    class Meta:
        model = SentimentTimeline
        fields = [
            'id', 'timestamp_seconds', 'sentiment', 'sentiment_score',
            'emotions', 'speaker', 'speaker_type', 'text_snippet'
        ]


class SentimentDashboardSerializer(serializers.ModelSerializer):
    """Serializer for sentiment dashboard"""
    
    class Meta:
        model = SentimentDashboard
        fields = [
            'id', 'period', 'start_date', 'end_date', 'total_calls',
            'avg_sentiment_score', 'positive_percentage', 'neutral_percentage',
            'negative_percentage', 'sentiment_trend', 'trend_percentage',
            'top_emotions', 'sentiment_by_call_type', 'sentiment_by_deal_stage',
            'insights', 'calculated_at'
        ]


class MeetingActionItemSerializer(serializers.ModelSerializer):
    """Serializer for meeting action items"""
    
    assigned_to_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MeetingActionItem
        fields = [
            'id', 'title', 'description', 'assigned_to', 'assigned_to_name',
            'mentioned_assignee', 'due_date', 'mentioned_deadline',
            'context_quote', 'timestamp_seconds', 'priority', 'status',
            'linked_task', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.email
        return None


class MeetingSummarySerializer(serializers.ModelSerializer):
    """Serializer for meeting summaries"""
    
    recording_title = serializers.CharField(source='recording.title', read_only=True)
    recording_duration = serializers.IntegerField(
        source='recording.duration_seconds', read_only=True
    )
    extracted_action_items = MeetingActionItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = MeetingSummary
        fields = [
            'id', 'recording', 'recording_title', 'recording_duration',
            'summary_type', 'executive_summary', 'key_points', 'decisions',
            'action_items', 'follow_up_recommendations', 'open_questions',
            'topics_discussed', 'attendee_summary', 'next_steps',
            'suggested_follow_up_date', 'confidence_score', 'is_shared',
            'email_sent', 'email_sent_at', 'extracted_action_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CallCoachingMetricsSerializer(serializers.ModelSerializer):
    """Serializer for coaching metrics"""
    
    class Meta:
        model = CallCoachingMetrics
        fields = [
            'id', 'period', 'start_date', 'end_date', 'total_calls',
            'total_duration_minutes', 'avg_talk_ratio', 'talk_ratio_trend',
            'avg_questions_per_call', 'question_quality_score',
            'objections_handled', 'objection_success_rate',
            'avg_engagement_score', 'avg_call_score', 'call_score_trend',
            'improvement_areas', 'strengths', 'recommendations', 'calculated_at'
        ]


class KeyMomentSerializer(serializers.ModelSerializer):
    """Serializer for key moments"""
    
    class Meta:
        model = KeyMoment
        fields = [
            'id', 'moment_type', 'importance', 'timestamp_seconds',
            'duration_seconds', 'title', 'description', 'quote',
            'speaker', 'speaker_type', 'context_before', 'context_after',
            'sentiment', 'confidence_score', 'related_competitor',
            'related_product', 'is_bookmarked', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StartCoachingSessionSerializer(serializers.Serializer):
    """Serializer for starting a coaching session"""
    
    recording_id = serializers.IntegerField(required=True)
    coaching_enabled = serializers.BooleanField(default=True)
    suggestions_enabled = serializers.BooleanField(default=True)


class ProcessAudioChunkSerializer(serializers.Serializer):
    """Serializer for processing audio chunks"""
    
    audio_data = serializers.CharField(required=True)  # Base64 encoded
    timestamp = serializers.FloatField(required=True)


class GenerateSummarySerializer(serializers.Serializer):
    """Serializer for generating meeting summary"""
    
    recording_id = serializers.IntegerField(required=True)
    summary_type = serializers.ChoiceField(
        choices=['full', 'executive', 'action_items', 'key_points'],
        default='full'
    )


class SendSummaryEmailSerializer(serializers.Serializer):
    """Serializer for sending summary email"""
    
    recipients = serializers.ListField(
        child=serializers.EmailField(),
        min_length=1
    )


class SentimentAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for sentiment analysis request"""
    
    recording_id = serializers.IntegerField(required=True)


class SentimentDashboardRequestSerializer(serializers.Serializer):
    """Serializer for dashboard request"""
    
    period = serializers.ChoiceField(
        choices=['daily', 'weekly', 'monthly'],
        default='weekly'
    )
