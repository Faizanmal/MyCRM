"""
Voice Intelligence Admin
Django admin configuration for voice intelligence models
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    ActionItem,
    CallScore,
    ConversationCategory,
    ConversationSummary,
    KeyMoment,
    RecordingCategory,
    SentimentAnalysis,
    Transcription,
    TranscriptionSettings,
    VoiceNote,
    VoiceRecording,
)


class TranscriptionInline(admin.StackedInline):
    model = Transcription
    extra = 0
    readonly_fields = [
        'provider', 'confidence_score', 'detected_language',
        'processing_time_seconds', 'word_count', 'created_at'
    ]

    def word_count(self, obj):
        return obj.word_count
    word_count.short_description = 'Word Count'


class ConversationSummaryInline(admin.TabularInline):
    model = ConversationSummary
    extra = 0
    readonly_fields = ['summary_type', 'created_at']
    fields = ['summary_type', 'summary_text', 'created_at']


class ActionItemInline(admin.TabularInline):
    model = ActionItem
    extra = 0
    fields = ['title', 'priority', 'status', 'assigned_to_name', 'due_date']
    readonly_fields = ['title']


class KeyMomentInline(admin.TabularInline):
    model = KeyMoment
    extra = 0
    fields = ['moment_type', 'start_timestamp', 'end_timestamp', 'summary']
    readonly_fields = ['moment_type', 'start_timestamp', 'end_timestamp', 'summary']


@admin.register(VoiceRecording)
class VoiceRecordingAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'owner', 'source_type', 'status_badge',
        'duration_formatted', 'recorded_at', 'has_transcription'
    ]
    list_filter = ['status', 'source_type', 'detected_language', 'created_at']
    search_fields = ['title', 'owner__username', 'owner__email']
    readonly_fields = [
        'id', 'duration_formatted', 'file_size_bytes', 'processing_started_at',
        'processing_completed_at', 'created_at', 'updated_at'
    ]
    inlines = [
        TranscriptionInline, ConversationSummaryInline,
        ActionItemInline, KeyMomentInline
    ]

    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'title', 'owner', 'source_type', 'status')
        }),
        ('File Info', {
            'fields': (
                'file_url', 'file_path', 'file_size_bytes', 'file_format',
                'duration_seconds', 'duration_formatted'
            )
        }),
        ('Audio Quality', {
            'fields': ('sample_rate', 'channels', 'bitrate'),
            'classes': ('collapse',)
        }),
        ('Participants', {
            'fields': ('participants', 'participant_count')
        }),
        ('Related Records', {
            'fields': ('contact', 'lead', 'opportunity', 'meeting')
        }),
        ('Processing', {
            'fields': (
                'processing_started_at', 'processing_completed_at',
                'processing_error', 'detected_language'
            )
        }),
        ('Timestamps', {
            'fields': ('recorded_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'uploading': '#FFA500',
            'uploaded': '#3498db',
            'processing': '#9b59b6',
            'transcribing': '#9b59b6',
            'transcribed': '#2ecc71',
            'analyzing': '#9b59b6',
            'completed': '#27ae60',
            'failed': '#e74c3c'
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def has_transcription(self, obj):
        return hasattr(obj, 'transcription')
    has_transcription.boolean = True
    has_transcription.short_description = 'Transcribed'


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'recording', 'provider', 'detected_language',
        'word_count', 'confidence_score', 'was_edited'
    ]
    list_filter = ['provider', 'detected_language', 'was_edited']
    search_fields = ['recording__title', 'full_text']
    readonly_fields = ['word_count', 'created_at', 'updated_at']

    def word_count(self, obj):
        return obj.word_count
    word_count.short_description = 'Words'


@admin.register(ConversationSummary)
class ConversationSummaryAdmin(admin.ModelAdmin):
    list_display = ['recording', 'summary_type', 'created_at']
    list_filter = ['summary_type', 'created_at']
    search_fields = ['recording__title', 'summary_text']
    readonly_fields = ['created_at']


@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'recording', 'priority_badge', 'status_badge',
        'assigned_to_name', 'due_date', 'was_confirmed'
    ]
    list_filter = ['priority', 'status', 'was_confirmed', 'created_at']
    search_fields = ['title', 'description', 'recording__title']
    readonly_fields = ['created_at', 'updated_at']

    def priority_badge(self, obj):
        colors = {
            'low': '#95a5a6',
            'medium': '#3498db',
            'high': '#e67e22',
            'critical': '#e74c3c'
        }
        color = colors.get(obj.priority, '#95a5a6')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'in_progress': '#3498db',
            'completed': '#27ae60',
            'cancelled': '#95a5a6'
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'recording', 'sentiment_badge', 'overall_score',
        'dominant_emotion', 'engagement_score'
    ]
    list_filter = ['overall_sentiment', 'dominant_emotion']
    readonly_fields = ['created_at']

    def sentiment_badge(self, obj):
        colors = {
            'very_negative': '#c0392b',
            'negative': '#e74c3c',
            'neutral': '#95a5a6',
            'positive': '#2ecc71',
            'very_positive': '#27ae60'
        }
        color = colors.get(obj.overall_sentiment, '#95a5a6')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_overall_sentiment_display()
        )
    sentiment_badge.short_description = 'Sentiment'


@admin.register(KeyMoment)
class KeyMomentAdmin(admin.ModelAdmin):
    list_display = [
        'recording', 'moment_type', 'timestamp_range',
        'speaker', 'importance_score', 'is_ai_detected'
    ]
    list_filter = ['moment_type', 'is_ai_detected', 'created_at']
    search_fields = ['recording__title', 'transcript_excerpt', 'summary']
    readonly_fields = ['created_at']

    def timestamp_range(self, obj):
        return f"{obj.start_timestamp}s - {obj.end_timestamp}s"
    timestamp_range.short_description = 'Time Range'


@admin.register(CallScore)
class CallScoreAdmin(admin.ModelAdmin):
    list_display = [
        'recording', 'score_display', 'opening_score', 'discovery_score',
        'closing_score', 'talk_to_listen_ratio', 'question_count'
    ]
    list_filter = ['created_at']
    search_fields = ['recording__title']
    readonly_fields = ['created_at']

    def score_display(self, obj):
        score = obj.overall_score
        if score >= 80:
            color = '#27ae60'
        elif score >= 60:
            color = '#f39c12'
        else:
            color = '#e74c3c'
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{}/100</span>',
            color, score
        )
    score_display.short_description = 'Overall Score'


@admin.register(VoiceNote)
class VoiceNoteAdmin(admin.ModelAdmin):
    list_display = [
        'ai_title', 'owner', 'duration_seconds',
        'is_transcribed', 'contact', 'lead', 'created_at'
    ]
    list_filter = ['is_transcribed', 'created_at']
    search_fields = ['ai_title', 'transcript', 'owner__username']
    readonly_fields = ['created_at']


@admin.register(ConversationCategory)
class ConversationCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'parent', 'recording_count']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    readonly_fields = ['recording_count', 'created_at']

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 10px; '
            'border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'


@admin.register(RecordingCategory)
class RecordingCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'recording', 'category', 'is_auto_classified',
        'confidence', 'classified_at'
    ]
    list_filter = ['category', 'is_auto_classified']
    search_fields = ['recording__title', 'category__name']


@admin.register(TranscriptionSettings)
class TranscriptionSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'preferred_provider', 'default_language',
        'auto_generate_summary', 'auto_score_calls'
    ]
    list_filter = [
        'preferred_provider', 'auto_generate_summary',
        'auto_analyze_sentiment', 'auto_score_calls'
    ]
    search_fields = ['user__username', 'user__email']
