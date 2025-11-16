"""
WebSocket Routing Configuration
"""
from django.urls import re_path
from core.consumers import NotificationConsumer, ActivityFeedConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/activity/$', ActivityFeedConsumer.as_asgi()),
]
