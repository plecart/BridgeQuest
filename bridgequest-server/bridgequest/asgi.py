"""
ASGI config for Bridge Quest project.

Gère HTTP (Django) et WebSocket (Channels) via Daphne.

Authentification WebSocket :
- Session Django (cookies) pour le web
- JWT via query string (?token=xxx) pour mobile Flutter
"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bridgequest.settings.development')

# Initialiser Django ASGI avant d'importer les modules qui utilisent les models
django_asgi_app = get_asgi_application()

from accounts.websocket_auth import JWTAuthMiddleware
from bridgequest.routing import websocket_urlpatterns

# WebSocket : AuthMiddlewareStack (session) puis JWTAuthMiddleware (JWT en ?token=xxx remplace si présent)
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            JWTAuthMiddleware(
                URLRouter(websocket_urlpatterns),
            ),
        ),
    ),
})
