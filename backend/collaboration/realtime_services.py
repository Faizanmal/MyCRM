"""
Real-time Collaboration Services - WebSocket handling, presence, and conflict resolution.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

User = get_user_model()


class EventType(str, Enum):
    """Real-time event types."""

    # Presence
    PRESENCE_UPDATE = "presence:update"
    PRESENCE_JOINED = "presence:joined"
    PRESENCE_LEFT = "presence:left"
    TYPING_START = "presence:typing_start"
    TYPING_STOP = "presence:typing_stop"

    # Collaboration
    SESSION_STARTED = "session:started"
    SESSION_ENDED = "session:ended"
    PARTICIPANT_JOINED = "session:participant_joined"
    PARTICIPANT_LEFT = "session:participant_left"
    CURSOR_MOVED = "session:cursor_moved"
    SELECTION_CHANGED = "session:selection_changed"

    # Changes
    CHANGE_APPLIED = "change:applied"
    CHANGE_REJECTED = "change:rejected"
    CONFLICT_DETECTED = "change:conflict"
    CONFLICT_RESOLVED = "change:conflict_resolved"

    # Locks
    LOCK_ACQUIRED = "lock:acquired"
    LOCK_RELEASED = "lock:released"
    LOCK_DENIED = "lock:denied"

    # Comments
    COMMENT_ADDED = "comment:added"
    COMMENT_UPDATED = "comment:updated"
    COMMENT_RESOLVED = "comment:resolved"

    # Entity
    ENTITY_UPDATED = "entity:updated"
    ENTITY_DELETED = "entity:deleted"
    VERSION_CREATED = "entity:version_created"


@dataclass
class RealtimeEvent:
    """A real-time event to broadcast."""

    event_type: EventType
    channel: str
    payload: dict
    sender_id: UUID | None = None
    target_user_ids: list[UUID] = field(default_factory=list)
    exclude_sender: bool = True
    timestamp: datetime = field(default_factory=timezone.now)


class ConnectionManager:
    """Manages WebSocket connections and message routing."""

    def __init__(self):
        self.connections: dict[str, set] = {}  # channel -> connections
        self.user_connections: dict[UUID, set] = {}  # user_id -> connections
        self.connection_info: dict[str, dict] = {}  # connection_id -> info
        self._handlers: dict[str, list[Callable]] = {}

    async def connect(
        self,
        connection_id: str,
        user_id: UUID,
        websocket: Any,
        client_info: dict | None = None
    ) -> None:
        """Register a new WebSocket connection."""
        self.connection_info[connection_id] = {
            'websocket': websocket,
            'user_id': user_id,
            'channels': set(),
            'client_info': client_info or {},
            'connected_at': timezone.now(),
        }

        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)

        # Update presence
        await PresenceService.set_online(user_id, connection_id, client_info)

    async def disconnect(self, connection_id: str) -> None:
        """Handle WebSocket disconnection."""
        info = self.connection_info.get(connection_id)
        if not info:
            return

        user_id = info['user_id']

        # Remove from channels
        for channel in info['channels']:
            if channel in self.connections:
                self.connections[channel].discard(connection_id)

        # Remove from user connections
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)

            # If no more connections, set offline
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
                await PresenceService.set_offline(user_id)

        # Clean up
        del self.connection_info[connection_id]

    async def subscribe(self, connection_id: str, channel: str) -> bool:
        """Subscribe a connection to a channel."""
        info = self.connection_info.get(connection_id)
        if not info:
            return False

        if channel not in self.connections:
            self.connections[channel] = set()

        self.connections[channel].add(connection_id)
        info['channels'].add(channel)
        return True

    async def unsubscribe(self, connection_id: str, channel: str) -> bool:
        """Unsubscribe a connection from a channel."""
        info = self.connection_info.get(connection_id)
        if not info:
            return False

        if channel in self.connections:
            self.connections[channel].discard(connection_id)
        info['channels'].discard(channel)
        return True

    async def broadcast(self, event: RealtimeEvent) -> int:
        """Broadcast an event to a channel."""
        connections = self.connections.get(event.channel, set())
        sent_count = 0

        message = {
            'type': event.event_type.value,
            'channel': event.channel,
            'payload': event.payload,
            'sender_id': str(event.sender_id) if event.sender_id else None,
            'timestamp': event.timestamp.isoformat(),
        }

        for conn_id in connections:
            info = self.connection_info.get(conn_id)
            if not info:
                continue

            # Skip sender if requested
            if event.exclude_sender and info['user_id'] == event.sender_id:
                continue

            # Filter by target users
            if event.target_user_ids and info['user_id'] not in event.target_user_ids:
                continue

            try:
                await info['websocket'].send(json.dumps(message))
                sent_count += 1
            except Exception:
                # Connection might be closed
                pass

        return sent_count

    async def send_to_user(
        self,
        user_id: UUID,
        event_type: EventType,
        payload: dict
    ) -> int:
        """Send a message to all connections of a specific user."""
        connections = self.user_connections.get(user_id, set())
        sent_count = 0

        message = {
            'type': event_type.value,
            'payload': payload,
            'timestamp': timezone.now().isoformat(),
        }

        for conn_id in connections:
            info = self.connection_info.get(conn_id)
            if not info:
                continue

            try:
                await info['websocket'].send(json.dumps(message))
                sent_count += 1
            except Exception:
                pass

        return sent_count

    def get_channel_users(self, channel: str) -> list[UUID]:
        """Get all users subscribed to a channel."""
        connections = self.connections.get(channel, set())
        user_ids = set()

        for conn_id in connections:
            info = self.connection_info.get(conn_id)
            if info:
                user_ids.add(info['user_id'])

        return list(user_ids)


# Global connection manager
connection_manager = ConnectionManager()


class PresenceService:
    """Manages user presence across the application."""

    @staticmethod
    async def set_online(
        user_id: UUID,
        connection_id: str,
        client_info: dict | None = None
    ) -> None:
        """Set user as online."""
        from .realtime_models import Presence

        Presence.objects.update_or_create(
            user_id=user_id,
            defaults={
                'status': 'online',
                'connection_id': connection_id,
                'client_info': client_info or {},
                'last_heartbeat': timezone.now(),
            }
        )

        # Broadcast presence update
        await connection_manager.broadcast(RealtimeEvent(
            event_type=EventType.PRESENCE_JOINED,
            channel='presence:global',
            payload={
                'user_id': str(user_id),
                'status': 'online',
            },
            sender_id=user_id,
            exclude_sender=False,
        ))

    @staticmethod
    async def set_offline(user_id: UUID) -> None:
        """Set user as offline."""
        from .realtime_models import Presence

        Presence.objects.filter(user_id=user_id).update(
            status='offline',
            last_heartbeat=timezone.now()
        )

        # Broadcast presence update
        await connection_manager.broadcast(RealtimeEvent(
            event_type=EventType.PRESENCE_LEFT,
            channel='presence:global',
            payload={'user_id': str(user_id), 'status': 'offline'},
            sender_id=user_id,
            exclude_sender=False,
        ))

    @staticmethod
    async def update_status(
        user_id: UUID,
        status: str,
        status_message: str = ''
    ) -> None:
        """Update user's status."""
        from .realtime_models import Presence

        Presence.objects.filter(user_id=user_id).update(
            status=status,
            status_message=status_message,
            last_heartbeat=timezone.now()
        )

        await connection_manager.broadcast(RealtimeEvent(
            event_type=EventType.PRESENCE_UPDATE,
            channel='presence:global',
            payload={
                'user_id': str(user_id),
                'status': status,
                'status_message': status_message,
            },
            sender_id=user_id,
        ))

    @staticmethod
    async def update_location(
        user_id: UUID,
        page: str,
        entity_type: str = '',
        entity_id: UUID | None = None
    ) -> None:
        """Update user's current location."""
        from .realtime_models import Presence

        Presence.objects.filter(user_id=user_id).update(
            current_page=page,
            current_entity_type=entity_type,
            current_entity_id=entity_id,
            last_heartbeat=timezone.now()
        )

    @staticmethod
    async def start_typing(user_id: UUID, field: str) -> None:
        """Indicate user started typing."""
        from .realtime_models import Presence

        presence = Presence.objects.filter(user_id=user_id).first()
        if not presence:
            return

        presence.is_typing = True
        presence.typing_field = field
        presence.save(update_fields=['is_typing', 'typing_field', 'last_heartbeat'])

        if presence.current_entity_id:
            channel = f"entity:{presence.current_entity_type}:{presence.current_entity_id}"
            await connection_manager.broadcast(RealtimeEvent(
                event_type=EventType.TYPING_START,
                channel=channel,
                payload={
                    'user_id': str(user_id),
                    'field': field,
                },
                sender_id=user_id,
            ))

    @staticmethod
    async def stop_typing(user_id: UUID) -> None:
        """Indicate user stopped typing."""
        from .realtime_models import Presence

        presence = Presence.objects.filter(user_id=user_id).first()
        if not presence:
            return

        typing_field = presence.typing_field
        entity_type = presence.current_entity_type
        entity_id = presence.current_entity_id

        presence.is_typing = False
        presence.typing_field = ''
        presence.save(update_fields=['is_typing', 'typing_field', 'last_heartbeat'])

        if entity_id:
            channel = f"entity:{entity_type}:{entity_id}"
            await connection_manager.broadcast(RealtimeEvent(
                event_type=EventType.TYPING_STOP,
                channel=channel,
                payload={
                    'user_id': str(user_id),
                    'field': typing_field,
                },
                sender_id=user_id,
            ))

    @staticmethod
    def get_online_users(entity_type: str = '', entity_id: UUID | None = None) -> list[dict]:
        """Get currently online users, optionally filtered by entity."""
        from .realtime_models import Presence

        queryset = Presence.objects.filter(
            status__in=['online', 'busy', 'away']
        ).select_related('user')

        if entity_type and entity_id:
            queryset = queryset.filter(
                current_entity_type=entity_type,
                current_entity_id=entity_id
            )

        return [
            {
                'user_id': str(p.user_id),
                'username': p.user.username if hasattr(p, 'user') else None,
                'status': p.status,
                'status_message': p.status_message,
                'current_page': p.current_page,
                'is_typing': p.is_typing,
                'typing_field': p.typing_field,
            }
            for p in queryset
        ]


