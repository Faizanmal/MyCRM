"""
Document E-Signature Models
Built-in DocuSign/PandaDoc alternative
"""

import hashlib
import uuid

from django.conf import settings
from django.db import models


class DocumentTemplate(models.Model):
    """Reusable document templates"""

    TEMPLATE_TYPES = [
        ('proposal', 'Proposal'),
        ('contract', 'Contract'),
        ('nda', 'NDA'),
        ('sow', 'Statement of Work'),
        ('quote', 'Quote'),
        ('agreement', 'Agreement'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True)

    # Content
    content_html = models.TextField()  # Rich HTML content with merge fields
    css_styles = models.TextField(blank=True)  # Custom styling

    # Merge fields available in template
    merge_fields = models.JSONField(default=list)  # ['company_name', 'contact_name', etc.]

    # Settings
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_templates'
    )
    is_active = models.BooleanField(default=True)
    is_shared = models.BooleanField(default=True)  # Shared with team

    # Analytics
    times_used = models.IntegerField(default=0)
    avg_completion_time = models.DurationField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class Document(models.Model):
    """Documents sent for signature"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('viewed', 'Viewed'),
        ('partially_signed', 'Partially Signed'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('voided', 'Voided'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )

    # Linked CRM objects
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='esign_documents'
    )
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='esign_documents'
    )

    # Content
    content_html = models.TextField()  # Final rendered content
    content_pdf = models.FileField(upload_to='esign/documents/', null=True, blank=True)
    signed_pdf = models.FileField(upload_to='esign/signed/', null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='esign_documents'
    )

    # Timing
    sent_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Settings
    require_all_signatures = models.BooleanField(default=True)
    signing_order = models.BooleanField(default=False)  # Sequential signing
    send_reminders = models.BooleanField(default=True)
    reminder_interval_days = models.IntegerField(default=3)

    # Security
    access_code_required = models.BooleanField(default=False)

    # Value tracking
    document_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def signing_progress(self):
        total = self.recipients.count()
        signed = self.recipients.filter(signed_at__isnull=False).count()
        return f"{signed}/{total}"


class DocumentRecipient(models.Model):
    """Recipients who need to sign/view a document"""

    RECIPIENT_TYPES = [
        ('signer', 'Needs to Sign'),
        ('viewer', 'View Only'),
        ('approver', 'Needs to Approve'),
        ('cc', 'Receives Copy'),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='recipients'
    )

    # Recipient info
    name = models.CharField(max_length=200)
    email = models.EmailField()
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    recipient_type = models.CharField(max_length=10, choices=RECIPIENT_TYPES, default='signer')
    signing_order = models.IntegerField(default=0)

    # Status tracking
    access_token = models.CharField(max_length=100, unique=True)
    access_code = models.CharField(max_length=20, blank=True)  # Optional PIN

    viewed_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    decline_reason = models.TextField(blank=True)

    # IP tracking
    viewed_from_ip = models.GenericIPAddressField(null=True, blank=True)
    signed_from_ip = models.GenericIPAddressField(null=True, blank=True)

    # Reminders
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    reminders_sent_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['signing_order', 'created_at']

    def __str__(self):
        return f"{self.name} - {self.document.name}"

    def save(self, *args, **kwargs):
        if not self.access_token:
            self.access_token = hashlib.sha256(
                f"{uuid.uuid4()}{self.email}".encode()
            ).hexdigest()[:64]
        super().save(*args, **kwargs)


class SignatureField(models.Model):
    """Signature and form fields on document"""

    FIELD_TYPES = [
        ('signature', 'Signature'),
        ('initials', 'Initials'),
        ('date', 'Date'),
        ('text', 'Text Input'),
        ('checkbox', 'Checkbox'),
        ('dropdown', 'Dropdown'),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='fields'
    )
    recipient = models.ForeignKey(
        DocumentRecipient,
        on_delete=models.CASCADE,
        related_name='fields'
    )

    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    field_name = models.CharField(max_length=100, blank=True)

    # Position (percentage-based for responsiveness)
    page_number = models.IntegerField(default=1)
    x_position = models.DecimalField(max_digits=5, decimal_places=2)  # % from left
    y_position = models.DecimalField(max_digits=5, decimal_places=2)  # % from top
    width = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    height = models.DecimalField(max_digits=5, decimal_places=2, default=5)

    # Settings
    is_required = models.BooleanField(default=True)
    default_value = models.CharField(max_length=500, blank=True)
    dropdown_options = models.JSONField(default=list)  # For dropdown type

    # Value
    value = models.TextField(blank=True)
    filled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['page_number', 'y_position', 'x_position']

    def __str__(self):
        return f"{self.get_field_type_display()} for {self.recipient.name}"


class Signature(models.Model):
    """Captured signatures"""

    SIGNATURE_TYPES = [
        ('drawn', 'Drawn'),
        ('typed', 'Typed'),
        ('uploaded', 'Uploaded'),
    ]

    recipient = models.ForeignKey(
        DocumentRecipient,
        on_delete=models.CASCADE,
        related_name='signatures'
    )
    field = models.OneToOneField(
        SignatureField,
        on_delete=models.CASCADE,
        related_name='signature'
    )

    signature_type = models.CharField(max_length=10, choices=SIGNATURE_TYPES)
    signature_data = models.TextField()  # Base64 image or text

    # Legal info
    signer_name = models.CharField(max_length=200)
    signer_email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Signature by {self.signer_name}"


class DocumentAuditLog(models.Model):
    """Audit trail for document activities"""

    ACTION_TYPES = [
        ('created', 'Document Created'),
        ('sent', 'Document Sent'),
        ('viewed', 'Document Viewed'),
        ('signed', 'Document Signed'),
        ('declined', 'Document Declined'),
        ('completed', 'All Signatures Complete'),
        ('voided', 'Document Voided'),
        ('reminder_sent', 'Reminder Sent'),
        ('downloaded', 'Document Downloaded'),
        ('field_filled', 'Field Filled'),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    recipient = models.ForeignKey(
        DocumentRecipient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    details = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} - {self.document.name}"


class SavedSignature(models.Model):
    """User's saved signatures for reuse"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_signatures'
    )

    name = models.CharField(max_length=100, default='My Signature')
    signature_data = models.TextField()  # Base64 image
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.user.email}'s signature"


class DocumentAnalytics(models.Model):
    """Analytics for document performance"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_analytics'
    )
    date = models.DateField()

    # Volume metrics
    documents_created = models.IntegerField(default=0)
    documents_sent = models.IntegerField(default=0)
    documents_completed = models.IntegerField(default=0)
    documents_declined = models.IntegerField(default=0)

    # Performance metrics
    avg_completion_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_value_sent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_value_signed = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date}"
