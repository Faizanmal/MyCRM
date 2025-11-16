"""
Real-time WebSocket Notifications
Django Channels consumer for live notifications
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Join user-specific notification group
        self.user_group_name = f'notifications_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to notification stream'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
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
    WebSocket consumer for real-time activity feed updates
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Join activity feed group
        self.feed_group_name = 'activity_feed'
        
        await self.channel_layer.group_add(
            self.feed_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        await self.channel_layer.group_discard(
            self.feed_group_name,
            self.channel_name
        )
    
    async def activity_created(self, event):
        """Send new activity to feed"""
        await self.send(text_data=json.dumps({
            'type': 'activity_created',
            'activity': event['activity']
        }))


# Utility function to send notifications via WebSocket
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
