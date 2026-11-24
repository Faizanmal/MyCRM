"""
WebSocket Consumer for Real-Time Collaborative Editing
Uses Django Channels for WebSocket communication.
"""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone


class DocumentCollaborationConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for real-time document collaboration"""

    async def connect(self):
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.room_group_name = f'document_{self.document_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated or not self.user.is_active:
            await self.close(code=4401)
            return

        # Enforce multi-tenant document boundary check
        has_access = await self.check_document_tenant_access()
        if not has_access:
            await self.close(code=4403)
            return

        self.revocation_group = f'user_revocation_{self.user.id}'

        # Join room group and user revocation group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.revocation_group,
            self.channel_name
        )

        await self.accept()

    @database_sync_to_async
    def check_document_tenant_access(self):
        """Verify user is authorized to collaborate on this document"""
        from core.websocket_security import is_user_authorized_for_channel
        authorized, _ = is_user_authorized_for_channel(self.user, f'document_{self.document_id}')
        return authorized

    async def user_session_revoked(self, event):
        """Handle forced disconnect when user is deactivated or revoked mid-session"""
        await self.send_json({
            'type': 'revoked',
            'message': event.get('message', 'Account access or session has been revoked.')
        })
        await self.close(code=4401)

    async def disconnect(self, close_code):
        # Mark session as inactive
        await self.end_editing_session()

        if hasattr(self, 'revocation_group'):
            await self.channel_layer.group_discard(
                self.revocation_group,
                self.channel_name
            )

        # Notify others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': str(self.user.id),
                'username': self.user.username
            }
        )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        message_type = content.get('type')

        if message_type == 'operation':
            await self.handle_operation(content)
        elif message_type == 'cursor_move':
            await self.handle_cursor_move(content)
        elif message_type == 'selection_change':
            await self.handle_selection_change(content)
        elif message_type == 'typing_indicator':
            await self.handle_typing_indicator(content)
        elif message_type == 'comment_added':
            await self.handle_comment_added(content)
        elif message_type == 'ping':
            await self.send_json({'type': 'pong'})

    async def handle_operation(self, content):
        """Handle document edit operation"""
        operation = content.get('operation', {})

        # Save operation to database
        saved_op = await self.save_operation(operation)

        if saved_op:
            # Broadcast to other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'operation_broadcast',
                    'operation': operation,
                    'user_id': str(self.user.id),
                    'username': self.user.username,
                    'version': saved_op.get('version')
                }
            )

    async def handle_cursor_move(self, content):
        """Handle cursor position update"""
        position = content.get('position', {})

        await self.update_cursor_position(position)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_broadcast',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'position': position
            }
        )

    async def handle_selection_change(self, content):
        """Handle text selection update"""
        selection = content.get('selection', {})

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'selection_broadcast',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'selection': selection
            }
        )

    async def handle_typing_indicator(self, content):
        """Handle typing indicator"""
        is_typing = content.get('is_typing', False)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_broadcast',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_typing': is_typing
            }
        )

    async def handle_comment_added(self, content):
        """Handle new comment notification"""
        comment = content.get('comment', {})

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'comment_broadcast',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'comment': comment
            }
        )

    # Broadcast handlers
    async def operation_broadcast(self, event):
        if str(self.user.id) != event['user_id']:
            await self.send_json({
                'type': 'operation',
                'operation': event['operation'],
                'user_id': event['user_id'],
                'username': event['username'],
                'version': event['version']
            })

    async def cursor_broadcast(self, event):
        if str(self.user.id) != event['user_id']:
            await self.send_json({
                'type': 'cursor_move',
                'user_id': event['user_id'],
                'username': event['username'],
                'position': event['position']
            })

    async def selection_broadcast(self, event):
        if str(self.user.id) != event['user_id']:
            await self.send_json({
                'type': 'selection_change',
                'user_id': event['user_id'],
                'username': event['username'],
                'selection': event['selection']
            })

    async def typing_broadcast(self, event):
        if str(self.user.id) != event['user_id']:
            await self.send_json({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            })

    async def comment_broadcast(self, event):
        await self.send_json({
            'type': 'comment_added',
            'user_id': event['user_id'],
            'username': event['username'],
            'comment': event['comment']
        })

    async def user_joined(self, event):
        if str(self.user.id) != event['user_id']:
            await self.send_json({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username'],
                'full_name': event['full_name'],
                'cursor_color': event['cursor_color']
            })

    async def user_left(self, event):
        if str(self.user.id) != event['user_id']:
            await self.send_json({
                'type': 'user_left',
                'user_id': event['user_id'],
                'username': event['username']
            })

    # Database operations
    @database_sync_to_async
    def create_editing_session(self):
        import random

        from .models import CollaborativeDocument, EditingSession

        try:
            doc = CollaborativeDocument.objects.get(id=self.document_id)
        except CollaborativeDocument.DoesNotExist:
            return None

        colors = ['#4F46E5', '#DC2626', '#059669', '#D97706', '#7C3AED', '#DB2777']

        session, _ = EditingSession.objects.update_or_create(
            document=doc,
            user=self.user,
            defaults={
                'channel_name': self.channel_name,
                'is_active': True,
                'cursor_color': random.choice(colors)
            }
        )
        return session

    @database_sync_to_async
    def end_editing_session(self):
        from .models import EditingSession

        EditingSession.objects.filter(
            document_id=self.document_id,
            user=self.user
        ).update(
            is_active=False,
            disconnected_at=timezone.now()
        )

    @database_sync_to_async
    def get_active_users(self):
        from .models import EditingSession

        sessions = EditingSession.objects.filter(
            document_id=self.document_id,
            is_active=True
        ).select_related('user')

        return [
            {
                'user_id': str(s.user.id),
                'username': s.user.username,
                'full_name': f"{s.user.first_name} {s.user.last_name}",
                'cursor_color': s.cursor_color,
                'cursor_position': s.cursor_position
            }
            for s in sessions
        ]

    @database_sync_to_async
    def update_cursor_position(self, position):
        from .models import EditingSession

        EditingSession.objects.filter(
            document_id=self.document_id,
            user=self.user
        ).update(cursor_position=position)

    @database_sync_to_async
    def save_operation(self, operation):
        from .models import CollaborativeDocument, DocumentOperation

        try:
            doc = CollaborativeDocument.objects.get(id=self.document_id)
        except CollaborativeDocument.DoesNotExist:
            return None

        op = DocumentOperation.objects.create(
            document=doc,
            user=self.user,
            operation_type=operation.get('type', 'insert'),
            position=operation.get('position', 0),
            content=operation.get('content', ''),
            length=operation.get('length', 0),
            attributes=operation.get('attributes', {}),
            base_version=doc.version
        )

        doc.version += 1
        doc.last_edited_by = self.user
        doc.save()

        return {'id': str(op.id), 'version': doc.version}
