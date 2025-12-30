"""
Real-time Collaboration Models - Live editing, presence, and conflict resolution.
"""

import uuid
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class CollaborationSession(models.Model):
    """Active collaboration session for a document or entity."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Target entity
    entity_type = models.CharField(max_length=50)  # contact, deal, document, etc.
    entity_id = models.UUIDField()
    
    # Session metadata
    name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Session settings
    allow_anonymous = models.BooleanField(default=False)
    max_participants = models.PositiveIntegerField(default=50)
    require_lock_for_edit = models.BooleanField(default=False)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Created by
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sessions'
    )
    
    class Meta:
        db_table = 'collaboration_session'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['is_active']),
        ]


class SessionParticipant(models.Model):
    """Tracks participants in a collaboration session."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    session = models.ForeignKey(
        CollaborationSession,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='session_participations'
    )
    
    # Presence
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('idle', 'Idle'),
            ('away', 'Away'),
            ('disconnected', 'Disconnected'),
        ],
        default='active'
    )
    
    # Permissions
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Owner'),
            ('editor', 'Editor'),
            ('commenter', 'Commenter'),
            ('viewer', 'Viewer'),
        ],
        default='editor'
    )
    
    # Cursor/selection tracking
    cursor_position = models.JSONField(null=True, blank=True)
    # e.g., {"field": "description", "offset": 150, "length": 0}
    
    selection = models.JSONField(null=True, blank=True)
    # e.g., {"field": "description", "start": 100, "end": 150}
    
    # UI state
    viewport = models.JSONField(null=True, blank=True)
    # e.g., {"scrollTop": 500, "section": "details"}
    
    # Timing
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    # Connection info
    connection_id = models.CharField(max_length=100, blank=True)
    client_info = models.JSONField(default=dict)  # Browser, device, etc.
    
    class Meta:
        db_table = 'collaboration_session_participant'
        unique_together = ['session', 'user']


class CollaborationChange(models.Model):
    """Individual change made during collaboration."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    session = models.ForeignKey(
        CollaborationSession,
        on_delete=models.CASCADE,
        related_name='changes'
    )
    participant = models.ForeignKey(
        SessionParticipant,
        on_delete=models.SET_NULL,
        null=True,
        related_name='changes'
    )
    
    # Change details
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('insert', 'Insert'),
            ('delete', 'Delete'),
            ('replace', 'Replace'),
            ('move', 'Move'),
            ('format', 'Format'),
        ]
    )
    
    # Target
    field_path = models.CharField(max_length=200)  # e.g., "description", "custom_fields.notes"
    
    # Change content
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    
    # For text operations (OT/CRDT)
    position = models.PositiveIntegerField(null=True, blank=True)  # Offset in text
    length = models.PositiveIntegerField(null=True, blank=True)  # Length of affected text
    
    # Versioning
    base_version = models.PositiveIntegerField()  # Version this change is based on
    result_version = models.PositiveIntegerField()  # Version after applying change
    
    # Conflict handling
    is_conflicted = models.BooleanField(default=False)
    conflict_resolution = models.CharField(max_length=20, blank=True)
    # 'accepted', 'rejected', 'merged', 'manual'
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    applied_at = models.DateTimeField(null=True)
    
    class Meta:
        db_table = 'collaboration_change'
        ordering = ['result_version']
        indexes = [
            models.Index(fields=['session', 'result_version']),
        ]


class EntityVersion(models.Model):
    """Version history for collaborative entities."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Entity reference
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    
    # Version info
    version = models.PositiveIntegerField()
    
    # Snapshot of entity at this version
    snapshot = models.JSONField()
    
    # Changes that led to this version
    changes = models.JSONField(default=list)  # List of change IDs
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Session reference
    session = models.ForeignKey(
        CollaborationSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions'
    )
    
    class Meta:
        db_table = 'collaboration_entity_version'
        unique_together = ['entity_type', 'entity_id', 'version']
        ordering = ['-version']


