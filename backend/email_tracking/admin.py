from django.contrib import admin

from .models import (
    EmailAnalytics,
    EmailEvent,
    EmailSequence,
    EmailTemplate,
    SequenceEnrollment,
    SequenceStep,
    TrackedEmail,
)


@admin.register(TrackedEmail)
class TrackedEmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'to_email', 'sender', 'status', 'open_count', 'click_count', 'sent_at']
    list_filter = ['status', 'sent_at']
    search_fields = ['subject', 'to_email', 'sender__email']
    readonly_fields = ['tracking_id', 'sent_at', 'delivered_at', 'first_opened_at',
                       'last_opened_at', 'first_clicked_at', 'open_count', 'click_count']


@admin.register(EmailEvent)
class EmailEventAdmin(admin.ModelAdmin):
    list_display = ['email', 'event_type', 'timestamp', 'device_type', 'email_client']
    list_filter = ['event_type', 'device_type', 'email_client']
    search_fields = ['email__subject']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'owner', 'times_used', 'avg_open_rate', 'avg_reply_rate', 'is_shared']
    list_filter = ['category', 'is_shared', 'is_active']
    search_fields = ['name', 'subject']


@admin.register(EmailSequence)
class EmailSequenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'total_enrolled', 'total_replied', 'reply_rate']
    list_filter = ['status']
    search_fields = ['name']


@admin.register(SequenceStep)
class SequenceStepAdmin(admin.ModelAdmin):
    list_display = ['sequence', 'order', 'step_type', 'sent_count', 'open_rate', 'reply_rate']
    list_filter = ['step_type']


@admin.register(SequenceEnrollment)
class SequenceEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['contact', 'sequence', 'status', 'current_step', 'enrolled_at']
    list_filter = ['status', 'sequence']
    search_fields = ['contact__email', 'contact__first_name', 'contact__last_name']


@admin.register(EmailAnalytics)
class EmailAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'emails_sent', 'emails_opened', 'open_rate', 'reply_rate']
    list_filter = ['date', 'user']
    date_hierarchy = 'date'
