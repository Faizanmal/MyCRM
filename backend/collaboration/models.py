import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from multi_tenant.models import TenantAwareModel

User = get_user_model()


class DealRoom(TenantAwareModel):
    """
    Secure collaboration space for deals/opportunities.
    Virtual rooms where teams can collaborate on specific deals.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('completed', 'Completed'),
    ]

    PRIVACY_CHOICES = [
        ('private', 'Private - Invite Only'),
        ('team', 'Team - All team members'),
        ('public', 'Public - Organization wide'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Link to opportunity or custom deal
    opportunity = models.ForeignKey(
        'opportunity_management.Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deal_rooms'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='private')

    # Owner and participants
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_deal_rooms'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived_at = models.DateTimeField(blank=True)

    # Statistics
    message_count = models.PositiveIntegerField(default=0)
    document_count = models.PositiveIntegerField(default=0)
    participant_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['owner', 'status']),
        ]

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class DealRoomParticipant(TenantAwareModel):
    """
    Participants in a deal room with specific roles and permissions.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('contributor', 'Contributor'),
        ('viewer', 'Viewer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal_room = models.ForeignKey(
        DealRoom,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    # Permissions
    can_invite = models.BooleanField(default=False)
    can_edit_room = models.BooleanField(default=False)
    can_upload_documents = models.BooleanField(default=True)
    can_delete_messages = models.BooleanField(default=False)

    # Activity tracking
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Notifications
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    class Meta:
        unique_together = [('deal_room', 'user')]
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['deal_room', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.deal_room.name} ({self.role})"


class Channel(TenantAwareModel):
    """
    Team messaging channel for real-time collaboration.
    """
    CHANNEL_TYPE_CHOICES = [
        ('public', 'Public Channel'),
        ('private', 'Private Channel'),
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPE_CHOICES, default='public')

    # Creator and members
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_channels'
    )
    members = models.ManyToManyField(
        User,
        through='ChannelMembership',
        related_name='channels'
    )

    # Settings
    is_archived = models.BooleanField(default=False)
    is_read_only = models.BooleanField(default=False)
    allow_threads = models.BooleanField(default=True)
    allow_file_sharing = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived_at = models.DateTimeField(blank=True)

    # Statistics
    message_count = models.PositiveIntegerField(default=0)
    member_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['organization', 'channel_type']),
            models.Index(fields=['created_by', 'is_archived']),
        ]

    def __str__(self):
        return f"#{self.name}" if self.channel_type == 'public' else self.name


class ChannelMembership(models.Model):
    """
    Tracks user membership in channels.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Membership details
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(auto_now_add=True)
    is_muted = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    # Permissions
    is_admin = models.BooleanField(default=False)
    can_post = models.BooleanField(default=True)
    can_invite = models.BooleanField(default=False)

    class Meta:
        unique_together = [('channel', 'user')]
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.email} in {self.channel.name}"


class Message(TenantAwareModel):
    """
    Chat message in a channel or deal room.
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text Message'),
        ('file', 'File Attachment'),
        ('system', 'System Message'),
        ('code', 'Code Snippet'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Message location (channel or deal room)
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='messages'
    )
    deal_room = models.ForeignKey(
        DealRoom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='messages'
    )

    # Message content
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_messages'
    )
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()

    # Threading
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    thread_reply_count = models.PositiveIntegerField(default=0)

    # Attachments
    attachments = models.JSONField(default=list, blank=True)

    # Reactions and interactions
    reactions = models.JSONField(default=dict, blank=True)  # {"👍": ["user_id1", "user_id2"]}

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(blank=True)
    deleted_at = models.DateTimeField(blank=True)

    # Flags
    is_pinned = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    # Mentions
    mentioned_users = models.ManyToManyField(
        User,
        related_name='mentioned_in_messages',
        blank=True
    )

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['channel', 'created_at']),
            models.Index(fields=['deal_room', 'created_at']),
            models.Index(fields=['parent_message', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]

    def __str__(self):
        location = self.channel.name if self.channel else self.deal_room.name
        return f"Message by {self.sender.email if self.sender else 'System'} in {location}"


class CollaborativeDocument(TenantAwareModel):
    """
    Document with collaboration features (versioning, comments, co-editing).
    """
    DOC_TYPE_CHOICES = [
        ('document', 'Document'),
        ('spreadsheet', 'Spreadsheet'),
        ('presentation', 'Presentation'),
        ('pdf', 'PDF'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('approved', 'Approved'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, default='document')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # File information
    file_path = models.CharField(max_length=500)
    file_size = models.PositiveBigIntegerField(default=0)  # in bytes
    mime_type = models.CharField(max_length=100, blank=True)

    # Ownership and access
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collaboration_owned_documents'
    )

    # Link to deal room if applicable
    deal_room = models.ForeignKey(
        DealRoom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )

    # Versioning
    version = models.PositiveIntegerField(default=1)
    parent_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions'
    )

    # Collaboration settings
    allow_comments = models.BooleanField(default=True)
    allow_downloads = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    locked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collaboration_locked_documents'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['deal_room', 'status']),
        ]

    def __str__(self):
        return f"{self.title} (v{self.version})"


