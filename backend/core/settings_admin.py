"""
Settings Admin Configuration
Admin interface for managing user preferences, notification settings, export jobs, and RBAC
"""

from django.contrib import admin
from django.utils.html import format_html

from .settings_models import (
    UserPreference,
    NotificationPreference,
    NotificationTypeSetting,
    ExportJob,
    UserRole,
    UserRoleAssignment,
)


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'accent_color_preview', 'default_view', 'compact_mode', 'updated_at']
    list_filter = ['theme', 'default_view', 'compact_mode', 'animations_enabled']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Appearance', {
            'fields': ('theme', 'accent_color', 'font_size', 'compact_mode', 'animations_enabled', 'high_contrast')
        }),
        ('Dashboard', {
            'fields': ('default_view', 'sidebar_collapsed', 'show_welcome_message', 'auto_refresh_enabled', 'auto_refresh_interval', 'dashboard_layout')
        }),
        ('Privacy', {
            'fields': ('share_activity_with_team', 'show_online_status', 'allow_mentions', 'data_export_enabled')
        }),
        ('Sound', {
            'fields': ('sound_enabled', 'sound_volume')
        }),
        ('Keyboard Shortcuts', {
            'fields': ('keyboard_shortcuts',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def accent_color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 12px; border-radius: 4px;">&nbsp;</span> {}',
            obj.accent_color,
            obj.accent_color
        )
    accent_color_preview.short_description = 'Accent Color'


class NotificationTypeSettingInline(admin.TabularInline):
    model = NotificationTypeSetting
    extra = 0
    fields = ['notification_type', 'email_enabled', 'push_enabled', 'in_app_enabled', 'sms_enabled', 'frequency', 'priority']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_enabled', 'push_enabled', 'in_app_enabled', 'sms_enabled', 'quiet_hours_enabled', 'digest_enabled']
    list_filter = ['email_enabled', 'push_enabled', 'quiet_hours_enabled', 'digest_enabled']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [NotificationTypeSettingInline]
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Channels', {
            'fields': ('email_enabled', 'push_enabled', 'in_app_enabled', 'sms_enabled')
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end', 'quiet_hours_days')
        }),
        ('Email Digest', {
            'fields': ('digest_enabled', 'digest_frequency', 'digest_time', 'digest_include_ai', 'digest_include_metrics')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'format', 'entities_display', 'status_badge', 'progress', 'file_size_display', 'created_at']
    list_filter = ['status', 'format', 'date_range', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'started_at', 'completed_at', 'expires_at', 'progress', 'file_path', 'file_size']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Job Info', {
            'fields': ('user', 'format', 'entities', 'date_range')
        }),
        ('Options', {
            'fields': ('include_archived', 'include_deleted')
        }),
        ('Status', {
            'fields': ('status', 'progress', 'error_message')
        }),
        ('File', {
            'fields': ('file_path', 'file_size')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at', 'expires_at')
        }),
    )
    
    def entities_display(self, obj):
        return ', '.join(obj.entities) if obj.entities else '-'
    entities_display.short_description = 'Entities'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'processing': '#3b82f6',
            'completed': '#22c55e',
            'failed': '#ef4444',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px;">{}</span>',
            colors.get(obj.status, '#gray'),
            obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size >= 1024 * 1024:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
            elif obj.file_size >= 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size} B"
        return '-'
    file_size_display.short_description = 'File Size'
    
    actions = ['cancel_jobs', 'retry_failed_jobs']
    
    def cancel_jobs(self, request, queryset):
        count = 0
        for job in queryset.filter(status__in=['pending', 'processing']):
            job.mark_failed('Cancelled by admin')
            count += 1
        self.message_user(request, f'{count} jobs cancelled')
    cancel_jobs.short_description = 'Cancel selected jobs'
    
    def retry_failed_jobs(self, request, queryset):
        count = 0
        for job in queryset.filter(status='failed'):
            job.status = 'pending'
            job.progress = 0
            job.error_message = None
            job.save()
            count += 1
            # Trigger async processing
            # process_export_job.delay(job.id)
        self.message_user(request, f'{count} jobs queued for retry')
    retry_failed_jobs.short_description = 'Retry failed jobs'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'level', 'permissions_count', 'is_system_role', 'color_preview']
    list_filter = ['is_system_role', 'level']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Role Info', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Configuration', {
            'fields': ('level', 'permissions', 'color', 'is_system_role')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def permissions_count(self, obj):
        return len(obj.permissions) if obj.permissions else 0
    permissions_count.short_description = 'Permissions'
    
    def color_preview(self, obj):
        return format_html(
            '<span class="{}" style="padding: 2px 8px; border-radius: 4px;">{}</span>',
            obj.color,
            obj.display_name
        )
    color_preview.short_description = 'Color Preview'
    
    actions = ['initialize_default_roles']
    
    def initialize_default_roles(self, request, queryset):
        UserRole.create_default_roles()
        self.message_user(request, 'Default roles initialized')
    initialize_default_roles.short_description = 'Initialize default roles'


@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'team_id', 'organization_id', 'assigned_by', 'assigned_at']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__username', 'user__email', 'role__name']
    readonly_fields = ['assigned_at']
    autocomplete_fields = ['user', 'role', 'assigned_by']
    
    fieldsets = (
        ('Assignment', {
            'fields': ('user', 'role')
        }),
        ('Scope', {
            'fields': ('team_id', 'organization_id'),
            'classes': ('collapse',)
        }),
        ('Meta', {
            'fields': ('assigned_by', 'assigned_at')
        }),
    )
