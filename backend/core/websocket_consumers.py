"""
WebSocket Consumer for Real-time CRM Notifications
Handles live updates for notifications, recommendations, and activities
"""

import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class CRMNotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time CRM notifications

    Handles:
    - Live notifications
    - AI recommendation updates
    - Deal stage changes
    - Team activity updates
    - Achievement unlocks
    """

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            # Try to authenticate from query string
            query_string = self.scope.get('query_string', b'').decode()
            token = self._get_token_from_query(query_string)
            if token:
                self.user = await self._authenticate_token(token)

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        # Create user-specific group
        self.user_group = f'user_{self.user.id}'

        # Join user-specific group
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )

        # Join global broadcasts group
        await self.channel_layer.group_add(
            'crm_global',
            self.channel_name
        )

        # If user has team, join team group
        team_id = await self._get_user_team_id()
        if team_id:
            self.team_group = f'team_{team_id}'
            await self.channel_layer.group_add(
                self.team_group,
                self.channel_name
            )

        await self.accept()

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'payload': {
                'status': 'connected',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        }))

        logger.info(f"WebSocket connected for user {self.user.id}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

        await self.channel_layer.group_discard(
            'crm_global',
            self.channel_name
        )

        if hasattr(self, 'team_group'):
            await self.channel_layer.group_discard(
                self.team_group,
                self.channel_name
            )

        logger.info(f"WebSocket disconnected: {close_code}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')
            payload = data.get('payload', {})

            # Handle different message types
            handlers = {
                'ping': self._handle_ping,
                'subscribe': self._handle_subscribe,
                'unsubscribe': self._handle_unsubscribe,
                'read_notification': self._handle_read_notification,
                'presence': self._handle_presence,
            }

            handler = handlers.get(message_type)
            if handler:
                await handler(payload)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'payload': {'message': f'Unknown message type: {message_type}'}
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'payload': {'message': 'Invalid JSON'}
            }))
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'payload': {'message': str(e)}
            }))

    # ==================== Message Handlers ====================

    async def _handle_ping(self, payload):
        """Handle ping/pong for keepalive"""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'payload': {'timestamp': payload.get('timestamp')}
        }))

    async def _handle_subscribe(self, payload):
        """Subscribe to additional channels"""
        channel = payload.get('channel')
        if channel:
            await self.channel_layer.group_add(channel, self.channel_name)
            await self.send(text_data=json.dumps({
                'type': 'subscribed',
                'payload': {'channel': channel}
            }))

    async def _handle_unsubscribe(self, payload):
        """Unsubscribe from channels"""
        channel = payload.get('channel')
        if channel:
            await self.channel_layer.group_discard(channel, self.channel_name)
            await self.send(text_data=json.dumps({
                'type': 'unsubscribed',
                'payload': {'channel': channel}
            }))

    async def _handle_read_notification(self, payload):
        """Mark notification as read"""
        notification_id = payload.get('id')
        if notification_id:
            await self._mark_notification_read(notification_id)

    async def _handle_presence(self, payload):
        """Handle user presence updates"""
        status = payload.get('status', 'online')
        # Broadcast to team
        if hasattr(self, 'team_group'):
            await self.channel_layer.group_send(
                self.team_group,
                {
                    'type': 'presence_update',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'status': status,
                }
            )

    # ==================== Group Message Handlers ====================
    # These handle messages sent to channel groups

    async def notification(self, event):
        """Handle notification messages"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'payload': event.get('payload', {}),
            'timestamp': event.get('timestamp', '')
        }))

    async def recommendation(self, event):
        """Handle AI recommendation updates"""
        await self.send(text_data=json.dumps({
            'type': 'recommendation',
            'payload': event.get('payload', {}),
            'timestamp': event.get('timestamp', '')
        }))

    async def achievement(self, event):
        """Handle achievement unlocks"""
        await self.send(text_data=json.dumps({
            'type': 'achievement',
            'payload': event.get('payload', {}),
            'timestamp': event.get('timestamp', '')
        }))

    async def deal_update(self, event):
        """Handle deal/opportunity updates"""
        await self.send(text_data=json.dumps({
            'type': 'deal_update',
            'payload': event.get('payload', {}),
            'timestamp': event.get('timestamp', '')
        }))

    async def mention(self, event):
        """Handle @mentions"""
        await self.send(text_data=json.dumps({
            'type': 'mention',
            'payload': event.get('payload', {}),
            'timestamp': event.get('timestamp', '')
        }))

    async def activity(self, event):
        """Handle activity feed updates"""
        await self.send(text_data=json.dumps({
            'type': 'activity',
            'payload': event.get('payload', {}),
            'timestamp': event.get('timestamp', '')
        }))

    async def presence_update(self, event):
        """Handle team presence updates"""
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'payload': {
                'user_id': event['user_id'],
                'username': event['username'],
                'status': event['status'],
            }
        }))

    async def broadcast(self, event):
        """Handle global broadcast messages"""
        await self.send(text_data=json.dumps({
            'type': 'broadcast',
            'payload': event.get('payload', {}),
            'timestamp': event.get('timestamp', '')
        }))

    # ==================== Helper Methods ====================

    def _get_token_from_query(self, query_string):
        """Extract token from query string"""
        params = dict(p.split('=') for p in query_string.split('&') if '=' in p)
        return params.get('token')

    @database_sync_to_async
    def _authenticate_token(self, token):
        """Authenticate user from JWT token"""
        try:
            from django.contrib.auth import get_user_model
            from rest_framework_simplejwt.tokens import AccessToken

            access_token = AccessToken(token)
            user_id = access_token['user_id']
            User = get_user_model()
            return User.objects.get(id=user_id)
        except Exception as e:
            logger.error(f"Token authentication failed: {e}")
            return None

    @database_sync_to_async
    def _get_user_team_id(self):
        """Get the user's team ID if any"""
        try:
            # Try to get team from user profile
            if hasattr(self.user, 'team_id'):
                return self.user.team_id
            if hasattr(self.user, 'profile') and hasattr(self.user.profile, 'team_id'):
                return self.user.profile.team_id
        except Exception:
            pass
        return None

    @database_sync_to_async
    def _mark_notification_read(self, notification_id):
        """Mark a notification as read in the database"""
        try:
            from activity_feed.models import Notification

            Notification.objects.filter(
                id=notification_id,
                user=self.user
            ).update(
                is_read=True,
                read_at=timezone.now()
            )
        except Exception as e:
            logger.error(f"Failed to mark notification read: {e}")


