from django.contrib import admin

from .models import (
    KPI,
    Dashboard,
    DashboardWidget,
    KPIValue,
    Report,
    ReportExecution,
    ReportSchedule,
)


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'dashboard_type', 'is_default', 'is_public', 'created_at']
    list_filter = ['dashboard_type', 'is_default', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    filter_horizontal = ['shared_with']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'dashboard_type', 'owner')
        }),
        ('Sharing Settings', {
            'fields': ('is_default', 'is_public', 'shared_with')
        }),
        ('Configuration', {
            'fields': ('layout',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'dashboard', 'widget_type', 'data_source', 'position_x', 'position_y']
    list_filter = ['widget_type', 'data_source', 'is_active']
    search_fields = ['name', 'dashboard__name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('dashboard', 'name', 'widget_type', 'data_source')
        }),
        ('Position & Size', {
            'fields': ('position_x', 'position_y', 'width', 'height', 'order')
        }),
        ('Configuration', {
            'fields': ('query_config', 'display_config', 'refresh_interval')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'owner', 'export_format', 'is_public', 'created_at']
    list_filter = ['report_type', 'export_format', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    filter_horizontal = ['shared_with']
    readonly_fields = ['created_at', 'updated_at', 'last_generated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'report_type', 'owner')
        }),
        ('Data Configuration', {
            'fields': ('data_sources', 'filters', 'columns', 'grouping', 'sorting', 'calculations')
        }),
        ('Export Settings', {
            'fields': ('export_format', 'include_charts', 'include_summary')
        }),
        ('Sharing', {
            'fields': ('is_public', 'shared_with')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_generated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'report', 'frequency', 'delivery_method', 'is_active', 'next_run_at']
    list_filter = ['frequency', 'delivery_method', 'is_active']
    search_fields = ['name', 'report__name']
    readonly_fields = ['last_sent_at', 'next_run_at', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('report', 'name', 'frequency', 'delivery_method')
        }),
        ('Schedule Configuration', {
            'fields': ('schedule_time', 'day_of_week', 'day_of_month')
        }),
        ('Delivery Configuration', {
            'fields': ('recipients', 'delivery_config')
        }),
        ('Status', {
            'fields': ('is_active', 'last_sent_at', 'next_run_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    list_display = ['report', 'executed_by', 'status', 'started_at', 'completed_at', 'rows_returned']
    list_filter = ['status', 'started_at']
    search_fields = ['report__name', 'executed_by__username']
    readonly_fields = ['report', 'schedule', 'executed_by', 'status', 'started_at', 'completed_at', 'filters_used', 'rows_returned', 'file_path', 'error_message']

    fieldsets = (
        ('Execution Information', {
            'fields': ('report', 'schedule', 'executed_by', 'status')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Results', {
            'fields': ('filters_used', 'rows_returned', 'file_path', 'file_size_bytes', 'error_message')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ['name', 'kpi_type', 'owner', 'target_value', 'unit', 'is_active', 'created_at']
    list_filter = ['kpi_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'kpi_type', 'owner')
        }),
        ('Calculation', {
            'fields': ('calculation_formula', 'data_source')
        }),
        ('Target & Display', {
            'fields': ('target_value', 'unit', 'display_format', 'color_good', 'color_warning', 'color_bad')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(KPIValue)
class KPIValueAdmin(admin.ModelAdmin):
    list_display = ['kpi', 'value', 'period_start', 'period_end', 'change_percentage']
    list_filter = ['kpi', 'period_start']
    search_fields = ['kpi__name']
    readonly_fields = ['kpi', 'value', 'period_start', 'period_end', 'previous_value', 'change_percentage', 'metadata', 'calculated_at']
    date_hierarchy = 'period_start'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