class EntityLock(models.Model):
    """Locks for exclusive editing of entities or fields."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # What is locked
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    field_path = models.CharField(max_length=200, blank=True)  # Empty = entire entity
    
    # Lock holder
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='entity_locks'
    )
    session = models.ForeignKey(
        CollaborationSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='locks'
    )
    
    # Lock type
    lock_type = models.CharField(
        max_length=20,
        choices=[
            ('exclusive', 'Exclusive'),
            ('shared', 'Shared'),
            ('intent', 'Intent'),
        ],
        default='exclusive'
    )
    
    # Timing
    acquired_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    released_at = models.DateTimeField(null=True, blank=True)
    
    # Auto-release settings
    auto_release_on_disconnect = models.BooleanField(default=True)
    max_duration_seconds = models.PositiveIntegerField(default=3600)
    
    class Meta:
        db_table = 'collaboration_entity_lock'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id', 'field_path']),
        ]


class ConflictRecord(models.Model):
    """Records of conflicts that occurred during collaboration."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    session = models.ForeignKey(
        CollaborationSession,
        on_delete=models.CASCADE,
        related_name='conflicts'
    )
    
    # Conflicting changes
    local_change = models.ForeignKey(
        CollaborationChange,
        on_delete=models.CASCADE,
        related_name='conflicts_as_local'
    )
    remote_change = models.ForeignKey(
        CollaborationChange,
        on_delete=models.CASCADE,
        related_name='conflicts_as_remote'
    )
    
    # Conflict details
    conflict_type = models.CharField(
        max_length=30,
        choices=[
            ('concurrent_edit', 'Concurrent Edit'),
            ('delete_update', 'Delete/Update'),
            ('move_edit', 'Move/Edit'),
            ('format_conflict', 'Format Conflict'),
        ]
    )
    
    field_path = models.CharField(max_length=200)
    
    # Resolution
    resolution_strategy = models.CharField(
        max_length=20,
        choices=[
            ('auto_merge', 'Auto Merge'),
            ('last_writer_wins', 'Last Writer Wins'),
            ('first_writer_wins', 'First Writer Wins'),
            ('manual', 'Manual Resolution'),
            ('fork', 'Fork (Keep Both)'),
        ],
        blank=True
    )
    
    resolved_value = models.JSONField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_conflicts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'collaboration_conflict'


class Comment(models.Model):
    """Comments on entities during collaboration."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Target
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    field_path = models.CharField(max_length=200, blank=True)  # Specific field
    
    # For inline comments (text selection)
    selection_start = models.PositiveIntegerField(null=True, blank=True)
    selection_end = models.PositiveIntegerField(null=True, blank=True)
    quoted_text = models.TextField(blank=True)
    
    # Comment content
    content = models.TextField()
    
    # Threading
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    thread_root = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='thread_comments'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Open'),
            ('resolved', 'Resolved'),
            ('wont_fix', 'Won\'t Fix'),
        ],
        default='open'
    )
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collaboration_comments'
    )
    
    # Mentions
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comment_mentions',
        blank=True
    )
    
    # Session context
    session = models.ForeignKey(
        CollaborationSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_comments'
    )
    
    class Meta:
        db_table = 'collaboration_comment'
        ordering = ['created_at']


class Presence(models.Model):
    """Real-time presence tracking across the application."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='presence_records'
    )
    
    # Current location
    current_page = models.CharField(max_length=500)
    current_entity_type = models.CharField(max_length=50, blank=True)
    current_entity_id = models.UUIDField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('online', 'Online'),
            ('busy', 'Busy'),
            ('away', 'Away'),
            ('dnd', 'Do Not Disturb'),
            ('offline', 'Offline'),
        ],
        default='online'
    )
    status_message = models.CharField(max_length=200, blank=True)
    
    # Activity
    is_typing = models.BooleanField(default=False)
    typing_field = models.CharField(max_length=200, blank=True)
    
    # Connection
    connection_id = models.CharField(max_length=100)
    connected_at = models.DateTimeField(auto_now_add=True)
    last_heartbeat = models.DateTimeField(auto_now=True)
    
    # Client info
    client_info = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'collaboration_presence'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['current_entity_type', 'current_entity_id']),
            models.Index(fields=['last_heartbeat']),
        ]


class RealtimeChannel(models.Model):
    """Configuration for real-time broadcast channels."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=200, unique=True)
    channel_type = models.CharField(
        max_length=30,
        choices=[
            ('entity', 'Entity Updates'),
            ('user', 'User Channel'),
            ('team', 'Team Channel'),
            ('broadcast', 'Broadcast'),
            ('session', 'Collaboration Session'),
        ]
    )
    
    # Access control
    is_public = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='allowed_channels',
        blank=True
    )
    allowed_roles = ArrayField(models.CharField(max_length=50), default=list)
    
    # Settings
    persist_messages = models.BooleanField(default=False)
    max_message_history = models.PositiveIntegerField(default=100)
    
    # Stats
    subscriber_count = models.PositiveIntegerField(default=0)
    message_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'collaboration_realtime_channel'


class RealtimeMessage(models.Model):
    """Messages sent through real-time channels."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    channel = models.ForeignKey(
        RealtimeChannel,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    # Message content
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    
    # Sender
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Targeting
    target_users = ArrayField(models.UUIDField(), default=list)  # Empty = all subscribers
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'collaboration_realtime_message'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['channel', 'created_at']),
        ]
