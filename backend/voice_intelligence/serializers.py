"""
Voice Intelligence Serializers
DRF serializers for voice intelligence models
"""

from rest_framework import serializers
from .models import (
    VoiceRecording, Transcription, ConversationSummary,
    ActionItem, SentimentAnalysis, KeyMoment, CallScore,
    VoiceNote, ConversationCategory, RecordingCategory,
    TranscriptionSettings
)


class TranscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Transcription model"""
    
    word_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Transcription
        fields = [
            'id', 'full_text', 'words_with_timing', 'has_speaker_labels',
            'speaker_segments', 'speaker_count', 'speaker_mapping',
            'confidence_score', 'word_error_rate', 'provider',
            'detected_language', 'processing_time_seconds',
            'was_edited', 'word_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationSummarySerializer(serializers.ModelSerializer):
    """Serializer for ConversationSummary model"""
    
    summary_type_display = serializers.CharField(
        source='get_summary_type_display', read_only=True
    )
    
    class Meta:
        model = ConversationSummary
        fields = [
            'id', 'summary_type', 'summary_type_display', 'summary_text',
            'key_points', 'topics', 'topic_segments', 'decisions',
            'questions_asked', 'questions_unanswered', 'next_steps',
            'keywords', 'entities_mentioned', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ActionItemSerializer(serializers.ModelSerializer):
    """Serializer for ActionItem model"""
    
    priority_display = serializers.CharField(
        source='get_priority_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = ActionItem
        fields = [
            'id', 'recording', 'title', 'description', 'assigned_to',
            'assigned_to_name', 'due_date', 'mentioned_at_timestamp',
            'context_quote', 'speaker', 'priority', 'priority_display',
            'status', 'status_display', 'linked_task', 'confidence',
            'was_confirmed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SentimentAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for SentimentAnalysis model"""
    
    overall_sentiment_display = serializers.CharField(
        source='get_overall_sentiment_display', read_only=True
    )
    
    class Meta:
        model = SentimentAnalysis
        fields = [
            'id', 'overall_sentiment', 'overall_sentiment_display',
            'overall_score', 'sentiment_timeline', 'sentiment_by_speaker',
            'emotions_detected', 'dominant_emotion', 'customer_sentiment',
            'agent_sentiment', 'positive_moments', 'negative_moments',
            'engagement_score', 'talk_ratio', 'tone_analysis', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class KeyMomentSerializer(serializers.ModelSerializer):
    """Serializer for KeyMoment model"""
    
    moment_type_display = serializers.CharField(
        source='get_moment_type_display', read_only=True
    )
    
    class Meta:
        model = KeyMoment
        fields = [
            'id', 'recording', 'moment_type', 'moment_type_display',
            'start_timestamp', 'end_timestamp', 'transcript_excerpt',
            'speaker', 'summary', 'importance_score', 'is_ai_detected',
            'marked_by', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CallScoreSerializer(serializers.ModelSerializer):
    """Serializer for CallScore model"""
    
    class Meta:
        model = CallScore
        fields = [
            'id', 'overall_score', 'opening_score', 'discovery_score',
            'presentation_score', 'objection_handling_score', 'closing_score',
            'talk_to_listen_ratio', 'longest_monologue_seconds',
            'question_count', 'words_per_minute', 'filler_word_count',
            'filler_words_used', 'customer_engagement_score',
            'interruption_count', 'mentioned_value_prop',
            'asked_discovery_questions', 'handled_objections',
            'established_next_steps', 'personalized_conversation',
            'coaching_tips', 'areas_for_improvement', 'strengths', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationCategorySerializer(serializers.ModelSerializer):
    """Serializer for ConversationCategory model"""
    
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationCategory
        fields = [
            'id', 'name', 'description', 'color', 'parent',
            'keywords', 'recording_count', 'subcategories', 'created_at'
        ]
        read_only_fields = ['id', 'recording_count', 'created_at']
    
    def get_subcategories(self, obj):
        return ConversationCategorySerializer(
            obj.subcategories.all(), many=True
        ).data


class RecordingCategorySerializer(serializers.ModelSerializer):
    """Serializer for RecordingCategory model"""
    
    category_name = serializers.CharField(
        source='category.name', read_only=True
    )
    category_color = serializers.CharField(
        source='category.color', read_only=True
    )
    
    class Meta:
        model = RecordingCategory
        fields = [
            'id', 'recording', 'category', 'category_name', 'category_color',
            'is_auto_classified', 'confidence', 'classified_at'
        ]
        read_only_fields = ['id', 'classified_at']


class VoiceRecordingListSerializer(serializers.ModelSerializer):
    """Serializer for VoiceRecording list view"""
    
    source_type_display = serializers.CharField(
        source='get_source_type_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    duration_formatted = serializers.ReadOnlyField()
    has_transcription = serializers.SerializerMethodField()
    has_summary = serializers.SerializerMethodField()
    action_items_count = serializers.SerializerMethodField()
    categories = RecordingCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = VoiceRecording
        fields = [
            'id', 'title', 'source_type', 'source_type_display',
            'status', 'status_display', 'duration_seconds',
            'duration_formatted', 'participant_count', 'recorded_at',
            'has_transcription', 'has_summary', 'action_items_count',
            'categories', 'contact', 'lead', 'opportunity'
        ]
    
    def get_has_transcription(self, obj):
        return hasattr(obj, 'transcription')
    
    def get_has_summary(self, obj):
        return obj.summaries.exists()
    
    def get_action_items_count(self, obj):
        return obj.action_items.count()


class VoiceRecordingDetailSerializer(serializers.ModelSerializer):
    """Serializer for VoiceRecording detail view"""
    
    source_type_display = serializers.CharField(
        source='get_source_type_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    duration_formatted = serializers.ReadOnlyField()
    transcription = TranscriptionSerializer(read_only=True)
    summaries = ConversationSummarySerializer(many=True, read_only=True)
    action_items = ActionItemSerializer(many=True, read_only=True)
    sentiment_analysis = SentimentAnalysisSerializer(read_only=True)
    key_moments = KeyMomentSerializer(many=True, read_only=True)
    call_score = CallScoreSerializer(read_only=True)
    categories = RecordingCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = VoiceRecording
        fields = [
            'id', 'title', 'source_type', 'source_type_display',
            'status', 'status_display', 'file_url', 'file_size_bytes',
            'file_format', 'duration_seconds', 'duration_formatted',
            'sample_rate', 'channels', 'bitrate', 'participants',
            'participant_count', 'recorded_at', 'detected_language',
            'processing_started_at', 'processing_completed_at',
            'processing_error', 'contact', 'lead', 'opportunity',
            'meeting', 'transcription', 'summaries', 'action_items',
            'sentiment_analysis', 'key_moments', 'call_score',
            'categories', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VoiceRecordingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a VoiceRecording"""
    
    audio_file = serializers.FileField(write_only=True)
    
    class Meta:
        model = VoiceRecording
        fields = [
            'audio_file', 'title', 'source_type', 'participants',
            'participant_count', 'contact', 'lead', 'opportunity',
            'meeting', 'recorded_at'
        ]
    
    def create(self, validated_data):
        audio_file = validated_data.pop('audio_file')
        user = self.context['request'].user
        
        from .services import VoiceRecordingService
        service = VoiceRecordingService()
        
        metadata = {
            'participants': validated_data.pop('participants', []),
            'participant_count': validated_data.pop('participant_count', 2),
            'contact_id': validated_data.pop('contact', None),
            'lead_id': validated_data.pop('lead', None),
            'opportunity_id': validated_data.pop('opportunity', None),
            'meeting_id': validated_data.pop('meeting', None),
        }
        
        recording = service.create_recording(
            user=user,
            audio_file=audio_file,
            source_type=validated_data.get('source_type', 'upload'),
            title=validated_data.get('title', ''),
            metadata=metadata
        )
        
        return recording


class VoiceNoteSerializer(serializers.ModelSerializer):
    """Serializer for VoiceNote model"""
    
    class Meta:
        model = VoiceNote
        fields = [
            'id', 'audio_url', 'duration_seconds', 'transcript',
            'is_transcribed', 'ai_title', 'ai_summary',
            'action_items_extracted', 'tags', 'contact', 'lead',
            'opportunity', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VoiceNoteCreateSerializer(serializers.Serializer):
    """Serializer for creating a VoiceNote"""
    
    audio_file = serializers.FileField()
    contact = serializers.UUIDField(required=False, allow_null=True)
    lead = serializers.UUIDField(required=False, allow_null=True)
    opportunity = serializers.UUIDField(required=False, allow_null=True)
    
    def create(self, validated_data):
        audio_file = validated_data.pop('audio_file')
        user = self.context['request'].user
        
        related_to = {}
        if validated_data.get('contact'):
            related_to['contact_id'] = validated_data['contact']
        if validated_data.get('lead'):
            related_to['lead_id'] = validated_data['lead']
        if validated_data.get('opportunity'):
            related_to['opportunity_id'] = validated_data['opportunity']
        
        from .services import VoiceNoteService
        service = VoiceNoteService()
        
        return service.create_voice_note(
            user=user,
            audio_file=audio_file,
            related_to=related_to if related_to else None
        )


class TranscriptionSettingsSerializer(serializers.ModelSerializer):
    """Serializer for TranscriptionSettings model"""
    
    class Meta:
        model = TranscriptionSettings
        fields = [
            'id', 'preferred_provider', 'default_language',
            'auto_detect_language', 'enable_speaker_diarization',
            'enable_punctuation', 'enable_profanity_filter',
            'auto_generate_summary', 'auto_extract_action_items',
            'auto_analyze_sentiment', 'auto_score_calls',
            'notify_on_completion', 'notify_on_high_priority_action',
            'custom_vocabulary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TranscriptionEditSerializer(serializers.Serializer):
    """Serializer for editing transcription text"""
    
    full_text = serializers.CharField()
    segments = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class ProcessRecordingSerializer(serializers.Serializer):
    """Serializer for triggering recording processing"""
    
    transcribe = serializers.BooleanField(default=True)
    analyze = serializers.BooleanField(default=True)
    summarize = serializers.BooleanField(default=True)
    extract_actions = serializers.BooleanField(default=True)
    score_call = serializers.BooleanField(default=True)


class BulkActionItemUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating action items"""
    
    action_item_ids = serializers.ListField(
        child=serializers.UUIDField()
    )
    status = serializers.ChoiceField(
        choices=['pending', 'in_progress', 'completed', 'cancelled'],
        required=False
    )
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'critical'],
        required=False
    )
    assigned_to = serializers.UUIDField(required=False, allow_null=True)


class SearchRecordingsSerializer(serializers.Serializer):
    """Serializer for search parameters"""
    
    query = serializers.CharField(required=False)
    source_type = serializers.ChoiceField(
        choices=['phone_call', 'video_meeting', 'voice_note', 'upload', 'live_capture'],
        required=False
    )
    status = serializers.ChoiceField(
        choices=['uploading', 'uploaded', 'processing', 'transcribing', 'transcribed', 'analyzing', 'completed', 'failed'],
        required=False
    )
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    contact_id = serializers.UUIDField(required=False)
    lead_id = serializers.UUIDField(required=False)
    opportunity_id = serializers.UUIDField(required=False)
    category_id = serializers.UUIDField(required=False)
    has_action_items = serializers.BooleanField(required=False)
    min_duration = serializers.IntegerField(required=False)
    max_duration = serializers.IntegerField(required=False)


class RecordingAnalyticsSerializer(serializers.Serializer):
    """Serializer for recording analytics response"""
    
    total_recordings = serializers.IntegerField()
    total_duration_seconds = serializers.IntegerField()
    total_duration_formatted = serializers.CharField()
    recordings_by_status = serializers.DictField()
    recordings_by_source = serializers.DictField()
    recordings_by_category = serializers.ListField()
    average_call_score = serializers.FloatField()
    top_coaching_tips = serializers.ListField()
    action_items_summary = serializers.DictField()
    sentiment_distribution = serializers.DictField()
    recent_activity = serializers.ListField()
