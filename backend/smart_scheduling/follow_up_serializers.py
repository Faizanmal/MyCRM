"""
Follow-up and Calendar Sync Serializers
"""

from rest_framework import serializers
from .follow_up_models import (
    MeetingFollowUp,
    FollowUpSequence,
    MeetingOutcome,
    RecurringMeetingPattern,
    MeetingAnalytics,
    CalendarEvent
)


class MeetingFollowUpSerializer(serializers.ModelSerializer):
    """Serializer for meeting follow-ups"""
    
    meeting_title = serializers.CharField(source='meeting.meeting_type.name', read_only=True)
    guest_name = serializers.CharField(source='meeting.guest_name', read_only=True)
    
    class Meta:
        model = MeetingFollowUp
        fields = [
            'id', 'meeting', 'meeting_title', 'guest_name',
            'follow_up_type', 'scheduled_at', 'delay_hours',
            'subject', 'body', 'is_ai_generated',
            'personalization_context', 'attachments',
            'status', 'sent_at', 'opened_at', 'clicked_at', 'replied_at',
            'last_error', 'retry_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'sent_at', 'opened_at', 'clicked_at', 'replied_at']


class FollowUpSequenceSerializer(serializers.ModelSerializer):
    """Serializer for follow-up sequences"""
    
    steps_count = serializers.SerializerMethodField()
    meeting_type_names = serializers.SerializerMethodField()
    
    class Meta:
        model = FollowUpSequence
        fields = [
            'id', 'name', 'description',
            'meeting_types', 'meeting_type_names', 'apply_to_all',
            'steps', 'steps_count',
            'is_active', 'use_ai_personalization',
            'times_used', 'avg_reply_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'times_used', 'avg_reply_rate', 'created_at', 'updated_at']
    
    def get_steps_count(self, obj):
        return len(obj.steps) if obj.steps else 0
    
    def get_meeting_type_names(self, obj):
        return [mt.name for mt in obj.meeting_types.all()]


class MeetingOutcomeSerializer(serializers.ModelSerializer):
    """Serializer for meeting outcomes"""
    
    meeting_title = serializers.CharField(source='meeting.meeting_type.name', read_only=True)
    guest_name = serializers.CharField(source='meeting.guest_name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.username', read_only=True)
    
    class Meta:
        model = MeetingOutcome
        fields = [
            'id', 'meeting', 'meeting_title', 'guest_name',
            'outcome', 'notes', 'action_items',
            'next_meeting_scheduled', 'next_meeting_date',
            'ai_summary', 'key_points', 'sentiment_score',
            'deal_progressed', 'new_deal_stage',
            'recorded_at', 'recorded_by', 'recorded_by_name'
        ]
        read_only_fields = ['id', 'recorded_at', 'ai_summary', 'key_points', 'sentiment_score']


class RecurringMeetingPatternSerializer(serializers.ModelSerializer):
    """Serializer for recurring meeting patterns"""
    
    meeting_type_name = serializers.CharField(source='meeting_type.name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    
    class Meta:
        model = RecurringMeetingPattern
        fields = [
            'id', 'name', 'frequency',
            'meeting_type', 'meeting_type_name',
            'day_of_week', 'day_of_month', 'preferred_time',
            'contact', 'contact_name',
            'is_active', 'next_occurrence',
            'auto_schedule', 'auto_schedule_days_ahead',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'next_occurrence', 'created_at', 'updated_at']


class MeetingAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for meeting analytics"""
    
    class Meta:
        model = MeetingAnalytics
        fields = [
            'id', 'period_type', 'period_start', 'period_end',
            'total_meetings', 'completed_meetings', 'cancelled_meetings',
            'no_show_meetings', 'rescheduled_meetings',
            'total_meeting_minutes', 'avg_meeting_duration',
            'meetings_by_type', 'meetings_by_day', 'meetings_by_hour',
            'positive_outcomes', 'neutral_outcomes', 'negative_outcomes',
            'follow_ups_sent', 'follow_ups_opened', 'follow_ups_replied',
            'meetings_to_opportunities', 'conversion_rate',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CalendarEventSerializer(serializers.ModelSerializer):
    """Serializer for synced calendar events"""
    
    provider = serializers.CharField(source='integration.provider', read_only=True)
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'integration', 'provider',
            'external_id', 'external_link',
            'title', 'description', 'location',
            'start_time', 'end_time', 'all_day', 'timezone',
            'status', 'is_busy',
            'organizer_email', 'attendees',
            'is_recurring', 'recurrence_id',
            'last_synced_at', 'etag'
        ]
        read_only_fields = ['id', 'last_synced_at']


# Request Serializers

class ScheduleFollowUpsRequestSerializer(serializers.Serializer):
    """Request serializer for scheduling follow-ups"""
    meeting_id = serializers.UUIDField()
    sequence_id = serializers.UUIDField(required=False)


class RecordOutcomeRequestSerializer(serializers.Serializer):
    """Request serializer for recording meeting outcomes"""
    meeting_id = serializers.UUIDField()
    outcome = serializers.ChoiceField(choices=[
        'positive', 'neutral', 'negative', 'no_show', 'rescheduled'
    ])
    notes = serializers.CharField(required=False, allow_blank=True)
    action_items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )


class CreateSequenceRequestSerializer(serializers.Serializer):
    """Request serializer for creating follow-up sequences"""
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    steps = serializers.ListField(child=serializers.DictField())
    meeting_type_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=[]
    )
    apply_to_all = serializers.BooleanField(default=False)
    use_ai_personalization = serializers.BooleanField(default=True)


class CreateFromTemplateRequestSerializer(serializers.Serializer):
    """Request serializer for creating sequence from template"""
    template_name = serializers.CharField()


class SyncCalendarRequestSerializer(serializers.Serializer):
    """Request serializer for calendar sync"""
    integration_id = serializers.UUIDField()


class CheckConflictsRequestSerializer(serializers.Serializer):
    """Request serializer for checking conflicts"""
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    exclude_meeting_id = serializers.UUIDField(required=False)


class GetAvailabilityRequestSerializer(serializers.Serializer):
    """Request serializer for getting availability"""
    date = serializers.DateField()
    duration_minutes = serializers.IntegerField(default=30)


class FindCommonTimeRequestSerializer(serializers.Serializer):
    """Request serializer for finding common free time"""
    participant_emails = serializers.ListField(child=serializers.EmailField())
    duration_minutes = serializers.IntegerField(default=30)
    date_range_days = serializers.IntegerField(default=7)


class AnalyzeCalendarRequestSerializer(serializers.Serializer):
    """Request serializer for calendar analysis"""
    days = serializers.IntegerField(default=30, min_value=7, max_value=365)


class UnifiedCalendarRequestSerializer(serializers.Serializer):
    """Request serializer for unified calendar view"""
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()


class CreateRecurringPatternRequestSerializer(serializers.Serializer):
    """Request serializer for creating recurring patterns"""
    name = serializers.CharField(max_length=200)
    meeting_type_id = serializers.UUIDField()
    frequency = serializers.ChoiceField(choices=[
        'daily', 'weekly', 'biweekly', 'monthly', 'quarterly'
    ])
    day_of_week = serializers.IntegerField(required=False, min_value=0, max_value=6)
    day_of_month = serializers.IntegerField(required=False, min_value=1, max_value=31)
    preferred_time = serializers.TimeField()
    contact_id = serializers.UUIDField(required=False)
    auto_schedule = serializers.BooleanField(default=False)
    auto_schedule_days_ahead = serializers.IntegerField(default=7)
