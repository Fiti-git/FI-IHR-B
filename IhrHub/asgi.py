"""
ASGI config for IhrHub project.

It exposes the ASGI callable as a module-level variable named ``application``.

Supports both HTTP and WebSocket via Django Channels.
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from chat.routing import websocket_urlpatterns  # 👈 add this import

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IhrHub.settings')

django.setup()

# Combine HTTP and WebSocket handling
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # existing Django views / APIs
    "websocket": AuthMiddlewareStack(  # new WebSocket handling
        URLRouter(websocket_urlpatterns)
    ),
})
