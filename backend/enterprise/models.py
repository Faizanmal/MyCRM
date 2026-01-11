"""
Zero-Trust Security Models
Enterprise-grade security with device fingerprinting, continuous auth, and audit logs.
"""

import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class DeviceFingerprint(models.Model):
    """Device fingerprinting for trust verification"""
    
    DEVICE_TYPE = [
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('unknown', 'Unknown'),
    ]
    
    TRUST_LEVEL = [
        ('trusted', 'Trusted'),
        ('verified', 'Verified'),
        ('unknown', 'Unknown'),
        ('suspicious', 'Suspicious'),
        ('blocked', 'Blocked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='device_fingerprints'
    )
    
    # Device identification
    fingerprint_hash = models.CharField(max_length=64, unique=True)
    device_name = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE, default='unknown')
    
    # Browser info
    user_agent = models.TextField(blank=True)
    browser_name = models.CharField(max_length=100, blank=True)
    browser_version = models.CharField(max_length=50, blank=True)
    
    # OS info
    os_name = models.CharField(max_length=100, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    
    # Screen/Hardware
    screen_resolution = models.CharField(max_length=50, blank=True)
    timezone = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=50, blank=True)
    
    # Canvas/WebGL fingerprint components
    canvas_hash = models.CharField(max_length=64, blank=True)
    webgl_hash = models.CharField(max_length=64, blank=True)
    audio_hash = models.CharField(max_length=64, blank=True)
    font_hash = models.CharField(max_length=64, blank=True)
    
    # Trust status
    trust_level = models.CharField(max_length=20, choices=TRUST_LEVEL, default='unknown')
    trust_score = models.IntegerField(default=50)  # 0-100
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_method = models.CharField(max_length=50, blank=True)
    
    # Geolocation
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    last_country = models.CharField(max_length=100, blank=True)
    last_city = models.CharField(max_length=100, blank=True)
    
    # Activity
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    login_count = models.IntegerField(default=0)
    
    # Notes
    admin_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'security_device_fingerprints'
        verbose_name = 'Device Fingerprint'
        verbose_name_plural = 'Device Fingerprints'
        ordering = ['-last_seen']

    def __str__(self):
        return f"{self.user.username} - {self.device_name or 'Unknown Device'}"