class CollaborationSessionService:
    """Manages collaboration sessions."""

    @staticmethod
    @transaction.atomic
    def create_session(
        entity_type: str,
        entity_id: UUID,
        user_id: UUID,
        **options
    ) -> 'CollaborationSession':
        """Create a new collaboration session."""
        from .realtime_models import CollaborationSession, SessionParticipant

        session = CollaborationSession.objects.create(
            entity_type=entity_type,
            entity_id=entity_id,
            created_by_id=user_id,
            **options
        )

        # Add creator as first participant
        SessionParticipant.objects.create(
            session=session,
            user_id=user_id,
            role='owner',
            status='active'
        )

        return session

    @staticmethod
    def get_or_create_session(
        entity_type: str,
        entity_id: UUID,
        user_id: UUID
    ) -> tuple['CollaborationSession', bool]:
        """Get existing active session or create new one."""
        from .realtime_models import CollaborationSession

        session = CollaborationSession.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            is_active=True
        ).first()

        if session:
            CollaborationSessionService.join_session(session.id, user_id)
            return session, False

        return CollaborationSessionService.create_session(
            entity_type, entity_id, user_id
        ), True

    @staticmethod
    @transaction.atomic
    def join_session(session_id: UUID, user_id: UUID, role: str = 'editor') -> 'SessionParticipant':
        """Join an existing session."""
        from .realtime_models import CollaborationSession, SessionParticipant

        session = CollaborationSession.objects.get(id=session_id, is_active=True)

        participant, created = SessionParticipant.objects.update_or_create(
            session=session,
            user_id=user_id,
            defaults={
                'role': role,
                'status': 'active',
                'left_at': None,
            }
        )

        return participant

    @staticmethod
    async def leave_session(session_id: UUID, user_id: UUID) -> None:
        """Leave a collaboration session."""
        from .realtime_models import SessionParticipant

        participant = SessionParticipant.objects.filter(
            session_id=session_id,
            user_id=user_id
        ).first()

        if participant:
            participant.status = 'disconnected'
            participant.left_at = timezone.now()
            participant.save()

            # Broadcast departure
            channel = f"session:{session_id}"
            await connection_manager.broadcast(RealtimeEvent(
                event_type=EventType.PARTICIPANT_LEFT,
                channel=channel,
                payload={'user_id': str(user_id)},
                sender_id=user_id,
            ))

    @staticmethod
    async def update_cursor(
        session_id: UUID,
        user_id: UUID,
        cursor_position: dict
    ) -> None:
        """Update participant's cursor position."""
        from .realtime_models import SessionParticipant

        SessionParticipant.objects.filter(
            session_id=session_id,
            user_id=user_id
        ).update(
            cursor_position=cursor_position,
            last_seen_at=timezone.now()
        )

        channel = f"session:{session_id}"
        await connection_manager.broadcast(RealtimeEvent(
            event_type=EventType.CURSOR_MOVED,
            channel=channel,
            payload={
                'user_id': str(user_id),
                'cursor': cursor_position,
            },
            sender_id=user_id,
        ))

    @staticmethod
    async def update_selection(
        session_id: UUID,
        user_id: UUID,
        selection: dict
    ) -> None:
        """Update participant's text selection."""
        from .realtime_models import SessionParticipant

        SessionParticipant.objects.filter(
            session_id=session_id,
            user_id=user_id
        ).update(
            selection=selection,
            last_seen_at=timezone.now()
        )

        channel = f"session:{session_id}"
        await connection_manager.broadcast(RealtimeEvent(
            event_type=EventType.SELECTION_CHANGED,
            channel=channel,
            payload={
                'user_id': str(user_id),
                'selection': selection,
            },
            sender_id=user_id,
        ))


