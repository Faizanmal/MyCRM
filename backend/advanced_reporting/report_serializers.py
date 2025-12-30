"""
Custom Report Builder Serializers
"""

from rest_framework import serializers
from .report_models import (
    ReportTemplate, ReportWidget, SavedReport, ScheduledReport,
    ReportDashboard, DashboardWidget, DataSource, ReportFolder,
    ReportSubscription
)


class ReportWidgetSerializer(serializers.ModelSerializer):
    """Serializer for ReportWidget"""
    
    class Meta:
        model = ReportWidget
        fields = [
            'id', 'name', 'widget_type',
            'position_x', 'position_y', 'width', 'height',
            'data_source', 'query', 'aggregation',
            'config', 'colors',
            'drill_down_enabled', 'drill_down_config', 'click_action',
            'auto_refresh', 'refresh_interval',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ReportTemplate"""
    
    widgets = ReportWidgetSerializer(many=True, read_only=True)
    widget_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'report_type',
            'data_source', 'base_query',
            'layout_config', 'columns', 'grouping', 'sorting',
            'filters', 'dynamic_filters',
            'chart_config', 'calculated_fields',
            'visibility', 'shared_with',
            'is_favorite', 'folder', 'tags',
            'view_count', 'last_viewed_at',
            'widgets', 'widget_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'view_count', 'last_viewed_at', 'created_at', 'updated_at']
    
    def get_widget_count(self, obj):
        return obj.widgets.count()


class ReportTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing reports"""
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'report_type',
            'data_source', 'visibility', 'is_favorite',
            'folder', 'tags', 'view_count', 'last_viewed_at',
            'created_at', 'updated_at'
        ]


