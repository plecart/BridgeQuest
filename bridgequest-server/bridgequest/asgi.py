"""
ASGI config for Bridge Quest project.

Gère HTTP (Django) et WebSocket (Channels) via Daphne.
"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from bridgequest.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bridgequest.settings.development')

# Initialiser Django ASGI avant d'importer les modules qui utilisent les models
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns),
        ),
    ),
})