class LockService:
    """Manages entity and field locks."""

    DEFAULT_LOCK_DURATION = timedelta(minutes=30)

    @staticmethod
    @transaction.atomic
    def acquire_lock(
        entity_type: str,
        entity_id: UUID,
        user_id: UUID,
        field_path: str = '',
        lock_type: str = 'exclusive',
        duration: timedelta | None = None,
        session_id: UUID | None = None
    ) -> tuple[Optional['EntityLock'], str]:
        """
        Attempt to acquire a lock.
        Returns (lock, error_message) - lock is None if failed.
        """
        from .realtime_models import EntityLock

        duration = duration or LockService.DEFAULT_LOCK_DURATION
        expires_at = timezone.now() + duration

        # Check for existing locks
        existing = EntityLock.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            released_at__isnull=True,
            expires_at__gt=timezone.now()
        )

        if field_path:
            # Check both the specific field and entire entity
            existing = existing.filter(
                models.Q(field_path='') | models.Q(field_path=field_path)
            )
        else:
            # Locking entire entity - any existing lock conflicts
            pass

        if lock_type == 'exclusive' and existing.exists():
            holder = existing.first()
            return None, f"Entity is locked by user {holder.user_id}"

        # Create lock
        lock = EntityLock.objects.create(
            entity_type=entity_type,
            entity_id=entity_id,
            field_path=field_path,
            user_id=user_id,
            session_id=session_id,
            lock_type=lock_type,
            expires_at=expires_at,
        )

        return lock, ''

    @staticmethod
    async def release_lock(lock_id: UUID, user_id: UUID) -> bool:
        """Release a lock."""
        from .realtime_models import EntityLock

        lock = EntityLock.objects.filter(
            id=lock_id,
            user_id=user_id,
            released_at__isnull=True
        ).first()

        if not lock:
            return False

        lock.released_at = timezone.now()
        lock.save()

        # Broadcast lock release
        channel = f"entity:{lock.entity_type}:{lock.entity_id}"
        await connection_manager.broadcast(RealtimeEvent(
            event_type=EventType.LOCK_RELEASED,
            channel=channel,
            payload={
                'lock_id': str(lock_id),
                'field_path': lock.field_path,
                'user_id': str(user_id),
            },
            sender_id=user_id,
        ))

        return True

    @staticmethod
    def get_locks(entity_type: str, entity_id: UUID) -> list['EntityLock']:
        """Get active locks for an entity."""
        from .realtime_models import EntityLock

        return list(EntityLock.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            released_at__isnull=True,
            expires_at__gt=timezone.now()
        ))

    @staticmethod
    def cleanup_expired_locks() -> int:
        """Clean up expired locks."""
        from .realtime_models import EntityLock

        count = EntityLock.objects.filter(
            released_at__isnull=True,
            expires_at__lte=timezone.now()
        ).update(released_at=timezone.now())

        return count


