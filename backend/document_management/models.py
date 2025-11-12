"""
Document Management Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import uuid
import os

User = get_user_model()


def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    
    # Organize by entity type
    if instance.lead:
        return f"documents/leads/{instance.lead.id}/{filename}"
    elif instance.contact:
        return f"documents/contacts/{instance.contact.id}/{filename}"
    elif instance.opportunity:
        return f"documents/opportunities/{instance.opportunity.id}/{filename}"
    else:
        return f"documents/general/{filename}"


class Document(models.Model):
    """Document storage with versioning"""
    
    CATEGORY_CHOICES = [
        ('contract', 'Contract'),
        ('proposal', 'Proposal'),
        ('invoice', 'Invoice'),
        ('presentation', 'Presentation'),
        ('report', 'Report'),
        ('email', 'Email'),
        ('agreement', 'Agreement'),
        ('identification', 'Identification'),
        ('other', 'Other'),
    ]
    
    ACCESS_LEVEL_CHOICES = [
        ('public', 'Public'),
        ('internal', 'Internal'),
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Document info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    
    # File
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 
                              'txt', 'csv', 'jpg', 'jpeg', 'png', 'gif']
        )]
    )
    file_size = models.BigIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100)
    
    # Versioning
    version = models.IntegerField(default=1)
    parent_document = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='versions'
    )
    
    # Entity associations
    lead = models.ForeignKey(
        'lead_management.Lead',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )
    contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )
    
    # Security
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default='internal'
    )
    
    # OCR extracted text
    extracted_text = models.TextField(blank=True, help_text="Text extracted via OCR")
    ocr_processed = models.BooleanField(default=False)
    
    # Tags for searchability
    tags = models.JSONField(default=list, blank=True)
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tracking
    download_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_documents'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['category', 'uploaded_at']),
            models.Index(fields=['lead']),
            models.Index(fields=['contact']),
            models.Index(fields=['opportunity']),
            models.Index(fields=['uploaded_by']),
        ]
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
    
    @property
    def file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.file.name)[1].lower()
    
    @property
    def is_image(self):
        """Check if document is an image"""
        return self.file_extension in ['.jpg', '.jpeg', '.png', '.gif']
    
    @property
    def is_pdf(self):
        """Check if document is a PDF"""
        return self.file_extension == '.pdf'
    
    def create_version(self, new_file, updated_by):
        """Create a new version of this document"""
        new_version = Document.objects.create(
            name=self.name,
            description=self.description,
            category=self.category,
            file=new_file,
            file_size=new_file.size,
            mime_type=new_file.content_type,
            version=self.version + 1,
            parent_document=self.parent_document or self,
            lead=self.lead,
            contact=self.contact,
            opportunity=self.opportunity,
            access_level=self.access_level,
            uploaded_by=updated_by
        )
        return new_version


class DocumentTemplate(models.Model):
    """Reusable document templates for proposals, contracts, etc."""
    
    TEMPLATE_TYPE_CHOICES = [
        ('proposal', 'Proposal'),
        ('contract', 'Contract'),
        ('quote', 'Quote'),
        ('invoice', 'Invoice'),
        ('agreement', 'Agreement'),
        ('letter', 'Letter'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES)
    
    # Template file
    file = models.FileField(upload_to='document_templates/')
    
    # Template variables for dynamic content
    variables = models.JSONField(
        default=list,
        help_text="List of variables: ['client_name', 'amount', 'date', etc.]"
    )
    
    # Preview
    thumbnail = models.ImageField(upload_to='template_thumbnails/', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_document_templates'
        verbose_name = 'Document Template'
        verbose_name_plural = 'Document Templates'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"


class DocumentShare(models.Model):
    """Document sharing with external parties"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='shares')
    
    # Share details
    shared_with_email = models.EmailField()
    access_token = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Permissions
    can_download = models.BooleanField(default=True)
    can_view = models.BooleanField(default=True)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    shared_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_document_shares'
        verbose_name = 'Document Share'
        verbose_name_plural = 'Document Shares'
        ordering = ['-shared_at']
    
    def __str__(self):
        return f"{self.document.name} shared with {self.shared_with_email}"
    
    @property
    def is_expired(self):
        """Check if share link is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_active(self):
        """Check if share is active"""
        return not self.is_expired


class DocumentComment(models.Model):
    """Comments on documents"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    
    comment = models.TextField()
    
    # Optional page reference for PDFs
    page_number = models.IntegerField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_document_comments'
        verbose_name = 'Document Comment'
        verbose_name_plural = 'Document Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.document.name} by {self.created_by}"


class DocumentApproval(models.Model):
    """Document approval workflow"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='approvals')
    
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_approvals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    comments = models.TextField(blank=True)
    
    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approval_requests'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crm_document_approvals'
        verbose_name = 'Document Approval'
        verbose_name_plural = 'Document Approvals'
        ordering = ['-requested_at']
        unique_together = ['document', 'approver']
    
    def __str__(self):
        return f"{self.document.name} approval by {self.approver} ({self.status})"
