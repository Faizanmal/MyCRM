"""
Enterprise Core Serializers for MyCRM
Advanced security and enterprise features API serialization
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AuditLog, SystemConfiguration, APIKey, DataBackup, 
    Workflow, WorkflowExecution, Integration, NotificationTemplate, SystemHealth,
    UserPermission, PermissionGroup, Team, TeamMember,
    DataImportLog, Notification, SavedSearch, Dashboard, Report, ScheduledReport,
    SearchLog, EmailLog, EmailClick, EmailCampaign
)

User = get_user_model()


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit log entries"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'resource', 
            'ip_address', 'user_agent', 'metadata', 'risk_level', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class SystemConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for system configuration"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = SystemConfiguration
        fields = [
            'key', 'value', 'config_type', 'description', 'is_encrypted',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API key management"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'user', 'user_name', 'permissions', 'rate_limit',
            'status', 'last_used', 'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'key_hash', 'last_used', 'created_at']


class DataBackupSerializer(serializers.ModelSerializer):
    """Serializer for data backup tracking"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = DataBackup
        fields = [
            'id', 'backup_type', 'file_path', 'file_size', 'status',
            'error_message', 'created_by', 'created_by_name', 'started_at',
            'completed_at', 'duration_minutes'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'duration_minutes']
    
    def get_duration_minutes(self, obj):
        if obj.completed_at and obj.started_at:
            duration = obj.completed_at - obj.started_at
            return round(duration.total_seconds() / 60, 2)
        return None


class WorkflowSerializer(serializers.ModelSerializer):
    """Serializer for workflow definitions"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    execution_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'trigger_type', 'trigger_conditions',
            'actions', 'status', 'created_by', 'created_by_name', 'created_at',
            'updated_at', 'execution_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'execution_count']
    
    def get_execution_count(self, obj):
        return obj.executions.count()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """Serializer for workflow execution tracking"""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'workflow_name', 'trigger_data', 'status',
            'steps_completed', 'total_steps', 'error_message', 'execution_log',
            'started_at', 'completed_at', 'duration_minutes', 'progress_percentage'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'duration_minutes', 'progress_percentage']
    
    def get_duration_minutes(self, obj):
        if obj.completed_at and obj.started_at:
            duration = obj.completed_at - obj.started_at
            return round(duration.total_seconds() / 60, 2)
        return None
    
    def get_progress_percentage(self, obj):
        if obj.total_steps > 0:
            return round((obj.steps_completed / obj.total_steps) * 100, 2)
        return 0


class IntegrationSerializer(serializers.ModelSerializer):
    """Serializer for external integrations"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    sync_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Integration
        fields = [
            'id', 'name', 'integration_type', 'provider', 'configuration',
            'status', 'last_sync', 'sync_frequency', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'sync_status'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'sync_status']
    
    def get_sync_status(self, obj):
        if not obj.last_sync:
            return 'never'
        
        from django.utils import timezone
        from datetime import timedelta
        
        time_since_sync = timezone.now() - obj.last_sync
        expected_interval = timedelta(minutes=obj.sync_frequency)
        
        if time_since_sync > expected_interval * 2:
            return 'overdue'
        elif time_since_sync > expected_interval:
            return 'due'
        else:
            return 'current'
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'subject_template', 'body_template',
            'variables', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SystemHealthSerializer(serializers.ModelSerializer):
    """Serializer for system health monitoring"""
    status_color = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemHealth
        fields = [
            'component', 'status', 'response_time', 'error_message',
            'metrics', 'checked_at', 'status_color'
        ]
        read_only_fields = ['checked_at', 'status_color']
    
    def get_status_color(self, obj):
        color_map = {
            'healthy': 'green',
            'warning': 'yellow',
            'critical': 'orange',
            'down': 'red'
        }
        return color_map.get(obj.status, 'gray')


class SecurityDashboardSerializer(serializers.Serializer):
    """Serializer for security dashboard data"""
    total_audit_logs = serializers.IntegerField()
    high_risk_events_today = serializers.IntegerField()
    failed_logins_today = serializers.IntegerField()
    active_api_keys = serializers.IntegerField()
    recent_backups = serializers.IntegerField()
    system_health_score = serializers.FloatField()
    active_integrations = serializers.IntegerField()
    workflow_executions_today = serializers.IntegerField()


class AdvancedAnalyticsSerializer(serializers.Serializer):
    """Serializer for advanced analytics data"""
    user_activity_trend = serializers.JSONField()
    security_incidents_trend = serializers.JSONField()
    system_performance_metrics = serializers.JSONField()
    integration_status_summary = serializers.JSONField()


# Additional Serializers for New Features

class UserPermissionSerializer(serializers.ModelSerializer):
    """Serializer for user permissions"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = UserPermission
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PermissionGroupSerializer(serializers.ModelSerializer):
    """Serializer for permission groups"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PermissionGroup
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        return obj.user_assignments.count()


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for teams"""
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.filter(is_active=True).count()


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for team members"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = TeamMember
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']


class DataImportLogSerializer(serializers.ModelSerializer):
    """Serializer for data import logs"""
    imported_by_name = serializers.CharField(source='imported_by.username', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = DataImportLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'completed_at']
    
    def get_success_rate(self, obj):
        if obj.total_records > 0:
            return (obj.imported_records / obj.total_records) * 100
        return 0


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'read_at']


class SavedSearchSerializer(serializers.ModelSerializer):
    """Serializer for saved searches"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SavedSearch
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for dashboards"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Dashboard
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for reports"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScheduledReportSerializer(serializers.ModelSerializer):
    """Serializer for scheduled reports"""
    report_name = serializers.CharField(source='report.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ScheduledReport
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'last_run']


class SearchLogSerializer(serializers.ModelSerializer):
    """Serializer for search logs"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SearchLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for email logs"""
    sent_by_name = serializers.CharField(source='sent_by.username', read_only=True)
    open_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailLog
        fields = '__all__'
        read_only_fields = ['id', 'sent_at', 'opened_at']
    
    def get_open_rate(self, obj):
        return 100 if obj.open_count > 0 else 0


class EmailClickSerializer(serializers.ModelSerializer):
    """Serializer for email clicks"""
    email_subject = serializers.CharField(source='email_log.subject', read_only=True)
    
    class Meta:
        model = EmailClick
        fields = '__all__'
        read_only_fields = ['id', 'clicked_at']


class EmailCampaignSerializer(serializers.ModelSerializer):
    """Serializer for email campaigns"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    open_rate = serializers.SerializerMethodField()
    click_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailCampaign
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'started_at', 'completed_at']
    
    def get_open_rate(self, obj):
        if obj.sent_count > 0:
            return (obj.opened_count / obj.sent_count) * 100
        return 0
    
    def get_click_rate(self, obj):
        if obj.sent_count > 0:
            return (obj.clicked_count / obj.sent_count) * 100
        return 0
    workflow_performance = serializers.JSONField()
    data_quality_score = serializers.FloatField()
    compliance_score = serializers.FloatField()