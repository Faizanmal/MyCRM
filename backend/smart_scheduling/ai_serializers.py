"""
Smart Scheduling AI Serializers
API serializers for AI-enhanced scheduling features
"""

from rest_framework import serializers

from .ai_models import (
    AISchedulingPreference,
    AITimeSuggestion,
    AttendeeIntelligence,
    MeetingPrepAI,
    NoShowPrediction,
    ScheduleOptimization,
    SmartReminder,
    SmartReschedule,
)


class AISchedulingPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for AI scheduling preferences"""

    class Meta:
        model = AISchedulingPreference
        fields = [
            'id', 'user', 'preferred_meeting_times', 'preferred_days',
            'preferred_meeting_duration', 'max_meetings_per_day',
            'max_consecutive_meetings', 'focus_time_start', 'focus_time_end',
            'focus_days', 'high_energy_hours', 'low_energy_hours',
            'meeting_type_preferences', 'min_gap_between_meetings',
            'prefer_batched_meetings', 'batch_meeting_days',
            'data_points_count', 'last_learning_at', 'preference_confidence',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'data_points_count', 'last_learning_at',
            'preference_confidence', 'created_at', 'updated_at'
        ]


class AITimeSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for AI time suggestions"""

    meeting_type_name = serializers.CharField(source='meeting_type.name', read_only=True)

    class Meta:
        model = AITimeSuggestion
        fields = [
            'id', 'user', 'meeting_type', 'meeting_type_name', 'suggestion_type',
            'suggested_start', 'suggested_end', 'overall_score', 'preference_score',
            'availability_score', 'energy_score', 'context_switch_score',
            'reasoning', 'factors', 'participant_email', 'participant_timezone',
            'mutual_availability', 'was_accepted', 'feedback',
            'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class NoShowPredictionSerializer(serializers.ModelSerializer):
    """Serializer for no-show predictions"""

    meeting_guest = serializers.CharField(source='meeting.guest_name', read_only=True)
    meeting_time = serializers.DateTimeField(source='meeting.start_time', read_only=True)

    class Meta:
        model = NoShowPrediction
        fields = [
            'id', 'meeting', 'meeting_guest', 'meeting_time',
            'no_show_probability', 'prediction_confidence', 'risk_factors',
            'risk_score', 'guest_meeting_history', 'historical_no_show_rate',
            'days_until_meeting', 'meeting_time_of_day', 'day_of_week',
            'email_open_rate', 'previous_reschedules', 'confirmation_sent',
            'confirmation_opened', 'recommended_actions', 'extra_reminder_suggested',
            'confirmation_call_suggested', 'actual_outcome', 'prediction_was_correct',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MeetingPrepAISerializer(serializers.ModelSerializer):
    """Serializer for AI meeting prep materials"""

    meeting_details = serializers.SerializerMethodField()

    class Meta:
        model = MeetingPrepAI
        fields = [
            'id', 'meeting', 'meeting_details', 'participant_summary',
            'company_info', 'linkedin_data', 'recent_news',
            'crm_contact_summary', 'previous_interactions', 'open_opportunities',
            'pending_tasks', 'meeting_history_with_contact', 'last_meeting_summary',
            'last_meeting_action_items', 'suggested_agenda', 'talking_points',
            'questions_to_ask', 'potential_objections', 'personalization_tips',
            'ice_breakers', 'mutual_connections', 'deal_stage', 'deal_value',
            'win_probability', 'recommended_next_steps',
            'prep_generated_at', 'last_updated_at', 'was_helpful', 'feedback'
        ]
        read_only_fields = ['id', 'prep_generated_at', 'last_updated_at']

    def get_meeting_details(self, obj):
        return {
            'id': str(obj.meeting.id),
            'guest_name': obj.meeting.guest_name,
            'guest_email': obj.meeting.guest_email,
            'start_time': obj.meeting.start_time.isoformat(),
            'meeting_type': obj.meeting.meeting_type.name if obj.meeting.meeting_type else ''
        }


class SmartRescheduleSerializer(serializers.ModelSerializer):
    """Serializer for smart reschedule suggestions"""

    meeting_info = serializers.SerializerMethodField()

    class Meta:
        model = SmartReschedule
        fields = [
            'id', 'meeting', 'meeting_info', 'trigger_type', 'trigger_reason',
            'original_start', 'original_end', 'alternatives',
            'suggested_start', 'suggested_end', 'suggestion_score',
            'status', 'notification_sent', 'notification_sent_at',
            'host_notified', 'guest_notified', 'response_by',
            'selected_alternative', 'response_at', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_meeting_info(self, obj):
        return {
            'id': str(obj.meeting.id),
            'guest_name': obj.meeting.guest_name,
            'meeting_type': obj.meeting.meeting_type.name if obj.meeting.meeting_type else ''
        }


class SmartReminderSerializer(serializers.ModelSerializer):
    """Serializer for smart reminders"""

    meeting_info = serializers.SerializerMethodField()

    class Meta:
        model = SmartReminder
        fields = [
            'id', 'meeting', 'meeting_info', 'scheduled_at', 'minutes_before',
            'is_ai_optimized', 'optimization_reason', 'optimal_channel',
            'channel_preference_score', 'subject', 'message',
            'include_prep_material', 'include_agenda', 'sent', 'sent_at',
            'delivery_status', 'opened', 'opened_at', 'clicked', 'clicked_at',
            'recipient_type', 'recipient_email', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_meeting_info(self, obj):
        return {
            'id': str(obj.meeting.id),
            'guest_name': obj.meeting.guest_name,
            'start_time': obj.meeting.start_time.isoformat()
        }


class ScheduleOptimizationSerializer(serializers.ModelSerializer):
    """Serializer for schedule optimizations"""

    class Meta:
        model = ScheduleOptimization
        fields = [
            'id', 'user', 'optimization_type', 'analysis_start', 'analysis_end',
            'current_schedule', 'current_metrics', 'optimized_schedule',
            'optimized_metrics', 'meetings_affected', 'time_saved_minutes',
            'focus_time_gained_minutes', 'context_switches_reduced',
            'current_score', 'optimized_score', 'improvement_percentage',
            'recommendations', 'explanation', 'status', 'applied', 'applied_at',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class AttendeeIntelligenceSerializer(serializers.ModelSerializer):
    """Serializer for attendee intelligence"""

    attendance_rate = serializers.FloatField(read_only=True)
    no_show_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = AttendeeIntelligence
        fields = [
            'id', 'email', 'name', 'preferred_meeting_times',
            'response_time_average', 'typical_response_days',
            'total_meetings_scheduled', 'meetings_attended', 'meetings_no_show',
            'meetings_cancelled', 'meetings_rescheduled', 'attendance_rate',
            'no_show_rate', 'average_meeting_duration', 'prefers_video',
            'prefers_phone', 'detected_timezone', 'timezone_confidence',
            'reminder_response_rate', 'best_reminder_timing',
            'best_communication_channel', 'reliability_score', 'engagement_score',
            'last_meeting_at', 'last_interaction_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'attendance_rate', 'no_show_rate',
            'created_at', 'updated_at'
        ]


# Request/Response Serializers

class FindOptimalTimesRequestSerializer(serializers.Serializer):
    """Request serializer for finding optimal times"""

    meeting_type_id = serializers.UUIDField()
    duration_minutes = serializers.IntegerField(min_value=5, max_value=480)
    date_range_days = serializers.IntegerField(min_value=1, max_value=90, default=14)
    participant_email = serializers.EmailField(required=False, allow_blank=True)
    num_suggestions = serializers.IntegerField(min_value=1, max_value=20, default=5)


class OptimalTimeResponseSerializer(serializers.Serializer):
    """Response serializer for optimal time suggestions"""

    id = serializers.CharField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    overall_score = serializers.FloatField()
    scores = serializers.DictField()
    reasons = serializers.ListField(child=serializers.CharField())


class PredictNoShowRequestSerializer(serializers.Serializer):
    """Request serializer for no-show prediction"""

    meeting_id = serializers.UUIDField()


class NoShowPredictionResponseSerializer(serializers.Serializer):
    """Response serializer for no-show prediction"""

    id = serializers.CharField()
    meeting_id = serializers.CharField()
    no_show_probability = serializers.FloatField()
    risk_score = serializers.IntegerField()
    risk_factors = serializers.ListField()
    recommended_actions = serializers.ListField()
    extra_reminder_suggested = serializers.BooleanField()
    confirmation_call_suggested = serializers.BooleanField()


class GenerateMeetingPrepRequestSerializer(serializers.Serializer):
    """Request serializer for meeting prep generation"""

    meeting_id = serializers.UUIDField()


class SetupSmartRemindersRequestSerializer(serializers.Serializer):
    """Request serializer for smart reminders setup"""

    meeting_id = serializers.UUIDField()


class SuggestRescheduleRequestSerializer(serializers.Serializer):
    """Request serializer for reschedule suggestions"""

    meeting_id = serializers.UUIDField()
    trigger_type = serializers.ChoiceField(
        choices=['conflict', 'optimization', 'no_show_risk', 'user_request', 'emergency'],
        default='optimization'
    )
    trigger_reason = serializers.CharField(required=False, allow_blank=True)


class OptimizeScheduleRequestSerializer(serializers.Serializer):
    """Request serializer for schedule optimization"""

    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    optimization_type = serializers.ChoiceField(
        choices=[
            'batch_meetings', 'create_focus_time', 'reduce_context_switch',
            'energy_alignment', 'travel_optimization'
        ],
        default='create_focus_time'
    )


class LearnPreferencesResponseSerializer(serializers.Serializer):
    """Response serializer for learn preferences"""

    preferences_updated = serializers.BooleanField()
    data_points_analyzed = serializers.IntegerField()
    preferred_times = serializers.DictField()
    preferred_days = serializers.DictField()
    high_energy_hours = serializers.ListField()
    confidence = serializers.FloatField()


class MeetingPrepFeedbackSerializer(serializers.Serializer):
    """Serializer for meeting prep feedback"""

    meeting_prep_id = serializers.UUIDField()
    was_helpful = serializers.BooleanField()
    feedback = serializers.CharField(required=False, allow_blank=True)