class ConflictResolver:
    """Handles conflict detection and resolution in collaborative editing."""

    @staticmethod
    def detect_conflict(
        base_version: int,
        local_change: dict,
        remote_change: dict
    ) -> str | None:
        """
        Detect if two changes conflict.
        Returns conflict type or None.
        """
        # Same field edited
        if local_change['field_path'] != remote_change['field_path']:
            return None

        # Text operations - check for overlapping positions
        if local_change['change_type'] in ['insert', 'delete', 'replace']:
            local_start = local_change.get('position', 0)
            local_end = local_start + local_change.get('length', 0)

            remote_start = remote_change.get('position', 0)
            remote_end = remote_start + remote_change.get('length', 0)

            # Check overlap
            if local_start <= remote_end and remote_start <= local_end:
                return 'concurrent_edit'

        # Delete + Update
        if local_change['change_type'] == 'delete' and remote_change['change_type'] != 'delete':
            return 'delete_update'

        if remote_change['change_type'] == 'delete' and local_change['change_type'] != 'delete':
            return 'delete_update'

        return None

    @staticmethod
    def resolve_conflict(
        conflict_type: str,
        local_change: dict,
        remote_change: dict,
        strategy: str = 'last_writer_wins'
    ) -> dict:
        """
        Resolve a conflict between two changes.
        Returns the resolved value.
        """
        if strategy == 'last_writer_wins':
            # Use the more recent change
            local_time = local_change.get('timestamp', '')
            remote_time = remote_change.get('timestamp', '')

            if local_time >= remote_time:
                return local_change['new_value']
            return remote_change['new_value']

        elif strategy == 'first_writer_wins':
            local_time = local_change.get('timestamp', '')
            remote_time = remote_change.get('timestamp', '')

            if local_time <= remote_time:
                return local_change['new_value']
            return remote_change['new_value']

        elif strategy == 'auto_merge':
            # Attempt to merge text changes
            return ConflictResolver._merge_text_changes(
                local_change, remote_change
            )

        # Default: return local
        return local_change['new_value']

    @staticmethod
    def _merge_text_changes(local: dict, remote: dict) -> str:
        """
        Attempt to merge two text changes using operational transform.
        """
        # Simplified OT - for production, use a proper OT/CRDT library
        base_text = local.get('old_value', '')

        # Apply changes in order based on position
        if local['position'] <= remote['position']:
            first, second = local, remote
        else:
            first, second = remote, local

        # Apply first change
        result = (
            base_text[:first['position']] +
            first['new_value'] +
            base_text[first['position'] + first.get('length', 0):]
        )

        # Adjust second change position
        offset = len(first['new_value']) - first.get('length', 0)
        adjusted_pos = second['position'] + offset

        # Apply second change
        result = (
            result[:adjusted_pos] +
            second['new_value'] +
            result[adjusted_pos + second.get('length', 0):]
        )

        return result


