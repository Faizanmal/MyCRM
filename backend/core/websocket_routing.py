"""
WebSocket URL routing for Django Channels
"""

from django.urls import re_path
from . import websocket_consumers

websocket_urlpatterns = [
    re_path(r'ws/crm/$', websocket_consumers.CRMNotificationConsumer.as_asgi()),
    re_path(r'ws/crm/(?P<room_name>\w+)/$', websocket_consumers.CRMNotificationConsumer.as_asgi()),
]
