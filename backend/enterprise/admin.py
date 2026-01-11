from django.contrib import admin
from .models import (
    DeviceFingerprint, SecuritySession, SecurityAuditLog,
    AccessPolicy, ThreatIndicator, SecurityIncident, DataClassification
)


@admin.register(DeviceFingerprint)
class DeviceFingerprintAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_name', 'device_type', 'trust_level', 'last_seen']
    list_filter = ['trust_level', 'device_type', 'is_verified']
    search_fields = ['user__username', 'device_name', 'fingerprint_hash']


@admin.register(SecuritySession)
class SecuritySessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'auth_method', 'ip_address', 'created_at']
    list_filter = ['status', 'auth_method', 'mfa_verified']
    search_fields = ['user__username', 'ip_address']


@admin.register(SecurityAuditLog)
class SecurityAuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'category', 'severity', 'success', 'timestamp']
    list_filter = ['category', 'severity', 'success']
    search_fields = ['action', 'description', 'user__username']
    date_hierarchy = 'timestamp'


@admin.register(AccessPolicy)
class AccessPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'enforcement_mode', 'priority', 'is_active']
    list_filter = ['enforcement_mode', 'is_active']


@admin.register(ThreatIndicator)
class ThreatIndicatorAdmin(admin.ModelAdmin):
    list_display = ['indicator_type', 'value', 'threat_level', 'is_active', 'hit_count']
    list_filter = ['indicator_type', 'threat_level', 'is_active']
    search_fields = ['value', 'description']


@admin.register(SecurityIncident)
class SecurityIncidentAdmin(admin.ModelAdmin):
    list_display = ['title', 'incident_type', 'severity', 'status', 'detected_at']
    list_filter = ['incident_type', 'severity', 'status']
    search_fields = ['title', 'description']


@admin.register(DataClassification)
class DataClassificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'sensitivity_level', 'is_active']
    list_filter = ['sensitivity_level', 'is_active']
