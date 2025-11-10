import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# 1. Set the settings module environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IhrHub.settings")

# 2. This is the crucial part: Initialize the Django application.
# This loads the settings and prepares the app for use.
django.setup()

# 3. Now that Django is set up, we can safely import our app's code
# that depends on Django (like models, views, etc.).
from chat.middleware import TokenAuthMiddleware
import chat.routing

# 4. Define the application routing
application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": get_asgi_application(),

    # WebSocket chat handler
    "websocket": TokenAuthMiddleware(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})