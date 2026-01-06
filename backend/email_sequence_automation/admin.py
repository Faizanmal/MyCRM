from django.contrib import admin

from .models import (
    ABTest,
    AutomatedTrigger,
    EmailPersonalizationToken,
    EmailSequence,
    SequenceActivity,
    SequenceAnalytics,
    SequenceEmail,
    SequenceEnrollment,
    SequenceStep,
)


@admin.register(EmailSequence)
class EmailSequenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'total_enrolled', 'total_completed', 'conversion_rate', 'created_at']
    list_filter = ['status', 'trigger_type', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['total_enrolled', 'total_completed', 'total_converted', 'avg_open_rate', 'avg_click_rate', 'avg_reply_rate']


@admin.register(SequenceStep)
class SequenceStepAdmin(admin.ModelAdmin):
    list_display = ['name', 'sequence', 'step_type', 'step_number', 'is_active', 'total_executed']
    list_filter = ['step_type', 'is_active']
    search_fields = ['name', 'sequence__name']


@admin.register(SequenceEmail)
class SequenceEmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'step', 'variant_name', 'is_winner', 'total_sent', 'open_rate', 'click_rate']
    list_filter = ['is_winner', 'ai_generated']
    search_fields = ['subject', 'step__name']


@admin.register(SequenceEnrollment)
class SequenceEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['contact', 'sequence', 'status', 'current_step', 'enrolled_at', 'emails_sent']
    list_filter = ['status', 'enrolled_at']
    search_fields = ['contact__email', 'contact__first_name', 'contact__last_name', 'sequence__name']


@admin.register(SequenceActivity)
class SequenceActivityAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'activity_type', 'step', 'timestamp']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['enrollment__contact__email', 'description']


@admin.register(ABTest)
class ABTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'step', 'test_metric', 'status', 'winning_variant', 'created_at']
    list_filter = ['status', 'test_metric']
    search_fields = ['name', 'step__name']


@admin.register(AutomatedTrigger)
class AutomatedTriggerAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'sequence', 'is_active', 'total_triggered', 'last_triggered_at']
    list_filter = ['trigger_type', 'is_active']
    search_fields = ['name', 'sequence__name']


@admin.register(EmailPersonalizationToken)
class EmailPersonalizationTokenAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'token_type', 'is_system', 'is_active']
    list_filter = ['token_type', 'is_system', 'is_active']
    search_fields = ['name', 'display_name']


@admin.register(SequenceAnalytics)
class SequenceAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['sequence', 'date', 'new_enrollments', 'emails_sent', 'open_rate', 'click_rate']
    list_filter = ['date']
    search_fields = ['sequence__name']
