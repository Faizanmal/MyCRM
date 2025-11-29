from django.contrib import admin
from .models import (
    SchedulingPage, MeetingType, Availability, BlockedTime,
    Meeting, MeetingReminder, CalendarIntegration, SchedulingAnalytics
)


@admin.register(SchedulingPage)
class SchedulingPageAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'slug', 'is_active', 'page_views', 'bookings_count', 'conversion_rate']
    list_filter = ['is_active']
    search_fields = ['name', 'owner__username', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MeetingType)
class MeetingTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'page', 'duration_minutes', 'location_type', 'is_active', 'bookings_count']
    list_filter = ['location_type', 'is_active', 'page']
    search_fields = ['name']


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['page', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'page']


@admin.register(BlockedTime)
class BlockedTimeAdmin(admin.ModelAdmin):
    list_display = ['page', 'title', 'start_datetime', 'end_datetime', 'all_day']
    list_filter = ['all_day', 'page']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'guest_email', 'meeting_type', 'host', 'start_time', 'status']
    list_filter = ['status', 'meeting_type', 'host']
    search_fields = ['guest_name', 'guest_email', 'host__username']
    date_hierarchy = 'start_time'


@admin.register(MeetingReminder)
class MeetingReminderAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'reminder_type', 'minutes_before', 'scheduled_at', 'is_sent']
    list_filter = ['reminder_type', 'is_sent']


@admin.register(CalendarIntegration)
class CalendarIntegrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'sync_enabled', 'is_active', 'last_synced_at']
    list_filter = ['provider', 'is_active']


@admin.register(SchedulingAnalytics)
class SchedulingAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['page', 'date', 'page_views', 'bookings_created', 'bookings_completed']
    list_filter = ['page', 'date']
    date_hierarchy = 'date'