class ChangeService:
    """Manages collaborative changes and versioning."""

    @staticmethod
    @transaction.atomic
    def apply_change(
        session_id: UUID,
        user_id: UUID,
        field_path: str,
        change_type: str,
        old_value: Any,
        new_value: Any,
        position: int | None = None,
        length: int | None = None
    ) -> tuple['CollaborationChange', Optional['ConflictRecord']]:
        """Apply a change within a session."""
        from .realtime_models import (
            CollaborationChange,
            CollaborationSession,
            ConflictRecord,
            EntityVersion,
            SessionParticipant,
        )

        session = CollaborationSession.objects.select_for_update().get(id=session_id)
        participant = SessionParticipant.objects.get(session=session, user_id=user_id)

        # Get current version
        current_version = EntityVersion.objects.filter(
            entity_type=session.entity_type,
            entity_id=session.entity_id
        ).order_by('-version').first()

        base_version = current_version.version if current_version else 0
        new_version = base_version + 1

        # Check for concurrent changes
        concurrent_changes = CollaborationChange.objects.filter(
            session=session,
            field_path=field_path,
            base_version=base_version,
            applied_at__isnull=False
        ).exclude(participant__user_id=user_id)

        conflict = None
        for concurrent in concurrent_changes:
            conflict_type = ConflictResolver.detect_conflict(
                base_version,
                {
                    'field_path': field_path,
                    'change_type': change_type,
                    'position': position,
                    'length': length,
                    'new_value': new_value,
                },
                {
                    'field_path': concurrent.field_path,
                    'change_type': concurrent.change_type,
                    'position': concurrent.position,
                    'length': concurrent.length,
                    'new_value': concurrent.new_value,
                }
            )

            if conflict_type:
                # Resolve automatically
                resolved = ConflictResolver.resolve_conflict(
                    conflict_type,
                    {'new_value': new_value, 'old_value': old_value},
                    {'new_value': concurrent.new_value, 'old_value': concurrent.old_value},
                    strategy='auto_merge' if change_type in ['insert', 'delete', 'replace'] else 'last_writer_wins'
                )

                # Create our change with resolved value
                change = CollaborationChange.objects.create(
                    session=session,
                    participant=participant,
                    change_type=change_type,
                    field_path=field_path,
                    old_value=old_value,
                    new_value=resolved,
                    position=position,
                    length=length,
                    base_version=base_version,
                    result_version=new_version,
                    is_conflicted=True,
                    conflict_resolution='auto_merge',
                    applied_at=timezone.now()
                )

                conflict = ConflictRecord.objects.create(
                    session=session,
                    local_change=change,
                    remote_change=concurrent,
                    conflict_type=conflict_type,
                    field_path=field_path,
                    resolution_strategy='auto_merge',
                    resolved_value=resolved,
                    resolved_at=timezone.now()
                )

                return change, conflict

        # No conflict - apply normally
        change = CollaborationChange.objects.create(
            session=session,
            participant=participant,
            change_type=change_type,
            field_path=field_path,
            old_value=old_value,
            new_value=new_value,
            position=position,
            length=length,
            base_version=base_version,
            result_version=new_version,
            applied_at=timezone.now()
        )

        return change, None

    @staticmethod
    async def broadcast_change(
        session_id: UUID,
        change: 'CollaborationChange',
        conflict: Optional['ConflictRecord'] = None
    ) -> None:
        """Broadcast a change to session participants."""
        channel = f"session:{session_id}"

        payload = {
            'change_id': str(change.id),
            'field_path': change.field_path,
            'change_type': change.change_type,
            'new_value': change.new_value,
            'position': change.position,
            'length': change.length,
            'version': change.result_version,
            'user_id': str(change.participant.user_id) if change.participant else None,
        }

        if conflict:
            payload['conflict'] = {
                'conflict_id': str(conflict.id),
                'conflict_type': conflict.conflict_type,
                'resolution': conflict.resolution_strategy,
                'resolved_value': conflict.resolved_value,
            }
            event_type = EventType.CONFLICT_RESOLVED
        else:
            event_type = EventType.CHANGE_APPLIED

        await connection_manager.broadcast(RealtimeEvent(
            event_type=event_type,
            channel=channel,
            payload=payload,
            sender_id=change.participant.user_id if change.participant else None,
        ))