# ==================== Utility Functions for Sending Messages ====================

async def send_user_notification(user_id, notification_type, payload):
    """
    Send a notification to a specific user

    Usage:
        await send_user_notification(
            user_id=1,
            notification_type='deal_update',
            payload={'deal_id': 123, 'stage': 'proposal'}
        )
    """
    from channels.layers import get_channel_layer
    from django.utils import timezone

    channel_layer = get_channel_layer()

    await channel_layer.group_send(
        f'user_{user_id}',
        {
            'type': notification_type,
            'payload': payload,
            'timestamp': timezone.now().isoformat(),
        }
    )


async def broadcast_team_notification(team_id, notification_type, payload):
    """Send notification to all members of a team"""
    from channels.layers import get_channel_layer
    from django.utils import timezone

    channel_layer = get_channel_layer()

    await channel_layer.group_send(
        f'team_{team_id}',
        {
            'type': notification_type,
            'payload': payload,
            'timestamp': timezone.now().isoformat(),
        }
    )


async def broadcast_global(notification_type, payload):
    """Broadcast to all connected users"""
    from channels.layers import get_channel_layer
    from django.utils import timezone

    channel_layer = get_channel_layer()

    await channel_layer.group_send(
        'crm_global',
        {
            'type': 'broadcast',
            'payload': {
                'notification_type': notification_type,
                **payload
            },
            'timestamp': timezone.now().isoformat(),
        }
    )


# Synchronous wrappers for use in signals and views
def sync_send_user_notification(user_id, notification_type, payload):
    """Synchronous wrapper for send_user_notification"""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(send_user_notification(user_id, notification_type, payload))
    finally:
        loop.close()


def sync_broadcast_team(team_id, notification_type, payload):
    """Synchronous wrapper for broadcast_team_notification"""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(broadcast_team_notification(team_id, notification_type, payload))
    finally:
        loop.close()


async def send_export_progress(user_id, job_id, progress, status):
    """
    Send export progress update to user

    Usage:
        await send_export_progress(
            user_id=1,
            job_id=123,
            progress=50,
            status='processing'
        )
    """
    from channels.layers import get_channel_layer
    from django.utils import timezone

    channel_layer = get_channel_layer()

    await channel_layer.group_send(
        f'user_{user_id}',
        {
            'type': 'export_progress',
            'payload': {
                'job_id': job_id,
                'progress': progress,
                'status': status,
            },
            'timestamp': timezone.now().isoformat(),
        }
    )
