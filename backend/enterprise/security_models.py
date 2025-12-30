"""
Advanced Security Models
Zero-trust, DLP, and Audit Trail Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class DeviceTrust(models.Model):
    """Trusted devices for zero-trust architecture"""
    
    DEVICE_TYPES = [
        ('desktop', 'Desktop'),
        ('laptop', 'Laptop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('unknown', 'Unknown'),
    ]
    
    TRUST_LEVELS = [
        ('untrusted', 'Untrusted'),
        ('basic', 'Basic Trust'),
        ('verified', 'Verified'),
        ('corporate', 'Corporate Managed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trusted_devices')
    
    # Device identification
    device_fingerprint = models.CharField(max_length=256, db_index=True)
    device_name = models.CharField(max_length=200, blank=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='unknown')
    
    # Device details
    user_agent = models.TextField(blank=True)
    os_name = models.CharField(max_length=100, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    browser_name = models.CharField(max_length=100, blank=True)
    browser_version = models.CharField(max_length=50, blank=True)
    
    # Trust status
    trust_level = models.CharField(max_length=20, choices=TRUST_LEVELS, default='untrusted')
    is_trusted = models.BooleanField(default=False)
    trust_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Verification
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_via = models.CharField(max_length=50, blank=True)  # 'email', 'sms', 'mfa'
    
    # Location
    last_ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_location = models.JSONField(default=dict)
    
    # Activity
    last_activity_at = models.DateTimeField(auto_now=True)
    login_count = models.IntegerField(default=0)
    
    # Revocation
    is_revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'device_trust'
        unique_together = ['user', 'device_fingerprint']
        ordering = ['-last_activity_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name or self.device_type}"


class SecuritySession(models.Model):
    """Enhanced session tracking for continuous authentication"""
    
    SESSION_STATUS = [
        ('active', 'Active'),
        ('idle', 'Idle'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('suspicious', 'Suspicious'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_sessions')
    device = models.ForeignKey(DeviceTrust, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Session info
    session_key = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active')
    
    # Authentication
    auth_method = models.CharField(max_length=50, default='password')  # 'password', 'mfa', 'sso', 'passkey'
    mfa_verified = models.BooleanField(default=False)
    auth_strength = models.IntegerField(default=1)  # 1-5 scale
    
    # Location
    ip_address = models.GenericIPAddressField()
    geo_country = models.CharField(max_length=100, blank=True)
    geo_city = models.CharField(max_length=100, blank=True)
    
    # Risk assessment
    risk_score = models.IntegerField(default=0)  # 0-100
    risk_factors = models.JSONField(default=list)
    
    # Activity tracking
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    # Actions performed
    actions_count = models.IntegerField(default=0)
    sensitive_actions_count = models.IntegerField(default=0)
    
    # Termination
    terminated_at = models.DateTimeField(null=True, blank=True)
    termination_reason = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'security_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Session for {self.user.username} from {self.ip_address}"


class ImmutableAuditLog(models.Model):
    """Immutable audit log with cryptographic verification"""
    
    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    ACTION_CATEGORIES = [
        ('authentication', 'Authentication'),
        ('authorization', 'Authorization'),
        ('data_access', 'Data Access'),
        ('data_modification', 'Data Modification'),
        ('data_deletion', 'Data Deletion'),
        ('export', 'Data Export'),
        ('configuration', 'Configuration Change'),
        ('security', 'Security Event'),
        ('compliance', 'Compliance Event'),
        ('admin', 'Administrative Action'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Actor
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    user_email = models.EmailField()  # Preserved even if user deleted
    user_role = models.CharField(max_length=100)
    
    # Session context
    session = models.ForeignKey(SecuritySession, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_fingerprint = models.CharField(max_length=256, blank=True)
    
    # Action
    action = models.CharField(max_length=100, db_index=True)
    action_category = models.CharField(max_length=50, choices=ACTION_CATEGORIES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='info')
    
    # Resource
    resource_type = models.CharField(max_length=100, db_index=True)
    resource_id = models.CharField(max_length=100, db_index=True)
    resource_name = models.CharField(max_length=500, blank=True)
    
    # Changes
    old_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)
    
    # Additional context
    metadata = models.JSONField(default=dict)
    
    # Cryptographic chain
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    previous_hash = models.CharField(max_length=64, blank=True)
    log_hash = models.CharField(max_length=64)
    
    # Compliance tags
    compliance_frameworks = models.JSONField(default=list)  # ['soc2', 'gdpr', 'hipaa']
    retention_days = models.IntegerField(default=2555)  # 7 years default
    
    class Meta:
        db_table = 'immutable_audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def __str__(self):
        return f"{self.timestamp}: {self.user_email} - {self.action}"
    
    def save(self, *args, **kwargs):
        # Generate hash before saving
        if not self.log_hash:
            self.log_hash = self._generate_hash()
        super().save(*args, **kwargs)
    
    def _generate_hash(self) -> str:
        import hashlib
        import json
        
        data = {
            'user_email': self.user_email,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'timestamp': self.timestamp.isoformat(),
            'previous_hash': self.previous_hash,
            'old_values': self.old_values,
            'new_values': self.new_values,
        }
        
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


class DataClassification(models.Model):
    """Data classification levels for DLP"""
    
    CLASSIFICATION_LEVELS = [
        ('public', 'Public'),
        ('internal', 'Internal'),
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted'),
        ('top_secret', 'Top Secret'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100, unique=True)
    level = models.CharField(max_length=20, choices=CLASSIFICATION_LEVELS)
    description = models.TextField(blank=True)
    
    # Protection requirements
    requires_encryption = models.BooleanField(default=False)
    requires_mfa = models.BooleanField(default=False)
    can_export = models.BooleanField(default=True)
    can_share_external = models.BooleanField(default=True)
    
    # Retention
    retention_days = models.IntegerField(null=True, blank=True)
    auto_delete = models.BooleanField(default=False)
    
    # Patterns for auto-classification
    patterns = models.JSONField(default=list, help_text="Regex patterns for detection")
    keywords = models.JSONField(default=list, help_text="Keywords for detection")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_classifications'
        ordering = ['level', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.level})"


class DLPPolicy(models.Model):
    """Data Loss Prevention policies"""
    
    POLICY_ACTIONS = [
        ('allow', 'Allow'),
        ('warn', 'Warn'),
        ('block', 'Block'),
        ('quarantine', 'Quarantine'),
        ('encrypt', 'Encrypt'),
        ('redact', 'Redact'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Scope
    classifications = models.ManyToManyField(DataClassification, related_name='policies')
    applies_to_roles = models.JSONField(default=list)
    
    # Triggers
    on_download = models.BooleanField(default=True)
    on_export = models.BooleanField(default=True)
    on_share = models.BooleanField(default=True)
    on_email = models.BooleanField(default=True)
    on_print = models.BooleanField(default=False)
    on_copy = models.BooleanField(default=False)
    
    # Action
    action = models.CharField(max_length=20, choices=POLICY_ACTIONS, default='warn')
    notification_template = models.TextField(blank=True)
    
    # Exceptions
    exempt_roles = models.JSONField(default=list)
    exempt_users = models.ManyToManyField(User, blank=True, related_name='dlp_exemptions')
    
    # Settings
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dlp_policies'
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return self.name


class DLPIncident(models.Model):
    """DLP incident records"""
    
    INCIDENT_STATUS = [
        ('new', 'New'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
        ('escalated', 'Escalated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    policy = models.ForeignKey(DLPPolicy, on_delete=models.SET_NULL, null=True, related_name='incidents')
    
    # Actor
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='dlp_incidents')
    user_email = models.EmailField()
    
    # Context
    action_attempted = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100)
    classification = models.ForeignKey(DataClassification, on_delete=models.SET_NULL, null=True)
    
    # Detection
    detection_method = models.CharField(max_length=100)
    matched_patterns = models.JSONField(default=list)
    
    # Response
    action_taken = models.CharField(max_length=20)
    was_blocked = models.BooleanField(default=False)
    
    # Investigation
    status = models.CharField(max_length=20, choices=INCIDENT_STATUS, default='new')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_dlp_incidents'
    )
    notes = models.TextField(blank=True)
    
    # Timestamps
    occurred_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'dlp_incidents'
        ordering = ['-occurred_at']
    
    def __str__(self):
        return f"DLP Incident: {self.action_attempted} by {self.user_email}"


class AccessPolicy(models.Model):
    """Micro-segmentation access policies"""
    
    POLICY_EFFECT = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Conditions
    conditions = models.JSONField(default=dict, help_text="""
        {
            "roles": ["admin", "manager"],
            "ip_ranges": ["10.0.0.0/8"],
            "time_windows": [{"start": "09:00", "end": "17:00", "days": [0,1,2,3,4]}],
            "device_trust": "verified",
            "mfa_required": true,
            "geo_countries": ["US", "CA"]
        }
    """)
    
    # Resources
    resource_patterns = models.JSONField(default=list, help_text="URL patterns this applies to")
    
    # Effect
    effect = models.CharField(max_length=10, choices=POLICY_EFFECT, default='allow')
    
    # Settings
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'access_policies'
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.effect})"
