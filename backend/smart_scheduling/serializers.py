"""
Smart Scheduling Serializers
"""

from rest_framework import serializers
from .models import (
    SchedulingPage, MeetingType, Availability, BlockedTime,
    Meeting, MeetingReminder, CalendarIntegration, SchedulingAnalytics
)


class AvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = Availability
        fields = '__all__'
        read_only_fields = ['id']


class MeetingTypeSerializer(serializers.ModelSerializer):
    bookings_count = serializers.ReadOnlyField()
    
    class Meta:
        model = MeetingType
        fields = '__all__'
        read_only_fields = ['id', 'bookings_count', 'created_at', 'updated_at']


class MeetingTypePublicSerializer(serializers.ModelSerializer):
    """Public serializer for booking pages"""
    class Meta:
        model = MeetingType
        fields = ['id', 'name', 'slug', 'description', 'duration_minutes', 
                  'location_type', 'color', 'custom_questions']


class SchedulingPageSerializer(serializers.ModelSerializer):
    meeting_types = MeetingTypeSerializer(many=True, read_only=True)
    availability = AvailabilitySerializer(many=True, read_only=True)
    booking_url = serializers.ReadOnlyField()
    conversion_rate = serializers.ReadOnlyField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = SchedulingPage
        fields = '__all__'
        read_only_fields = ['id', 'page_views', 'bookings_count', 'created_at', 'updated_at']


class SchedulingPagePublicSerializer(serializers.ModelSerializer):
    """Public serializer for external booking page"""
    meeting_types = MeetingTypePublicSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = SchedulingPage
        fields = ['name', 'slug', 'description', 'welcome_message', 'logo', 
                  'brand_color', 'timezone', 'meeting_types', 'owner_name']


class BlockedTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedTime
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class MeetingSerializer(serializers.ModelSerializer):
    meeting_type_name = serializers.CharField(source='meeting_type.name', read_only=True)
    host_name = serializers.CharField(source='host.get_full_name', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    
    class Meta:
        model = Meeting
        fields = '__all__'
        read_only_fields = ['id', 'host', 'cancel_token', 'reschedule_token', 
                           'created_at', 'updated_at']


class MeetingListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    meeting_type_name = serializers.CharField(source='meeting_type.name', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = Meeting
        fields = ['id', 'guest_name', 'guest_email', 'meeting_type_name', 
                  'start_time', 'end_time', 'status', 'duration_minutes']


class BookMeetingSerializer(serializers.Serializer):
    """Serializer for booking a meeting"""
    meeting_type_id = serializers.UUIDField()
    start_time = serializers.DateTimeField()
    guest_name = serializers.CharField(max_length=200)
    guest_email = serializers.EmailField()
    guest_phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    guest_timezone = serializers.CharField(max_length=50, default='UTC')
    notes = serializers.CharField(required=False, allow_blank=True)
    custom_answers = serializers.JSONField(required=False, default=dict)


class RescheduleMeetingSerializer(serializers.Serializer):
    """Serializer for rescheduling"""
    new_start_time = serializers.DateTimeField()
    reason = serializers.CharField(required=False, allow_blank=True)


class CancelMeetingSerializer(serializers.Serializer):
    """Serializer for cancellation"""
    reason = serializers.CharField(required=False, allow_blank=True)


class AvailableSlotsSerializer(serializers.Serializer):
    """Serializer for available time slots"""
    date = serializers.DateField()
    slots = serializers.ListField(child=serializers.DateTimeField())


class MeetingReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingReminder
        fields = '__all__'
        read_only_fields = ['id', 'sent_at', 'is_sent']


class CalendarIntegrationSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = CalendarIntegration
        fields = ['id', 'provider', 'provider_display', 'calendar_id', 'calendar_name',
                  'sync_enabled', 'check_conflicts', 'create_events', 'is_active', 
                  'last_synced_at', 'created_at']
        read_only_fields = ['id', 'last_synced_at', 'created_at']


class SchedulingAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulingAnalytics
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Dashboard statistics"""
    total_meetings = serializers.IntegerField()
    meetings_this_week = serializers.IntegerField()
    meetings_this_month = serializers.IntegerField()
    completion_rate = serializers.DecimalField(max_digits=5, decimal_places=1)
    no_show_rate = serializers.DecimalField(max_digits=5, decimal_places=1)
    avg_meeting_duration = serializers.IntegerField()
    busiest_day = serializers.CharField()
    busiest_time = serializers.CharField()
