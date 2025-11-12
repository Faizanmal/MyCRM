from rest_framework import serializers
from .models import Dashboard, DashboardWidget, Report, ReportSchedule, ReportExecution, KPI, KPIValue


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for dashboard widgets"""
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'dashboard', 'name', 'widget_type', 'data_source', 'position_x', 'position_y',
            'width', 'height', 'query_config', 'display_config', 'refresh_interval',
            'is_active', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for dashboards with nested widgets"""
    widgets = DashboardWidgetSerializer(many=True, read_only=True)
    shared_with_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'dashboard_type', 'owner', 'is_default', 'is_public',
            'shared_with', 'shared_with_details', 'layout',
            'widgets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_shared_with_details(self, obj):
        """Get details of users dashboard is shared with"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return [
            {'id': user.id, 'username': user.username, 'email': user.email}
            for user in obj.shared_with.all()
        ]


class ReportExecutionSerializer(serializers.ModelSerializer):
    """Serializer for report execution history"""
    
    class Meta:
        model = ReportExecution
        fields = [
            'id', 'report', 'schedule', 'executed_by', 'status', 'started_at', 'completed_at',
            'filters_used', 'rows_returned', 'file_path', 'file_size_bytes', 'error_message'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializer for report schedules"""
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'report', 'name', 'frequency', 'delivery_method', 'schedule_time',
            'day_of_week', 'day_of_month', 'recipients', 'delivery_config',
            'is_active', 'last_sent_at', 'next_run_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_sent_at', 'next_run_at', 'created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for reports with schedules and executions"""
    schedules = ReportScheduleSerializer(many=True, read_only=True)
    recent_executions = serializers.SerializerMethodField()
    shared_with_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'description', 'report_type', 'owner', 'data_sources',
            'filters', 'columns', 'grouping', 'sorting', 'calculations', 'export_format',
            'include_charts', 'include_summary', 'is_public', 'shared_with', 'shared_with_details',
            'schedules', 'recent_executions', 'last_generated_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_generated_at']
    
    def get_recent_executions(self, obj):
        """Get 5 most recent executions"""
        executions = obj.executions.order_by('-started_at')[:5]
        return ReportExecutionSerializer(executions, many=True).data
    
    def get_shared_with_details(self, obj):
        """Get details of users report is shared with"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return [
            {'id': user.id, 'username': user.username, 'email': user.email}
            for user in obj.shared_with.all()
        ]


class KPIValueSerializer(serializers.ModelSerializer):
    """Serializer for KPI values (time series data)"""
    
    class Meta:
        model = KPIValue
        fields = ['id', 'kpi', 'value', 'period_start', 'period_end', 'previous_value', 'change_percentage', 'metadata', 'calculated_at']
        read_only_fields = ['id', 'calculated_at']


class KPISerializer(serializers.ModelSerializer):
    """Serializer for KPIs with recent values"""
    recent_values = serializers.SerializerMethodField()
    current_value = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()
    
    class Meta:
        model = KPI
        fields = [
            'id', 'name', 'description', 'kpi_type', 'calculation_formula',
            'data_source', 'unit', 'target_value', 'display_format',
            'color_good', 'color_warning', 'color_bad', 'is_active', 'owner',
            'current_value', 'trend', 'recent_values', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_recent_values(self, obj):
        """Get recent KPI values for charting"""
        values = obj.values.order_by('-period_end')[:30]
        return KPIValueSerializer(values, many=True).data
    
    def get_current_value(self, obj):
        """Get most recent KPI value"""
        latest = obj.values.order_by('-period_end').first()
        return float(latest.value) if latest else None
    
    def get_trend(self, obj):
        """Calculate trend (up/down/stable)"""
        values = list(obj.values.order_by('-period_end')[:7].values_list('value', flat=True))
        if len(values) < 2:
            return 'stable'
        
        # Simple trend: compare average of first half vs second half
        mid = len(values) // 2
        recent_avg = sum(values[:mid]) / mid if mid > 0 else 0
        older_avg = sum(values[mid:]) / (len(values) - mid) if len(values) > mid else 0
        
        if recent_avg > older_avg * 1.05:
            return 'up'
        elif recent_avg < older_avg * 0.95:
            return 'down'
        return 'stable'


class DashboardWidgetDataSerializer(serializers.Serializer):
    """Serializer for widget data API response"""
    widget_id = serializers.IntegerField()
    widget_type = serializers.CharField()
    title = serializers.CharField()
    data = serializers.JSONField()
    updated_at = serializers.DateTimeField()