class CommentService:
    """Manages real-time comments."""

    @staticmethod
    @transaction.atomic
    def add_comment(
        entity_type: str,
        entity_id: UUID,
        user_id: UUID,
        content: str,
        field_path: str = '',
        selection_start: int | None = None,
        selection_end: int | None = None,
        quoted_text: str = '',
        parent_id: UUID | None = None,
        session_id: UUID | None = None
    ) -> 'Comment':
        """Add a new comment."""
        from .realtime_models import Comment

        parent = None
        thread_root = None

        if parent_id:
            parent = Comment.objects.get(id=parent_id)
            thread_root = parent.thread_root or parent

        comment = Comment.objects.create(
            entity_type=entity_type,
            entity_id=entity_id,
            field_path=field_path,
            selection_start=selection_start,
            selection_end=selection_end,
            quoted_text=quoted_text,
            content=content,
            author_id=user_id,
            parent=parent,
            thread_root=thread_root,
            session_id=session_id,
        )

        return comment

    @staticmethod
    async def broadcast_comment(comment: 'Comment') -> None:
        """Broadcast a new comment."""
        channel = f"entity:{comment.entity_type}:{comment.entity_id}"

        await connection_manager.broadcast(RealtimeEvent(
            event_type=EventType.COMMENT_ADDED,
            channel=channel,
            payload={
                'comment_id': str(comment.id),
                'content': comment.content,
                'field_path': comment.field_path,
                'author_id': str(comment.author_id),
                'parent_id': str(comment.parent_id) if comment.parent_id else None,
                'thread_root_id': str(comment.thread_root_id) if comment.thread_root_id else None,
                'created_at': comment.created_at.isoformat(),
            },
            sender_id=comment.author_id,
        ))

    @staticmethod
    async def resolve_comment(comment_id: UUID, user_id: UUID) -> bool:
        """Resolve a comment."""
        from .realtime_models import Comment

        comment = Comment.objects.filter(id=comment_id).first()
        if not comment:
            return False

        comment.status = 'resolved'
        comment.resolved_at = timezone.now()
        comment.resolved_by_id = user_id
        comment.save()

        channel = f"entity:{comment.entity_type}:{comment.entity_id}"
        await connection_manager.broadcast(RealtimeEvent(
            event_type=EventType.COMMENT_RESOLVED,
            channel=channel,
            payload={
                'comment_id': str(comment_id),
                'resolved_by': str(user_id),
            },
            sender_id=user_id,
        ))

        return True


