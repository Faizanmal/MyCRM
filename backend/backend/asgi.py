"""
ASGI config for backend project with WebSocket support.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from core.routing import websocket_urlpatterns
from core.websocket_auth_middleware import JWTOrSessionAuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket handler with Session + JWT + Tenant resolution
    "websocket": JWTOrSessionAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
