"""
Conversation Intelligence Admin Configuration
"""

from django.contrib import admin

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


class CallAnalysisInline(admin.StackedInline):
    model = CallAnalysis
    extra = 0
    readonly_fields = ['created_at']


class CallTranscriptInline(admin.StackedInline):
    model = CallTranscript
    extra = 0
    readonly_fields = ['created_at']


@admin.register(CallRecording)
class CallRecordingAdmin(admin.ModelAdmin):
    list_display = ['title', 'call_type', 'platform', 'owner', 'status', 'duration_formatted', 'recorded_at']
    list_filter = ['status', 'call_type', 'platform', 'recorded_at']
    search_fields = ['title', 'owner__email']
    readonly_fields = ['uuid', 'duration_formatted']
    inlines = [CallTranscriptInline, CallAnalysisInline]
    raw_id_fields = ['opportunity', 'contact']
    filter_horizontal = ['shared_with']


@admin.register(CallTranscript)
class CallTranscriptAdmin(admin.ModelAdmin):
    list_display = ['recording', 'word_count', 'detected_language', 'confidence_score', 'created_at']
    search_fields = ['recording__title']


@admin.register(TranscriptSegment)
class TranscriptSegmentAdmin(admin.ModelAdmin):
    list_display = ['transcript', 'speaker', 'speaker_type', 'sentiment', 'start_time', 'end_time']
    list_filter = ['speaker_type', 'sentiment']


@admin.register(CallAnalysis)
class CallAnalysisAdmin(admin.ModelAdmin):
    list_display = ['recording', 'call_score', 'engagement_score', 'overall_sentiment', 'question_count']
    list_filter = ['overall_sentiment', 'energy_level']
    search_fields = ['recording__title']


@admin.register(TopicMention)
class TopicMentionAdmin(admin.ModelAdmin):
    list_display = ['recording', 'topic_type', 'topic_name', 'sentiment', 'timestamp']
    list_filter = ['topic_type', 'sentiment']
    search_fields = ['topic_name', 'recording__title']


@admin.register(CallCoaching)
class CallCoachingAdmin(admin.ModelAdmin):
    list_display = ['recording', 'coach', 'feedback_type', 'is_ai_generated', 'timestamp', 'created_at']
    list_filter = ['feedback_type', 'is_ai_generated']
    search_fields = ['recording__title', 'coach__email', 'feedback']


class PlaylistClipInline(admin.TabularInline):
    model = PlaylistClip
    extra = 1


@admin.register(CallPlaylist)
class CallPlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'creator', 'is_public', 'created_at']
    list_filter = ['category', 'is_public']
    search_fields = ['name', 'creator__email']
    inlines = [PlaylistClipInline]


@admin.register(CallTracker)
class CallTrackerAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_shared', 'total_mentions', 'created_at']
    list_filter = ['is_shared']
    search_fields = ['name', 'created_by__email']


@admin.register(ConversationAnalytics)
class ConversationAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'calls_recorded', 'total_duration_minutes', 'avg_call_score']
    list_filter = ['date']
    search_fields = ['user__email']
    date_hierarchy = 'date'