class DocumentComment(TenantAwareModel):
    """
    Comments on collaborative documents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        CollaborativeDocument,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collaboration_document_comments'
    )

    # Comment content
    content = models.TextField()

    # Location in document
    page_number = models.PositiveIntegerField(blank=True)
    position = models.JSONField(blank=True)  # {"x": 100, "y": 200}
    highlighted_text = models.TextField(blank=True)

    # Threading
    parent_comment = models.ForeignKey(
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
        related_name='collaboration_resolved_comments'
    )
    resolved_at = models.DateTimeField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['document', 'is_resolved']),
            models.Index(fields=['author', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author.email} on {self.document.title}"


class ApprovalWorkflow(TenantAwareModel):
    """
    Configurable approval workflow template.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Workflow configuration
    is_active = models.BooleanField(default=True)
    is_sequential = models.BooleanField(
        default=True,
        help_text='If True, steps execute in order. If False, all steps run in parallel.'
    )

    # Auto-start conditions
    auto_start_on_create = models.BooleanField(default=False)
    trigger_conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text='Conditions to auto-start workflow: {"amount_gt": 10000, "status": "draft"}'
    )

    # Creator
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_workflows'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Statistics
    total_instances = models.PositiveIntegerField(default=0)
    completed_instances = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class ApprovalStep(TenantAwareModel):
    """
    Individual step in an approval workflow.
    """
    STEP_TYPE_CHOICES = [
        ('approval', 'Approval Required'),
        ('review', 'Review Only'),
        ('notification', 'Notification'),
        ('condition', 'Conditional Branch'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name='steps'
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    step_type = models.CharField(max_length=20, choices=STEP_TYPE_CHOICES, default='approval')
    order = models.PositiveIntegerField(default=0)

    # Approvers
    approvers = models.ManyToManyField(
        User,
        related_name='approval_steps',
        blank=True
    )
    approver_count_required = models.PositiveIntegerField(
        default=1,
        help_text='Number of approvals required to pass this step'
    )

    # Conditions for conditional steps
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text='Conditions to execute this step: {"field": "amount", "operator": "gt", "value": 5000}'
    )

    # Settings
    allow_delegate = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    timeout_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Auto-escalate or auto-approve after this many hours'
    )

    # Actions on timeout
    timeout_action = models.CharField(
        max_length=20,
        choices=[('approve', 'Auto-Approve'), ('reject', 'Auto-Reject'), ('escalate', 'Escalate')],
        default='escalate',
        blank=True
    )

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['workflow', 'order']),
        ]

    def __str__(self):
        return f"{self.workflow.name} - Step {self.order}: {self.name}"


class ApprovalInstance(TenantAwareModel):
    """
    Running instance of an approval workflow.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name='instances'
    )

    # What is being approved (generic relation)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Request details
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='requested_approvals'
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_step = models.ForeignKey(
        ApprovalStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_instances'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True)

    # Attachments and context
    attachments = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['workflow', 'status']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.title} - {self.status}"


class ApprovalAction(TenantAwareModel):
    """
    Individual approval action taken on a workflow instance step.
    """
    ACTION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('delegated', 'Delegated'),
        ('commented', 'Commented'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(
        ApprovalInstance,
        on_delete=models.CASCADE,
        related_name='actions'
    )
    step = models.ForeignKey(
        ApprovalStep,
        on_delete=models.CASCADE,
        related_name='actions'
    )

    # Action details
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='approval_actions'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    comment = models.TextField(blank=True)

    # Delegation
    delegated_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delegated_approvals'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['instance', 'step']),
            models.Index(fields=['actor', 'created_at']),
        ]

    def __str__(self):
        return f"{self.actor.email} {self.action} - {self.instance.title}"
