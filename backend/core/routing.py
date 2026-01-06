"""
WebSocket Routing Configuration
"""
from django.urls import re_path

from core.consumers import ActivityFeedConsumer, NotificationConsumer, RealtimeConsumer

websocket_urlpatterns = [
    re_path(r'ws/realtime/$', RealtimeConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/activity/$', ActivityFeedConsumer.as_asgi()),
]
