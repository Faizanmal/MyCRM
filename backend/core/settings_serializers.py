"""
Settings Serializers
Serializers for user preferences, notification settings, export jobs, and RBAC
"""

from rest_framework import serializers
from .settings_models import (
    UserPreference,
    NotificationPreference,
    NotificationTypeSetting,
    ExportJob,
    UserRole,
    UserRoleAssignment,
)


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user preferences"""
    
    class Meta:
        model = UserPreference
        fields = [
            'id',
            # Appearance
            'theme',
            'accent_color',
            'font_size',
            'compact_mode',
            'animations_enabled',
            'high_contrast',
            # Dashboard
            'default_view',
            'sidebar_collapsed',
            'show_welcome_message',
            'auto_refresh_enabled',
            'auto_refresh_interval',
            'dashboard_layout',
            # Privacy
            'share_activity_with_team',
            'show_online_status',
            'allow_mentions',
            'data_export_enabled',
            # Sound
            'sound_enabled',
            'sound_volume',
            # Shortcuts
            'keyboard_shortcuts',
            # Timestamps
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationTypeSettingSerializer(serializers.ModelSerializer):
    """Serializer for notification type settings"""
    
    class Meta:
        model = NotificationTypeSetting
        fields = [
            'id',
            'notification_type',
            'email_enabled',
            'push_enabled',
            'in_app_enabled',
            'sms_enabled',
            'frequency',
            'priority',
        ]
        read_only_fields = ['id']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    type_settings = NotificationTypeSettingSerializer(many=True, read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id',
            # Channels
            'email_enabled',
            'push_enabled',
            'in_app_enabled',
            'sms_enabled',
            # Quiet Hours
            'quiet_hours_enabled',
            'quiet_hours_start',
            'quiet_hours_end',
            'quiet_hours_days',
            # Digest
            'digest_enabled',
            'digest_frequency',
            'digest_time',
            'digest_include_ai',
            'digest_include_metrics',
            # Type Settings
            'type_settings',
            # Timestamps
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'type_settings']


class NotificationPreferenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification preferences with type settings"""
    type_settings = NotificationTypeSettingSerializer(many=True, required=False)
    
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled',
            'push_enabled',
            'in_app_enabled',
            'sms_enabled',
            'quiet_hours_enabled',
            'quiet_hours_start',
            'quiet_hours_end',
            'quiet_hours_days',
            'digest_enabled',
            'digest_frequency',
            'digest_time',
            'digest_include_ai',
            'digest_include_metrics',
            'type_settings',
        ]
    
    def update(self, instance, validated_data):
        type_settings_data = validated_data.pop('type_settings', None)
        
        # Update main preferences
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update type settings if provided
        if type_settings_data:
            for setting_data in type_settings_data:
                notification_type = setting_data.get('notification_type')
                NotificationTypeSetting.objects.update_or_create(
                    notification_preference=instance,
                    notification_type=notification_type,
                    defaults=setting_data
                )
        
        return instance


class ExportJobSerializer(serializers.ModelSerializer):
    """Serializer for export jobs"""
    download_url = serializers.SerializerMethodField()
    file_size_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ExportJob
        fields = [
            'id',
            'format',
            'entities',
            'date_range',
            'include_archived',
            'include_deleted',
            'status',
            'progress',
            'file_path',
            'file_size',
            'file_size_formatted',
            'download_url',
            'error_message',
            'created_at',
            'started_at',
            'completed_at',
            'expires_at',
        ]
        read_only_fields = [
            'id', 'status', 'progress', 'file_path', 'file_size',
            'error_message', 'created_at', 'started_at', 'completed_at', 'expires_at',
        ]
    
    def get_download_url(self, obj):
        if obj.status == 'completed' and obj.file_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/api/v1/export/{obj.id}/download/')
        return None
    
    def get_file_size_formatted(self, obj):
        if obj.file_size:
            if obj.file_size >= 1024 * 1024:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
            elif obj.file_size >= 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size} B"
        return None


class ExportJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating export jobs"""
    
    class Meta:
        model = ExportJob
        fields = [
            'format',
            'entities',
            'date_range',
            'include_archived',
            'include_deleted',
        ]
    
    def validate_entities(self, value):
        valid_entities = ['contacts', 'companies', 'deals', 'tasks', 'activities', 'emails', 'calendar']
        for entity in value:
            if entity not in valid_entities:
                raise serializers.ValidationError(f"Invalid entity type: {entity}")
        if not value:
            raise serializers.ValidationError("At least one entity type must be selected")
        return value


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for user roles"""
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRole
        fields = [
            'id',
            'name',
            'display_name',
            'description',
            'level',
            'permissions',
            'permissions_count',
            'color',
            'is_system_role',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_permissions_count(self, obj):
        return len(obj.permissions) if obj.permissions else 0


class UserRoleAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for user role assignments"""
    role = UserRoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=UserRole.objects.all(),
        source='role',
        write_only=True
    )
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    assigned_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRoleAssignment
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'role',
            'role_id',
            'team_id',
            'organization_id',
            'assigned_by',
            'assigned_by_name',
            'assigned_at',
        ]
        read_only_fields = ['id', 'assigned_by', 'assigned_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    def get_assigned_by_name(self, obj):
        if obj.assigned_by:
            return obj.assigned_by.get_full_name() or obj.assigned_by.username
        return None


class UserPermissionsSerializer(serializers.Serializer):
    """Serializer for returning user's effective permissions"""
    user_id = serializers.IntegerField()
    email = serializers.EmailField()
    name = serializers.CharField()
    roles = UserRoleSerializer(many=True)
    permissions = serializers.ListField(child=serializers.CharField())
    is_admin = serializers.BooleanField()
    highest_role_level = serializers.IntegerField()


# ==================== Analytics Serializers ====================

class AnalyticsOverviewSerializer(serializers.Serializer):
    """Serializer for analytics overview metrics"""
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    revenue_growth = serializers.FloatField()
    total_deals = serializers.IntegerField()
    deals_growth = serializers.FloatField()
    conversion_rate = serializers.FloatField()
    conversion_growth = serializers.FloatField()
    active_leads = serializers.IntegerField()
    leads_growth = serializers.FloatField()


class RevenueByMonthSerializer(serializers.Serializer):
    """Serializer for monthly revenue data"""
    month = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    deals_count = serializers.IntegerField()


class DealsByStageSerializer(serializers.Serializer):
    """Serializer for deals by stage"""
    stage = serializers.CharField()
    count = serializers.IntegerField()
    value = serializers.DecimalField(max_digits=15, decimal_places=2)


class TeamMemberPerformanceSerializer(serializers.Serializer):
    """Serializer for team member performance"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    avatar = serializers.URLField(allow_null=True)
    deals_count = serializers.IntegerField()
    deals_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    activities_count = serializers.IntegerField()
    conversion_rate = serializers.FloatField()
    trend = serializers.FloatField()


class FunnelStageSerializer(serializers.Serializer):
    """Serializer for funnel stages"""
    stage = serializers.CharField()
    count = serializers.IntegerField()
    conversion_rate = serializers.FloatField()


class LeadSourceSerializer(serializers.Serializer):
    """Serializer for lead sources"""
    source = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class AnalyticsDashboardSerializer(serializers.Serializer):
    """Serializer for complete analytics dashboard"""
    overview = AnalyticsOverviewSerializer()
    revenue_by_month = RevenueByMonthSerializer(many=True)
    deals_by_stage = DealsByStageSerializer(many=True)
    team_performance = TeamMemberPerformanceSerializer(many=True)
    funnel = FunnelStageSerializer(many=True)
    lead_sources = LeadSourceSerializer(many=True)
