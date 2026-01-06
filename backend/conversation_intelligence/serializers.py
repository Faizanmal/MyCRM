"""
Conversation Intelligence Serializers
"""

from rest_framework import serializers

from .models import (
    CallAnalysis,
    CallCoaching,
    CallPlaylist,
    CallRecording,
    CallTracker,
    CallTranscript,
    ConversationAnalytics,
    PlaylistClip,
    TopicMention,
    TranscriptSegment,
)


class TranscriptSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranscriptSegment
        fields = '__all__'


class CallTranscriptSerializer(serializers.ModelSerializer):
    segments = TranscriptSegmentSerializer(many=True, read_only=True)

    class Meta:
        model = CallTranscript
        fields = '__all__'


class CallAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallAnalysis
        fields = '__all__'


class TopicMentionSerializer(serializers.ModelSerializer):
    topic_type_display = serializers.CharField(source='get_topic_type_display', read_only=True)

    class Meta:
        model = TopicMention
        fields = '__all__'


class CallCoachingSerializer(serializers.ModelSerializer):
    coach_name = serializers.CharField(source='coach.get_full_name', read_only=True)

    class Meta:
        model = CallCoaching
        fields = '__all__'
        read_only_fields = ['coach']


class CallRecordingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    call_type_display = serializers.CharField(source='get_call_type_display', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    duration_formatted = serializers.ReadOnlyField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    has_analysis = serializers.SerializerMethodField()
    call_score = serializers.SerializerMethodField()

    class Meta:
        model = CallRecording
        fields = [
            'id', 'uuid', 'title', 'call_type', 'call_type_display',
            'platform', 'platform_display', 'duration_seconds', 'duration_formatted',
            'status', 'recorded_at', 'owner', 'owner_name', 'has_analysis', 'call_score'
        ]

    def get_has_analysis(self, obj):
        return hasattr(obj, 'analysis')

    def get_call_score(self, obj):
        if hasattr(obj, 'analysis'):
            return obj.analysis.call_score
        return None


class CallRecordingDetailSerializer(serializers.ModelSerializer):
    """Full serializer with related data"""
    call_type_display = serializers.CharField(source='get_call_type_display', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    duration_formatted = serializers.ReadOnlyField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    transcript = CallTranscriptSerializer(read_only=True)
    analysis = CallAnalysisSerializer(read_only=True)
    topic_mentions = TopicMentionSerializer(many=True, read_only=True)
    coaching_notes = CallCoachingSerializer(many=True, read_only=True)

    class Meta:
        model = CallRecording
        fields = '__all__'
        read_only_fields = ['uuid', 'owner', 'status', 'processing_error']


class CallRecordingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRecording
        fields = [
            'title', 'call_type', 'platform', 'opportunity', 'contact',
            'recording_file', 'recording_url', 'recorded_at', 'is_shared'
        ]


class PlaylistClipSerializer(serializers.ModelSerializer):
    recording_title = serializers.CharField(source='recording.title', read_only=True)

    class Meta:
        model = PlaylistClip
        fields = '__all__'


class CallPlaylistSerializer(serializers.ModelSerializer):
    clips = PlaylistClipSerializer(many=True, read_only=True)
    clip_count = serializers.IntegerField(source='clips.count', read_only=True)
    creator_name = serializers.CharField(source='creator.get_full_name', read_only=True)

    class Meta:
        model = CallPlaylist
        fields = '__all__'
        read_only_fields = ['creator']


class CallTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallTracker
        fields = '__all__'
        read_only_fields = ['created_by', 'total_mentions']


class ConversationAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationAnalytics
        fields = '__all__'


# Action serializers
class AddCoachingSerializer(serializers.Serializer):
    timestamp = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    feedback = serializers.CharField()
    feedback_type = serializers.ChoiceField(
        choices=['praise', 'suggestion', 'correction', 'question'],
        default='suggestion'
    )


class CreateClipSerializer(serializers.Serializer):
    recording_id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    start_time = serializers.DecimalField(max_digits=10, decimal_places=2)
    end_time = serializers.DecimalField(max_digits=10, decimal_places=2)
