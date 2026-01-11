"""
WebSocket Routing Configuration
"""
from django.urls import re_path

from core.consumers import ActivityFeedConsumer, NotificationConsumer, RealtimeConsumer
from realtime_collaboration.consumers import DocumentCollaborationConsumer

websocket_urlpatterns = [
    re_path(r'ws/realtime/$', RealtimeConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/activity/$', ActivityFeedConsumer.as_asgi()),
    # Real-time document collaboration
    re_path(r'ws/documents/(?P<document_id>[^/]+)/$', DocumentCollaborationConsumer.as_asgi()),
]
