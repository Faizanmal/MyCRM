"""
Real-time WebSocket Notifications
Django Channels consumer for live notifications
"""
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    """

    async def connect(self):
        """Handle WebSocket connection with revocation check"""
        self.user = self.scope['user']

        if self.user.is_anonymous or not self.user.is_active:
            await self.close(code=4401)
            return

        is_valid = await self.is_user_membership_valid()
        if not is_valid:
            await self.close(code=4403)
            return

        # Join user-specific notification group and revocation listener group
        self.user_group_name = f'notifications_{self.user.id}'
        self.revocation_group = f'user_revocation_{self.user.id}'

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.revocation_group,
            self.channel_name
        )

        await self.accept()

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to notification stream'
        }))

    @database_sync_to_async
    def is_user_membership_valid(self):
        """Verify user is active and has valid tenant membership"""
        from core.websocket_security import is_user_still_active
        return is_user_still_active(self.user.id)

    async def user_session_revoked(self, event):
        """Handle forced disconnect when user is deactivated or revoked mid-session"""
        await self.send(text_data=json.dumps({
            'type': 'revoked',
            'message': event.get('message', 'Account access or session has been revoked.')
        }))
        await self.close(code=4401)

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        if hasattr(self, 'revocation_group'):
            await self.channel_layer.group_discard(
                self.revocation_group,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'mark_read':
                # Mark notification as read
                notification_id = data.get('notification_id')
                await self.mark_notification_read(notification_id)

            elif message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def notification_message(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))

    async def activity_update(self, event):
        """Send activity update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'activity',
            'activity': event['activity']
        }))

    async def task_update(self, event):
        """Send task update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'task_update',
            'task': event['task']
        }))

    async def lead_update(self, event):
        """Send lead update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'lead_update',
            'lead': event['lead']
        }))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read in database"""
        from activity_feed.models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False


class ActivityFeedConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time activity feed updates scoped to tenant
    """

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']

        if self.user.is_anonymous or not self.user.is_active:
            await self.close(code=4401)
            return

        # Get tenant/organization from scope or user
        self.tenant_id = await self.get_user_tenant_id()
        if not self.tenant_id:
            await self.close(code=4403)
            return

        # Join tenant-scoped activity feed group and user revocation group
        self.feed_group_name = f'activity_feed_tenant_{self.tenant_id}'
        self.revocation_group = f'user_revocation_{self.user.id}'

        await self.channel_layer.group_add(
            self.feed_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.revocation_group,
            self.channel_name
        )

        await self.accept()

    @database_sync_to_async
    def get_user_tenant_id(self):
        """Resolve user's primary organization membership ID"""
        from multi_tenant.models import OrganizationMember
        user = getattr(self, 'user', None) or (self.scope.get('user') if hasattr(self, 'scope') else None)
        if not user or user.is_anonymous:
            return None
        membership = OrganizationMember.objects.filter(user=user, is_active=True).first()
        return membership.organization_id if membership else None

    async def user_session_revoked(self, event):
        """Handle forced disconnect when user is deactivated or revoked mid-session"""
        await self.send(text_data=json.dumps({
            'type': 'revoked',
            'message': event.get('message', 'Account access or session has been revoked.')
        }))
        await self.close(code=4401)

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if hasattr(self, 'feed_group_name'):
            await self.channel_layer.group_discard(
                self.feed_group_name,
                self.channel_name
            )
        if hasattr(self, 'revocation_group'):
            await self.channel_layer.group_discard(
                self.revocation_group,
                self.channel_name
            )

    async def activity_created(self, event):
        """Send new activity to feed"""
        await self.send(text_data=json.dumps({
            'type': 'activity_created',
            'activity': event['activity']
        }))


class RealtimeConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time updates with channel subscriptions
    """

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        self.subscribed_channels = set()

        if self.user.is_anonymous or not self.user.is_active:
            await self.close(code=4401)
            return

        is_valid = await self.is_user_membership_valid()
        if not is_valid:
            await self.close(code=4403)
            return

        self.revocation_group = f'user_revocation_{self.user.id}'
        await self.channel_layer.group_add(
            self.revocation_group,
            self.channel_name
        )

        await self.accept()

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to realtime stream'
        }))

    @database_sync_to_async
    def is_user_membership_valid(self):
        """Verify user is active and has valid tenant membership"""
        from core.websocket_security import is_user_still_active
        return is_user_still_active(self.user.id)

    @database_sync_to_async
    def verify_channel_access(self, channel):
        """Verify whether user is authorized to subscribe to channel"""
        from core.websocket_security import is_user_authorized_for_channel
        return is_user_authorized_for_channel(self.user, channel)

    async def user_session_revoked(self, event):
        """Handle forced disconnect when user is deactivated or revoked mid-session"""
        await self.send(text_data=json.dumps({
            'type': 'revoked',
            'message': event.get('message', 'Account access or session has been revoked.')
        }))
        await self.close(code=4401)

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Unsubscribe from all channels
        for channel in self.subscribed_channels:
            await self.channel_layer.group_discard(
                channel,
                self.channel_name
            )
        if hasattr(self, 'revocation_group'):
            await self.channel_layer.group_discard(
                self.revocation_group,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'subscribe':
                channel = data.get('channel')
                if channel:
                    await self.subscribe_to_channel(channel)

            elif message_type == 'unsubscribe':
                channel = data.get('channel')
                if channel:
                    await self.unsubscribe_from_channel(channel)

            elif message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def subscribe_to_channel(self, channel):
        """Subscribe to a channel with strict tenant and ID validation"""
        is_allowed, reason = await self.verify_channel_access(channel)
        if not is_allowed:
            await self.send(text_data=json.dumps({
                'type': 'subscription_error',
                'channel': channel,
                'error': reason
            }))
            return

        if channel not in self.subscribed_channels:
            self.subscribed_channels.add(channel)
            await self.channel_layer.group_add(
                channel,
                self.channel_name
            )
            await self.send(text_data=json.dumps({
                'type': 'subscribed',
                'channel': channel
            }))

    async def unsubscribe_from_channel(self, channel):
        """Unsubscribe from a channel"""
        if channel in self.subscribed_channels:
            self.subscribed_channels.remove(channel)
            await self.channel_layer.group_discard(
                channel,
                self.channel_name
            )
            await self.send(text_data=json.dumps({
                'type': 'unsubscribed',
                'channel': channel
            }))

    # Message handlers for different channels
    async def notification_update(self, event):
        """Send notification update"""
        await self.send(text_data=json.dumps({
            'type': event.get('message_type', 'notification'),
            'channel': 'notifications',
            **event.get('data', {})
        }))

    async def data_update(self, event):
        """Send data update"""
        await self.send(text_data=json.dumps({
            'type': 'data_update',
            'channel': event.get('channel', 'data'),
            **event
        }))

async def broadcast_activity(activity_data):
    """
    Broadcast activity to all connected users
    """
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        'activity_feed',
        {
            'type': 'activity_created',
            'activity': activity_data
        }
    )


async def send_notification_to_user(user_id, notification_data):
    """
    Send notification to user via WebSocket

    Usage:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user_id}',
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        )
    """
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f'notifications_{user_id}',
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )


class HealthCheckConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for health and liveness checks.
    Allows load balancers, container orchestration, and monitoring clients to verify WebSocket connectivity.
    """

    async def connect(self):
        channel_layer_ok = self.channel_layer is not None
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'health_status',
            'status': 'healthy' if channel_layer_ok else 'degraded',
            'service': 'websocket',
            'channel_layer': self.channel_layer.__class__.__name__ if channel_layer_ok else None,
        }))

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'echo',
                    'received': data
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
