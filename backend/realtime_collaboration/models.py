"""
Real-Time Collaboration Models
Documents, versions, comments, and collaborative editing sessions.
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CollaborativeDocument(models.Model):
    """Documents that can be collaboratively edited"""

    DOCUMENT_TYPE = [
        ('proposal', 'Proposal'),
        ('contract', 'Contract'),
        ('note', 'Meeting Notes'),
        ('presentation', 'Presentation'),
        ('report', 'Report'),
        ('template', 'Template'),
        ('other', 'Other'),
    ]

    STATUS = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    PERMISSION_LEVEL = [
        ('view', 'View Only'),
        ('comment', 'Can Comment'),
        ('edit', 'Can Edit'),
        ('admin', 'Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE, default='other')

    # Content
    content = models.JSONField(default=dict)  # Rich text JSON structure
    content_text = models.TextField(blank=True)  # Plain text for search

    # Versioning
    version = models.IntegerField(default=1)

    # Status
    status = models.CharField(max_length=20, choices=STATUS, default='draft')

    # Ownership
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='realtime_owned_documents'
    )
    tenant = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='collaborative_documents'
    )

    # Sharing
    is_public = models.BooleanField(default=False)
    public_link_enabled = models.BooleanField(default=False)
    public_link_token = models.CharField(max_length=64, blank=True)
    default_permission = models.CharField(max_length=10, choices=PERMISSION_LEVEL, default='view')

    # Related entities
    related_lead = models.ForeignKey(
        'lead_management.Lead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collaborative_documents'
    )
    related_opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collaborative_documents'
    )
    related_contact = models.ForeignKey(
        'contact_management.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collaborative_documents'
    )

    # Lock
    is_locked = models.BooleanField(default=False)
    locked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='realtime_locked_documents'
    )
    locked_at = models.DateTimeField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='last_edited_documents'
    )

    class Meta:
        db_table = 'collab_documents'
        verbose_name = 'Collaborative Document'
        verbose_name_plural = 'Collaborative Documents'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class DocumentVersion(models.Model):
    """Version history for documents"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    document = models.ForeignKey(
        CollaborativeDocument,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    version = models.IntegerField()
    content = models.JSONField(default=dict)
    content_text = models.TextField(blank=True)

    # Changes
    changes_summary = models.TextField(blank=True)
    operations = models.JSONField(default=list)  # Operational transform ops

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Restoration
    is_restored = models.BooleanField(default=False)
    restored_from = models.IntegerField(blank=True)

    class Meta:
        db_table = 'collab_document_versions'
        verbose_name = 'Document Version'
        verbose_name_plural = 'Document Versions'
        unique_together = ['document', 'version']
        ordering = ['-version']

    def __str__(self):
        return f"{self.document.title} - v{self.version}"


class DocumentCollaborator(models.Model):
    """Users who have access to a document"""

    PERMISSION_LEVEL = [
        ('view', 'View Only'),
        ('comment', 'Can Comment'),
        ('edit', 'Can Edit'),
        ('admin', 'Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    document = models.ForeignKey(
        CollaborativeDocument,
        on_delete=models.CASCADE,
        related_name='collaborators'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collaborated_documents'
    )

    permission = models.CharField(max_length=10, choices=PERMISSION_LEVEL, default='view')

    # Notifications
    notify_on_changes = models.BooleanField(default=True)
    notify_on_comments = models.BooleanField(default=True)

    # Activity
    last_viewed_at = models.DateTimeField(blank=True)
    last_edited_at = models.DateTimeField(blank=True)

    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_collaborators'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collab_document_collaborators'
        verbose_name = 'Document Collaborator'
        verbose_name_plural = 'Document Collaborators'
        unique_together = ['document', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.document.title}"


class DocumentComment(models.Model):
    """Comments and annotations on documents"""

    COMMENT_TYPE = [
        ('comment', 'Comment'),
        ('suggestion', 'Suggestion'),
        ('question', 'Question'),
        ('approval', 'Approval'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    document = models.ForeignKey(
        CollaborativeDocument,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    # Comment details
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPE, default='comment')
    content = models.TextField()

    # Position in document
    anchor_id = models.CharField(max_length=100, blank=True)  # Element ID
    selection_start = models.IntegerField(blank=True)
    selection_end = models.IntegerField(blank=True)
    selected_text = models.TextField(blank=True)

    # Threading
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='realtime_resolved_comments'
    )
    resolved_at = models.DateTimeField(blank=True)

    # Author
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='realtime_document_comments'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'collab_document_comments'
        verbose_name = 'Document Comment'
        verbose_name_plural = 'Document Comments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.document.title}"


class EditingSession(models.Model):
    """Active editing sessions for real-time collaboration"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    document = models.ForeignKey(
        CollaborativeDocument,
        on_delete=models.CASCADE,
        related_name='editing_sessions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='editing_sessions'
    )

    # Connection
    channel_name = models.CharField(max_length=255)

    # Cursor position
    cursor_position = models.JSONField(default=dict, blank=True)
    selection = models.JSONField(default=dict, blank=True)

    # Presence
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)

    # Color for presence indicator
    cursor_color = models.CharField(max_length=7, default='#4F46E5')

    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'collab_editing_sessions'
        verbose_name = 'Editing Session'
        verbose_name_plural = 'Editing Sessions'

    def __str__(self):
        return f"{self.user.username} editing {self.document.title}"


class DocumentOperation(models.Model):
    """Operational transform operations for conflict resolution"""

    OPERATION_TYPE = [
        ('insert', 'Insert'),
        ('delete', 'Delete'),
        ('retain', 'Retain'),
        ('format', 'Format'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    document = models.ForeignKey(
        CollaborativeDocument,
        on_delete=models.CASCADE,
        related_name='operations'
    )
    session = models.ForeignKey(
        EditingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    # Operation details
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPE)
    position = models.IntegerField()
    content = models.TextField(blank=True)
    length = models.IntegerField(default=0)
    attributes = models.JSONField(default=dict, blank=True)

    # Version tracking
    base_version = models.IntegerField()

    # Conflict resolution
    is_transformed = models.BooleanField(default=False)
    original_operation = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collab_document_operations'
        verbose_name = 'Document Operation'
        verbose_name_plural = 'Document Operations'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.operation_type} at {self.position}"


class DocumentTemplate(models.Model):
    """Reusable document templates"""

    TEMPLATE_TYPE = [
        ('proposal', 'Proposal'),
        ('contract', 'Contract'),
        ('meeting_notes', 'Meeting Notes'),
        ('report', 'Report'),
        ('email', 'Email Template'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE)

    # Content
    content = models.JSONField(default=dict)
    thumbnail_url = models.URLField(blank=True)

    # Variables
    variables = models.JSONField(default=list)  # [{name, type, default}]

    # Ownership
    is_system = models.BooleanField(default=False)
    tenant = models.ForeignKey(
        'multi_tenant.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='realtime_document_templates')

    # Stats
    use_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'collab_document_templates'
        verbose_name = 'Document Template'
        verbose_name_plural = 'Document Templates'

    def __str__(self):
        return self.name