class RealtimeEventHandler:
    """Handles incoming WebSocket messages."""

    HANDLERS = {}

    @classmethod
    def register(cls, event_type: str):
        """Decorator to register event handlers."""
        def decorator(func):
            cls.HANDLERS[event_type] = func
            return func
        return decorator

    @classmethod
    async def handle(
        cls,
        connection_id: str,
        user_id: UUID,
        message: dict
    ) -> dict | None:
        """Route incoming message to appropriate handler."""
        event_type = message.get('type')
        handler = cls.HANDLERS.get(event_type)

        if handler:
            return await handler(connection_id, user_id, message)

        return {'error': f'Unknown event type: {event_type}'}


# Register handlers
@RealtimeEventHandler.register('subscribe')
async def handle_subscribe(connection_id: str, user_id: UUID, message: dict):
    channel = message.get('channel')
    if channel:
        await connection_manager.subscribe(connection_id, channel)
        return {'status': 'subscribed', 'channel': channel}
    return {'error': 'No channel specified'}


@RealtimeEventHandler.register('unsubscribe')
async def handle_unsubscribe(connection_id: str, user_id: UUID, message: dict):
    channel = message.get('channel')
    if channel:
        await connection_manager.unsubscribe(connection_id, channel)
        return {'status': 'unsubscribed', 'channel': channel}
    return {'error': 'No channel specified'}


@RealtimeEventHandler.register('presence:update')
async def handle_presence_update(connection_id: str, user_id: UUID, message: dict):
    status = message.get('status', 'online')
    status_message = message.get('status_message', '')
    await PresenceService.update_status(user_id, status, status_message)
    return {'status': 'updated'}


@RealtimeEventHandler.register('cursor:move')
async def handle_cursor_move(connection_id: str, user_id: UUID, message: dict):
    session_id = message.get('session_id')
    cursor = message.get('cursor')
    if session_id and cursor:
        await CollaborationSessionService.update_cursor(
            UUID(session_id), user_id, cursor
        )
    return {'status': 'updated'}


@RealtimeEventHandler.register('change:apply')
async def handle_change_apply(connection_id: str, user_id: UUID, message: dict):
    session_id = UUID(message['session_id'])

    change, conflict = ChangeService.apply_change(
        session_id=session_id,
        user_id=user_id,
        field_path=message['field_path'],
        change_type=message['change_type'],
        old_value=message.get('old_value'),
        new_value=message['new_value'],
        position=message.get('position'),
        length=message.get('length'),
    )

    await ChangeService.broadcast_change(session_id, change, conflict)

    return {
        'status': 'applied',
        'change_id': str(change.id),
        'version': change.result_version,
        'conflict': bool(conflict),
    }