class SavedReportSerializer(serializers.ModelSerializer):
    """Serializer for SavedReport"""
    
    template_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedReport
        fields = [
            'id', 'template', 'template_name', 'name',
            'status', 'started_at', 'completed_at', 'execution_time_ms',
            'parameters', 'result_data', 'row_count',
            'export_format', 'file_url', 'file_size',
            'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_template_name(self, obj):
        return obj.template.name if obj.template else None


class SavedReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing saved reports"""
    
    template_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedReport
        fields = [
            'id', 'template', 'template_name', 'name',
            'status', 'execution_time_ms', 'row_count',
            'export_format', 'file_url',
            'created_at'
        ]
    
    def get_template_name(self, obj):
        return obj.template.name if obj.template else None


class ScheduledReportSerializer(serializers.ModelSerializer):
    """Serializer for ScheduledReport"""
    
    template_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduledReport
        fields = [
            'id', 'template', 'template_name', 'name',
            'frequency', 'schedule_time', 'day_of_week', 'day_of_month',
            'timezone', 'parameters', 'export_format',
            'delivery_method', 'delivery_config', 'recipients',
            'include_empty', 'attach_file', 'include_link',
            'is_active', 'next_run_at', 'last_run_at',
            'last_status', 'run_count', 'failure_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'next_run_at', 'last_run_at', 'last_status',
            'run_count', 'failure_count', 'created_at', 'updated_at'
        ]
    
    def get_template_name(self, obj):
        return obj.template.name if obj.template else None


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for DashboardWidget"""
    
    widget_details = ReportWidgetSerializer(source='widget', read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'widget', 'widget_details',
            'widget_type', 'config',
            'position_x', 'position_y', 'width', 'height',
            'title_override', 'config_overrides',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportDashboardSerializer(serializers.ModelSerializer):
    """Serializer for ReportDashboard"""
    
    dashboard_widgets = DashboardWidgetSerializer(many=True, read_only=True)
    widget_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportDashboard
        fields = [
            'id', 'name', 'description',
            'layout_type', 'grid_columns', 'layout_config',
            'theme', 'custom_css',
            'global_filters', 'date_range_filter',
            'is_public', 'public_token', 'shared_with', 'embed_enabled',
            'auto_refresh', 'refresh_interval',
            'is_favorite', 'is_default', 'view_count',
            'dashboard_widgets', 'widget_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'public_token', 'view_count',
            'created_at', 'updated_at'
        ]
    
    def get_widget_count(self, obj):
        return obj.dashboard_widgets.count()


class ReportDashboardListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing dashboards"""
    
    widget_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportDashboard
        fields = [
            'id', 'name', 'description',
            'is_public', 'is_favorite', 'is_default',
            'view_count', 'widget_count',
            'created_at', 'updated_at'
        ]
    
    def get_widget_count(self, obj):
        return obj.dashboard_widgets.count()


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for DataSource"""
    
    class Meta:
        model = DataSource
        fields = [
            'id', 'name', 'display_name', 'description',
            'source_type', 'model_name', 'app_label',
            'fields', 'relationships', 'allowed_aggregations',
            'requires_permission', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportFolderSerializer(serializers.ModelSerializer):
    """Serializer for ReportFolder"""
    
    children = serializers.SerializerMethodField()
    report_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportFolder
        fields = [
            'id', 'name', 'parent', 'color', 'icon',
            'is_shared', 'shared_with',
            'children', 'report_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        return ReportFolderSerializer(obj.children.all(), many=True).data
    
    def get_report_count(self, obj):
        from .report_models import ReportTemplate
        return ReportTemplate.objects.filter(folder=obj.name).count()


class ReportSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for ReportSubscription"""
    
    scheduled_report_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportSubscription
        fields = [
            'id', 'scheduled_report', 'scheduled_report_name',
            'delivery_method', 'delivery_address',
            'include_summary', 'include_full_report',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_scheduled_report_name(self, obj):
        return obj.scheduled_report.name if obj.scheduled_report else None


# Request Serializers
class CreateReportSerializer(serializers.Serializer):
    """Request serializer for creating a report"""
    
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    report_type = serializers.ChoiceField(choices=[
        'table', 'chart', 'dashboard', 'pivot', 'summary', 'detail'
    ])
    data_source = serializers.CharField(max_length=100)
    columns = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )
    grouping = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[]
    )
    sorting = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )
    filters = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )
    dynamic_filters = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )
    chart_config = serializers.DictField(required=False, default=dict)
    calculated_fields = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[]
    )
    visibility = serializers.ChoiceField(
        choices=['private', 'team', 'organization', 'public'],
        default='private'
    )


class ExecuteReportSerializer(serializers.Serializer):
    """Request serializer for executing a report"""
    
    parameters = serializers.DictField(required=False, default=dict)
    limit = serializers.IntegerField(min_value=1, max_value=10000, default=1000)
    offset = serializers.IntegerField(min_value=0, default=0)


class ExportReportSerializer(serializers.Serializer):
    """Request serializer for exporting a report"""
    
    format = serializers.ChoiceField(choices=['csv', 'json', 'excel', 'pdf', 'html'])
    include_headers = serializers.BooleanField(default=True)
    include_summary = serializers.BooleanField(default=True)


class CreateWidgetSerializer(serializers.Serializer):
    """Request serializer for creating a widget"""
    
    name = serializers.CharField(max_length=255)
    widget_type = serializers.ChoiceField(choices=[
        'metric', 'chart_bar', 'chart_line', 'chart_pie', 'chart_donut',
        'chart_area', 'chart_scatter', 'table', 'list', 'funnel',
        'gauge', 'heatmap', 'map', 'text'
    ])
    data_source = serializers.CharField(max_length=100)
    query = serializers.DictField(required=False, default=dict)
    aggregation = serializers.CharField(required=False, allow_blank=True)
    config = serializers.DictField(required=False, default=dict)
    position_x = serializers.IntegerField(default=0)
    position_y = serializers.IntegerField(default=0)
    width = serializers.IntegerField(default=4, min_value=1, max_value=12)
    height = serializers.IntegerField(default=3, min_value=1, max_value=12)


class CreateDashboardSerializer(serializers.Serializer):
    """Request serializer for creating a dashboard"""
    
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    layout_type = serializers.ChoiceField(choices=['grid', 'free'], default='grid')
    grid_columns = serializers.IntegerField(default=12, min_value=1, max_value=24)
    theme = serializers.CharField(default='light')
    auto_refresh = serializers.BooleanField(default=False)
    refresh_interval = serializers.IntegerField(default=60, min_value=10)


class AddDashboardWidgetSerializer(serializers.Serializer):
    """Request serializer for adding widget to dashboard"""
    
    widget_id = serializers.UUIDField(required=False)
    widget_type = serializers.CharField(required=False, allow_blank=True)
    config = serializers.DictField(required=False, default=dict)
    position_x = serializers.IntegerField(default=0)
    position_y = serializers.IntegerField(default=0)
    width = serializers.IntegerField(default=4, min_value=1, max_value=12)
    height = serializers.IntegerField(default=3, min_value=1, max_value=12)
    title_override = serializers.CharField(required=False, allow_blank=True)


class UpdateLayoutSerializer(serializers.Serializer):
    """Request serializer for updating dashboard layout"""
    
    widgets = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )


class CreateScheduleSerializer(serializers.Serializer):
    """Request serializer for creating a schedule"""
    
    report_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    frequency = serializers.ChoiceField(choices=[
        'once', 'daily', 'weekly', 'biweekly', 'monthly', 'quarterly'
    ])
    schedule_time = serializers.TimeField()
    day_of_week = serializers.IntegerField(required=False, min_value=0, max_value=6)
    day_of_month = serializers.IntegerField(required=False, min_value=1, max_value=31)
    timezone = serializers.CharField(default='UTC')
    parameters = serializers.DictField(required=False, default=dict)
    export_format = serializers.ChoiceField(
        choices=['pdf', 'csv', 'excel', 'html'],
        default='pdf'
    )
    delivery_method = serializers.ChoiceField(
        choices=['email', 'slack', 'teams', 'webhook', 'sftp'],
        default='email'
    )
    delivery_config = serializers.DictField(required=False, default=dict)
    recipients = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[]
    )


class ShareDashboardSerializer(serializers.Serializer):
    """Request serializer for sharing a dashboard"""
    
    is_public = serializers.BooleanField(default=False)
    embed_enabled = serializers.BooleanField(default=False)
    users = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=[]
    )


class CloneReportSerializer(serializers.Serializer):
    """Request serializer for cloning a report"""
    
    new_name = serializers.CharField(max_length=255)