class SecuritySession(models.Model):
    """Enhanced session tracking for zero-trust"""
    
    STATUS = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('suspicious', 'Suspicious'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='security_sessions'
    )
    device = models.ForeignKey(
        DeviceFingerprint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions'
    )
    
    # Session info
    session_key = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS, default='active')
    
    # Authentication
    auth_method = models.CharField(max_length=50)  # password, sso, mfa, etc.
    mfa_verified = models.BooleanField(default=False)
    mfa_method = models.CharField(max_length=50, blank=True)
    
    # Location
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Risk assessment
    risk_score = models.IntegerField(default=0)  # 0-100
    risk_factors = models.JSONField(default=list, blank=True)
    
    # Continuous auth
    last_activity = models.DateTimeField(auto_now=True)
    last_verification = models.DateTimeField(null=True, blank=True)
    verification_interval = models.IntegerField(default=3600)  # seconds
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    terminated_at = models.DateTimeField(null=True, blank=True)
    termination_reason = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'security_sessions'
        verbose_name = 'Security Session'
        verbose_name_plural = 'Security Sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class SecurityAuditLog(models.Model):
    """Comprehensive audit logging for compliance"""
    
    SEVERITY = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    CATEGORY = [
        ('authentication', 'Authentication'),
        ('authorization', 'Authorization'),
        ('data_access', 'Data Access'),
        ('data_modification', 'Data Modification'),
        ('data_export', 'Data Export'),
        ('admin_action', 'Admin Action'),
        ('security_event', 'Security Event'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    session = models.ForeignKey(
        SecuritySession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    tenant = models.ForeignKey(
        'multi_tenant.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # What
    action = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY)
    severity = models.CharField(max_length=20, choices=SEVERITY, default='info')
    description = models.TextField()
    
    # Target
    resource_type = models.CharField(max_length=100, blank=True)
    resource_id = models.CharField(max_length=100, blank=True)
    resource_name = models.CharField(max_length=255, blank=True)
    
    # Details
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Where
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Result
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'security_audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['category', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"


class AccessPolicy(models.Model):
    """Configurable access policies for zero-trust"""
    
    ENFORCEMENT_MODE = [
        ('disabled', 'Disabled'),
        ('monitor', 'Monitor Only'),
        ('enforce', 'Enforce'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Scope
    tenant = models.ForeignKey(
        'multi_tenant.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='access_policies'
    )
    applies_to_all = models.BooleanField(default=False)
    user_groups = models.JSONField(default=list, blank=True)
    
    # Rules
    rules = models.JSONField(default=list)  # [{condition, action}]
    
    # Enforcement
    enforcement_mode = models.CharField(max_length=20, choices=ENFORCEMENT_MODE, default='monitor')
    
    # Priority
    priority = models.IntegerField(default=100)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'security_access_policies'
        verbose_name = 'Access Policy'
        verbose_name_plural = 'Access Policies'
        ordering = ['priority']

    def __str__(self):
        return self.name


class ThreatIndicator(models.Model):
    """Threat intelligence indicators"""
    
    INDICATOR_TYPE = [
        ('ip', 'IP Address'),
        ('email', 'Email'),
        ('domain', 'Domain'),
        ('user_agent', 'User Agent'),
        ('fingerprint', 'Device Fingerprint'),
    ]
    
    THREAT_LEVEL = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    indicator_type = models.CharField(max_length=20, choices=INDICATOR_TYPE)
    value = models.CharField(max_length=255)
    threat_level = models.CharField(max_length=20, choices=THREAT_LEVEL)
    
    # Details
    description = models.TextField(blank=True)
    source = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Validity
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    hit_count = models.IntegerField(default=0)
    last_hit = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'security_threat_indicators'
        verbose_name = 'Threat Indicator'
        verbose_name_plural = 'Threat Indicators'
        unique_together = ['indicator_type', 'value']

    def __str__(self):
        return f"{self.indicator_type}: {self.value}"


class SecurityIncident(models.Model):
    """Security incident tracking"""
    
    STATUS = [
        ('new', 'New'),
        ('investigating', 'Investigating'),
        ('contained', 'Contained'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]
    
    SEVERITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    INCIDENT_TYPE = [
        ('brute_force', 'Brute Force'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('data_exfiltration', 'Data Exfiltration'),
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('insider_threat', 'Insider Threat'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    title = models.CharField(max_length=255)
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPE)
    severity = models.CharField(max_length=20, choices=SEVERITY)
    status = models.CharField(max_length=20, choices=STATUS, default='new')
    
    # Details
    description = models.TextField()
    affected_users = models.ManyToManyField(User, blank=True, related_name='security_incidents')
    affected_resources = models.JSONField(default=list, blank=True)
    
    # Evidence
    related_logs = models.ManyToManyField(SecurityAuditLog, blank=True)
    indicators = models.ManyToManyField(ThreatIndicator, blank=True)
    evidence = models.JSONField(default=list, blank=True)
    
    # Response
    containment_actions = models.TextField(blank=True)
    remediation_steps = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents'
    )
    
    # Timeline
    detected_at = models.DateTimeField(auto_now_add=True)
    contained_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_incidents'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'security_incidents'
        verbose_name = 'Security Incident'
        verbose_name_plural = 'Security Incidents'
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.title} - {self.severity}"


class DataClassification(models.Model):
    """Data classification levels for DLP"""
    
    SENSITIVITY = [
        ('public', 'Public'),
        ('internal', 'Internal'),
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted'),
        ('secret', 'Secret'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    sensitivity_level = models.CharField(max_length=20, choices=SENSITIVITY)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6B7280')
    
    # Rules
    patterns = models.JSONField(default=list)  # Regex patterns to detect
    keywords = models.JSONField(default=list)  # Keywords to detect
    
    # Handling requirements
    encryption_required = models.BooleanField(default=False)
    access_logging_required = models.BooleanField(default=True)
    export_allowed = models.BooleanField(default=True)
    sharing_allowed = models.BooleanField(default=True)
    retention_days = models.IntegerField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'security_data_classifications'
        verbose_name = 'Data Classification'
        verbose_name_plural = 'Data Classifications'
        ordering = ['sensitivity_level']

    def __str__(self):
        return f"{self.name} ({self.get_sensitivity_level_display()})"
