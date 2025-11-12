from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Dashboard, Report, ReportSchedule, Analytics, KPIMetric, DataExport

User = get_user_model()


class DashboardSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'user', 'user_name', 'is_default',
            'layout', 'widgets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'description', 'report_type', 'format', 'filters',
            'fields', 'group_by', 'order_by', 'chart_config', 'is_public',
            'shared_with', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ReportScheduleSerializer(serializers.ModelSerializer):
    report_name = serializers.CharField(source='report.name', read_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'report', 'report_name', 'frequency', 'day_of_week',
            'day_of_month', 'time', 'recipients', 'is_active', 'last_run',
            'next_run', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_run', 'created_at', 'updated_at']


class AnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytics
        fields = [
            'id', 'name', 'description', 'metric_type', 'model_name',
            'field_name', 'filters', 'calculation', 'period_start',
            'period_end', 'value', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class KPIMetricSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    achievement_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = KPIMetric
        fields = [
            'id', 'name', 'description', 'target_value', 'current_value',
            'unit', 'calculation_method', 'data_source', 'display_order',
            'is_active', 'achievement_percentage', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class DataExportSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    
    class Meta:
        model = DataExport
        fields = [
            'id', 'name', 'export_type', 'format', 'filters', 'fields',
            'status', 'file_path', 'file_size', 'record_count', 'error_message',
            'requested_by', 'requested_by_name', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'requested_by', 'created_at', 'completed_at']
