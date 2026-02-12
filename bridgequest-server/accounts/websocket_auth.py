"""
Authentification JWT pour les connexions WebSocket.

Permet aux clients mobiles (Flutter) d'authentifier les connexions WebSocket
via un token JWT passé en paramètre de requête (?token=...).

S'exécute après AuthMiddlewareStack : si un token JWT valide est présent,
il remplace l'utilisateur de session (priorité mobile).
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


def _extract_token_from_scope(scope):
    """Extrait le token JWT de la query string du scope."""
    query_string = scope.get("query_string", b"").decode()
    params = parse_qs(query_string)
    token_list = params.get("token", [])
    if not token_list:
        return None
    token = token_list[0].strip()
    return token if token else None


@database_sync_to_async
def _get_user_from_token(token):
    """Valide le token JWT et retourne l'utilisateur ou None."""
    try:
        validated = AccessToken(token)
        user_id = validated.get("user_id")
        if not user_id:
            return None
        return User.objects.get(pk=user_id)
    except (InvalidToken, TokenError, User.DoesNotExist):
        return None


class JWTAuthMiddleware:
    """
    Middleware d'authentification JWT pour WebSocket.

    Lit le token depuis la query string (?token=xxx). Si valide, remplace
    scope["user"] par l'utilisateur JWT (priorité sur la session Django).
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        token = _extract_token_from_scope(scope)
        if token:
            user = await _get_user_from_token(token)
            if user is not None:
                scope["user"] = user
        return await self.app(scope, receive, send)
