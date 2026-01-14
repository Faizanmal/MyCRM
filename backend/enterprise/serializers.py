"""
Zero-Trust Security Serializers
"""

from rest_framework import serializers

from .models import (
    AccessPolicy,
    DataClassification,
    DeviceFingerprint,
    SecurityAuditLog,
    SecurityIncident,
    SecuritySession,
    ThreatIndicator,
)


class DeviceFingerprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceFingerprint
        fields = [
            'id', 'device_name', 'device_type', 'browser_name', 'browser_version',
            'os_name', 'os_version', 'trust_level', 'trust_score',
            'is_verified', 'verified_at', 'last_ip', 'last_country', 'last_city',
            'first_seen', 'last_seen', 'login_count'
        ]
        read_only_fields = ['id', 'trust_score', 'first_seen', 'last_seen', 'login_count']


class RegisterDeviceSerializer(serializers.Serializer):
    fingerprint_hash = serializers.CharField(max_length=64)
    device_name = serializers.CharField(max_length=255, required=False)
    user_agent = serializers.CharField(required=False)
    screen_resolution = serializers.CharField(max_length=50, required=False)
    timezone = serializers.CharField(max_length=100, required=False)
    language = serializers.CharField(max_length=50, required=False)
    canvas_hash = serializers.CharField(max_length=64, required=False)
    webgl_hash = serializers.CharField(max_length=64, required=False)


class SecuritySessionSerializer(serializers.ModelSerializer):
    device = DeviceFingerprintSerializer(read_only=True)

    class Meta:
        model = SecuritySession
        fields = [
            'id', 'device', 'status', 'auth_method', 'mfa_verified',
            'ip_address', 'country', 'city', 'risk_score', 'risk_factors',
            'last_activity', 'created_at', 'expires_at'
        ]


class SecurityAuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = SecurityAuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'category', 'severity',
            'description', 'resource_type', 'resource_id', 'resource_name',
            'ip_address', 'success', 'error_message', 'timestamp'
        ]

    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None


class SecurityAuditLogDetailSerializer(SecurityAuditLogSerializer):
    class Meta(SecurityAuditLogSerializer.Meta):
        fields = SecurityAuditLogSerializer.Meta.fields + [
            'old_values', 'new_values', 'metadata', 'user_agent'
        ]


class AccessPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPolicy
        fields = [
            'id', 'name', 'description', 'applies_to_all', 'user_groups',
            'rules', 'enforcement_mode', 'priority', 'is_active',
            'created_at', 'updated_at'
        ]


class ThreatIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatIndicator
        fields = [
            'id', 'indicator_type', 'value', 'threat_level', 'description',
            'source', 'tags', 'is_active', 'expires_at', 'hit_count',
            'last_hit', 'created_at'
        ]


class SecurityIncidentSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    affected_user_count = serializers.SerializerMethodField()

    class Meta:
        model = SecurityIncident
        fields = [
            'id', 'title', 'incident_type', 'severity', 'status',
            'description', 'affected_resources', 'assigned_to',
            'assigned_to_name', 'affected_user_count',
            'detected_at', 'contained_at', 'resolved_at', 'updated_at'
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None

    def get_affected_user_count(self, obj):
        return obj.affected_users.count()


class SecurityIncidentDetailSerializer(SecurityIncidentSerializer):
    affected_users = serializers.SerializerMethodField()

    class Meta(SecurityIncidentSerializer.Meta):
        fields = SecurityIncidentSerializer.Meta.fields + [
            'affected_users', 'evidence', 'containment_actions',
            'remediation_steps', 'lessons_learned', 'created_by'
        ]

    def get_affected_users(self, obj):
        return [
            {'id': str(u.id), 'name': f"{u.first_name} {u.last_name}", 'email': u.email}
            for u in obj.affected_users.all()
        ]


class DataClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataClassification
        fields = [
            'id', 'name', 'sensitivity_level', 'description', 'color',
            'patterns', 'keywords', 'encryption_required',
            'access_logging_required', 'export_allowed', 'sharing_allowed',
            'retention_days', 'is_active'
        ]


class SecurityDashboardSerializer(serializers.Serializer):
    active_sessions = serializers.IntegerField()
    suspicious_sessions = serializers.IntegerField()
    trusted_devices = serializers.IntegerField()
    blocked_devices = serializers.IntegerField()
    open_incidents = serializers.IntegerField()
    critical_incidents = serializers.IntegerField()
    recent_threats = ThreatIndicatorSerializer(many=True)
    login_attempts_today = serializers.IntegerField()
    failed_logins_today = serializers.IntegerField()


class RiskAssessmentSerializer(serializers.Serializer):
    overall_risk = serializers.CharField()
    risk_score = serializers.IntegerField()
    factors = serializers.ListField()
    recommendations = serializers.ListField()
