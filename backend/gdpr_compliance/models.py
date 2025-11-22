from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import TenantAwareModel


class ConsentType(TenantAwareModel):
    """Types of consent that can be requested from users."""
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=[
            ('essential', 'Essential'),
            ('functional', 'Functional'),
            ('analytics', 'Analytics'),
            ('marketing', 'Marketing'),
            ('third_party', 'Third Party'),
        ],
        default='functional'
    )
    is_required = models.BooleanField(default=False)
    version = models.IntegerField(default=1)
    legal_basis = models.CharField(
        max_length=100,
        choices=[
            ('consent', 'Consent'),
            ('contract', 'Contract'),
            ('legal_obligation', 'Legal Obligation'),
            ('vital_interests', 'Vital Interests'),
            ('public_task', 'Public Task'),
            ('legitimate_interests', 'Legitimate Interests'),
        ],
        default='consent'
    )
    retention_period_days = models.IntegerField(
        null=True,
        blank=True,
        help_text='Number of days to retain data. Null means indefinite.'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gdpr_consent_types'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class UserConsent(TenantAwareModel):
    """Tracks user consent for different purposes."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gdpr_consents')
    consent_type = models.ForeignKey(ConsentType, on_delete=models.CASCADE, related_name='user_consents')
    is_granted = models.BooleanField(default=False)
    consent_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    consent_method = models.CharField(
        max_length=50,
        choices=[
            ('explicit', 'Explicit Opt-in'),
            ('implicit', 'Implicit'),
            ('pre_checked', 'Pre-checked Box'),
            ('opt_out', 'Opt-out'),
        ],
        default='explicit'
    )
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    withdrawal_reason = models.TextField(blank=True)
    version = models.IntegerField(default=1)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'gdpr_user_consents'
        ordering = ['-consent_date']
        indexes = [
            models.Index(fields=['user', 'consent_type']),
            models.Index(fields=['is_granted', 'withdrawn_at']),
        ]

    def __str__(self):
        status = "Granted" if self.is_granted and not self.withdrawn_at else "Withdrawn"
        return f"{self.user.username} - {self.consent_type.name} ({status})"


class DataExportRequest(TenantAwareModel):
    """User requests to export their personal data."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_export_requests')
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    request_type = models.CharField(
        max_length=50,
        choices=[
            ('full_export', 'Full Data Export'),
            ('specific_data', 'Specific Data Categories'),
            ('portability', 'Data Portability'),
        ],
        default='full_export'
    )
    data_categories = models.JSONField(
        default=list,
        blank=True,
        help_text='List of specific data categories to export'
    )
    format = models.CharField(
        max_length=20,
        choices=[
            ('json', 'JSON'),
            ('csv', 'CSV'),
            ('xml', 'XML'),
            ('pdf', 'PDF'),
        ],
        default='json'
    )
    file_url = models.URLField(blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'gdpr_data_export_requests'
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()} ({self.requested_at.strftime('%Y-%m-%d')})"


class DataDeletionRequest(TenantAwareModel):
    """User requests to delete their personal data (Right to be Forgotten)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_deletion_requests')
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    deletion_type = models.CharField(
        max_length=50,
        choices=[
            ('full_deletion', 'Full Account Deletion'),
            ('anonymization', 'Data Anonymization'),
            ('specific_data', 'Specific Data Deletion'),
        ],
        default='full_deletion'
    )
    data_categories = models.JSONField(
        default=list,
        blank=True,
        help_text='Specific data categories to delete'
    )
    reason = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_deletion_requests'
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    backup_created = models.BooleanField(default=False)
    backup_location = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'gdpr_data_deletion_requests'
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()} ({self.requested_at.strftime('%Y-%m-%d')})"


class DataProcessingActivity(TenantAwareModel):
    """Records of processing activities (GDPR Article 30)."""
    name = models.CharField(max_length=200)
    description = models.TextField()
    purpose = models.TextField(help_text='Purpose of processing')
    legal_basis = models.CharField(
        max_length=100,
        choices=[
            ('consent', 'Consent'),
            ('contract', 'Contract'),
            ('legal_obligation', 'Legal Obligation'),
            ('vital_interests', 'Vital Interests'),
            ('public_task', 'Public Task'),
            ('legitimate_interests', 'Legitimate Interests'),
        ]
    )
    data_categories = models.JSONField(
        default=list,
        help_text='Categories of personal data processed'
    )
    data_subjects = models.JSONField(
        default=list,
        help_text='Categories of data subjects (customers, employees, etc.)'
    )
    recipients = models.JSONField(
        default=list,
        help_text='Categories of recipients of personal data'
    )
    third_country_transfers = models.BooleanField(default=False)
    third_countries = models.JSONField(default=list, blank=True)
    safeguards = models.TextField(
        blank=True,
        help_text='Safeguards for international transfers'
    )
    retention_period = models.CharField(max_length=200)
    security_measures = models.TextField(
        help_text='Technical and organizational security measures'
    )
    data_controller = models.CharField(max_length=200)
    data_processor = models.CharField(max_length=200, blank=True)
    dpo_contact = models.EmailField(blank=True, help_text='Data Protection Officer contact')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_reviewed = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'gdpr_processing_activities'
        ordering = ['name']

    def __str__(self):
        return self.name


class DataBreachIncident(TenantAwareModel):
    """Records data breach incidents (GDPR Article 33 & 34)."""
    incident_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(
        max_length=50,
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
            ('critical', 'Critical'),
        ]
    )
    breach_type = models.CharField(
        max_length=100,
        choices=[
            ('confidentiality', 'Confidentiality Breach'),
            ('integrity', 'Integrity Breach'),
            ('availability', 'Availability Breach'),
            ('combined', 'Combined Breach'),
        ]
    )
    discovered_at = models.DateTimeField()
    reported_at = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_breaches')
    affected_users_count = models.IntegerField(default=0)
    affected_users = models.ManyToManyField(User, related_name='data_breaches', blank=True)
    data_categories_affected = models.JSONField(default=list)
    breach_cause = models.TextField()
    containment_measures = models.TextField(blank=True)
    remediation_plan = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('identified', 'Identified'),
            ('investigating', 'Investigating'),
            ('contained', 'Contained'),
            ('remediated', 'Remediated'),
            ('closed', 'Closed'),
        ],
        default='identified'
    )
    authority_notified = models.BooleanField(default=False)
    authority_notification_date = models.DateTimeField(null=True, blank=True)
    users_notified = models.BooleanField(default=False)
    user_notification_date = models.DateTimeField(null=True, blank=True)
    notification_required = models.BooleanField(
        default=True,
        help_text='Whether notification to authorities is required (within 72 hours)'
    )
    risk_assessment = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'gdpr_breach_incidents'
        ordering = ['-discovered_at']

    def __str__(self):
        return f"{self.incident_id} - {self.title} ({self.get_severity_display()})"


class DataAccessLog(TenantAwareModel):
    """Audit log for personal data access."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_access_logs')
    accessed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_accesses_made')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    access_type = models.CharField(
        max_length=50,
        choices=[
            ('view', 'View'),
            ('create', 'Create'),
            ('update', 'Update'),
            ('delete', 'Delete'),
            ('export', 'Export'),
        ]
    )
    data_fields = models.JSONField(
        default=list,
        blank=True,
        help_text='Specific fields accessed'
    )
    purpose = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    accessed_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'gdpr_data_access_logs'
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['user', 'accessed_at']),
            models.Index(fields=['accessed_by', 'accessed_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.accessed_by.username} accessed {self.user.username}'s data ({self.access_type})"


class PrivacyNotice(TenantAwareModel):
    """Privacy notices and policy versions."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    version = models.CharField(max_length=50)
    language = models.CharField(max_length=10, default='en')
    effective_date = models.DateField()
    notice_type = models.CharField(
        max_length=50,
        choices=[
            ('privacy_policy', 'Privacy Policy'),
            ('cookie_policy', 'Cookie Policy'),
            ('data_processing', 'Data Processing Agreement'),
            ('terms_of_service', 'Terms of Service'),
        ],
        default='privacy_policy'
    )
    is_current = models.BooleanField(default=True)
    requires_acceptance = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'gdpr_privacy_notices'
        ordering = ['-effective_date', '-version']

    def __str__(self):
        return f"{self.title} v{self.version}"


class UserPrivacyPreference(TenantAwareModel):
    """User privacy preferences and settings."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='privacy_preferences')
    allow_data_processing = models.BooleanField(default=True)
    allow_marketing_emails = models.BooleanField(default=False)
    allow_analytics = models.BooleanField(default=True)
    allow_third_party_sharing = models.BooleanField(default=False)
    allow_profiling = models.BooleanField(default=False)
    data_retention_preference = models.CharField(
        max_length=50,
        choices=[
            ('minimum', 'Minimum Required'),
            ('standard', 'Standard Period'),
            ('extended', 'Extended Period'),
        ],
        default='standard'
    )
    contact_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text='Preferred contact methods and frequencies'
    )
    accepted_privacy_notices = models.ManyToManyField(PrivacyNotice, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gdpr_user_privacy_preferences'

    def __str__(self):
        return f"{self.user.username}'s Privacy Preferences"
