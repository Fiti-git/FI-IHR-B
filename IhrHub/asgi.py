import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack # Keep this if you also use session auth
import chat.routing
from chat.middleware import TokenAuthMiddleware # 🟢 IMPORT YOUR NEW MIDDLEWARE

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware( # 🟢 WRAP YOUR URLRouter
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})