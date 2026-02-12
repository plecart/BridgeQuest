"""
Consumers WebSocket pour le module Games.

Deux canaux distincts :
- LobbyConsumer : salle d'attente (phase WAITING)
- GameConsumer : partie en cours (phases DEPLOYMENT, IN_PROGRESS)
"""
import asyncio

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from games.models import Game, GameState, Player
from games.services.game_broadcast import get_game_group_name
from games.services.lobby_broadcast import get_lobby_group_name
from games.services.lobby_service import (
    LOBBY_DISCONNECT_GRACE_SECONDS,
    cancel_pending_exclusion,
    exclude_player_after_timeout,
    exclude_player_immediately,
    mark_player_disconnected,
)
from games.services.player_payload import build_player_websocket_payload

# Codes de fermeture WebSocket
_WS_CLOSE_UNAUTHORIZED = 4001
_WS_CLOSE_NOT_IN_GAME = 4002
_WS_CLOSE_WRONG_CHANNEL = 4003

# Message client : sortie volontaire → exclusion immédiate (sans délai 30 s)
_WS_MESSAGE_LEAVE = "leave"

_CLOSE_CODES_SKIP_EXCLUSION = (
    _WS_CLOSE_UNAUTHORIZED,
    _WS_CLOSE_NOT_IN_GAME,
    _WS_CLOSE_WRONG_CHANNEL,
)


class _BaseGameConsumerMixin:
    """
    Mixin partagé pour LobbyConsumer et GameConsumer.

    Fournit les méthodes communes d'authentification et de sérialisation.
    """

    @database_sync_to_async
    def _get_player_in_game(self):
        """Récupère le joueur dans la partie, ou None si absent."""
        try:
            return Player.objects.select_related("user").get(
                user=self.user,
                game_id=self.game_id,
            )
        except Player.DoesNotExist:
            return None

    @database_sync_to_async
    def _get_game(self):
        """Récupère la partie."""
        return Game.objects.get(pk=self.game_id)

    async def _forward_to_client(self, event_type, payload):
        """Transmet un événement du groupe au client WebSocket."""
        await self.send_json({"type": event_type, **payload})

    async def _send_connected_message(self):
        """Envoie la confirmation de connexion au client."""
        await self.send_json({
            "type": "connected",
            "game_id": self.game_id,
            "player": self._player_payload(),
        })

    async def receive_json(self, content):
        """Reçoit un message du client. Echo pour vérifier la connectivité."""
        await self.send_json({"type": "echo", "received": content})


class LobbyConsumer(_BaseGameConsumerMixin, AsyncJsonWebsocketConsumer):
    """
    Consumer WebSocket pour la salle d'attente d'une partie.

    Canal : ws/lobby/{game_id}/
    Groupe : lobby_{game_id}
    Phase : WAITING uniquement.
    Événements : player_joined, player_left, player_excluded, admin_transferred,
                 game_deleted, game_started.
    Codes de fermeture : 4001 (non authentifié), 4002 (non dans la partie),
                        4003 (partie déjà commencée, utiliser ws/game/).
    """

    async def connect(self):
        """Accepte la connexion si l'utilisateur est authentifié et dans la partie."""
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.room_group_name = get_lobby_group_name(self.game_id)
        self._joined_group = False
        self.user = self.scope.get("user")

        if isinstance(self.user, AnonymousUser) or not self.user:
            await self.close(code=_WS_CLOSE_UNAUTHORIZED)
            return

        player = await self._get_player_in_game()
        if player is None:
            await self.close(code=_WS_CLOSE_NOT_IN_GAME)
            return

        game = await self._get_game()
        if game.state != GameState.WAITING:
            await self.close(code=_WS_CLOSE_WRONG_CHANNEL)
            return

        self.player = player
        self._voluntarily_left = False

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        self._joined_group = True
        cancel_pending_exclusion(self.game_id, self.player.id)
        await self.accept()
        await self._send_connected_message()
        await self._broadcast_player_joined()

    def _player_payload(self):
        """Construit le payload d'un joueur (lobby : inclut is_admin)."""
        return build_player_websocket_payload(self.player, include_admin=True)

    async def _broadcast_player_joined(self):
        """Diffuse l'événement joueur rejoint au groupe."""
        payload = self._player_payload()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "player_joined",
                "player": payload,
            },
        )

    def _is_voluntary_leave_message(self, content):
        """Vérifie si le message indique une sortie volontaire."""
        return isinstance(content, dict) and content.get("type") == _WS_MESSAGE_LEAVE

    async def _handle_voluntary_leave(self):
        """Exclut immédiatement le joueur (sortie volontaire, sans délai 30 s)."""
        self._voluntarily_left = True
        await database_sync_to_async(exclude_player_immediately)(
            self.game_id, self.player.id,
        )

    async def receive_json(self, content):
        """Gère les messages client : leave (sortie volontaire) ou echo."""
        if self._is_voluntary_leave_message(content):
            await self._handle_voluntary_leave()
        else:
            await super().receive_json(content)

    def _should_schedule_exclusion(self, close_code):
        """Indique si une déconnexion doit déclencher le délai d'exclusion (30 s)."""
        return (
            self._joined_group
            and hasattr(self, "player")
            and close_code not in _CLOSE_CODES_SKIP_EXCLUSION
            and not getattr(self, "_voluntarily_left", False)
        )

    async def disconnect(self, close_code):
        """Quitte le groupe, diffuse joueur quitte et planifie exclusion si délai dépassé."""
        if self._should_schedule_exclusion(close_code):
            await self._broadcast_player_left()
            await self._schedule_player_exclusion()
        if self._joined_group:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def _schedule_player_exclusion(self):
        """
        Planifie l'exclusion du joueur après le délai de grâce (30 s).

        Si le joueur se reconnecte avant, cancel_pending_exclusion annule.
        """
        game_id = self.game_id
        player_id = self.player.id

        mark_player_disconnected(game_id, player_id)
        asyncio.create_task(self._run_delayed_exclusion(game_id, player_id))

    async def _run_delayed_exclusion(self, game_id, player_id):
        """Exécute l'exclusion après le délai de grâce."""
        await asyncio.sleep(LOBBY_DISCONNECT_GRACE_SECONDS)
        await database_sync_to_async(exclude_player_after_timeout)(game_id, player_id)

    async def _broadcast_player_left(self):
        """Diffuse l'événement joueur quitte au groupe."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "player_left",
                "player": self._player_payload(),
            },
        )

    async def player_joined(self, event):
        """Reçoit player_joined du groupe et transmet au client."""
        await self._forward_to_client("player_joined", {"player": event["player"]})

    async def player_left(self, event):
        """Reçoit player_left du groupe et transmet au client."""
        await self._forward_to_client("player_left", {"player": event["player"]})

    async def game_started(self, event):
        """Reçoit game_started du groupe et transmet au client."""
        await self._forward_to_client("game_started", {
            "game_id": event["game_id"],
            "state": event["state"],
        })

    async def player_excluded(self, event):
        """Reçoit player_excluded du groupe et transmet au client."""
        await self._forward_to_client("player_excluded", {"player": event["player"]})

    async def admin_transferred(self, event):
        """Reçoit admin_transferred du groupe et transmet au client."""
        await self._forward_to_client(
            "admin_transferred", {"new_admin": event["new_admin"]}
        )

    async def game_deleted(self, event):
        """Reçoit game_deleted du groupe et transmet au client."""
        await self._forward_to_client("game_deleted", {
            "game_id": event["game_id"],
        })


class GameConsumer(_BaseGameConsumerMixin, AsyncJsonWebsocketConsumer):
    """
    Consumer WebSocket pour la partie en cours.

    Canal : ws/game/{game_id}/
    Groupe : game_{game_id}
    Phases : DEPLOYMENT, IN_PROGRESS uniquement.
    Événements : position_updated (et futurs : conversion, score, etc.).
    Codes de fermeture : 4001 (non authentifié), 4002 (non dans la partie),
                        4003 (partie en attente ou terminée).
    """

    async def connect(self):
        """Accepte la connexion si l'utilisateur est dans la partie et le jeu actif."""
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.room_group_name = get_game_group_name(self.game_id)
        self._joined_group = False
        self.user = self.scope.get("user")

        if isinstance(self.user, AnonymousUser) or not self.user:
            await self.close(code=_WS_CLOSE_UNAUTHORIZED)
            return

        player = await self._get_player_in_game()
        if player is None:
            await self.close(code=_WS_CLOSE_NOT_IN_GAME)
            return

        game = await self._get_game()
        if game.state not in (GameState.DEPLOYMENT, GameState.IN_PROGRESS):
            await self.close(code=_WS_CLOSE_WRONG_CHANNEL)
            return

        self.player = player

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        self._joined_group = True
        await self.accept()
        await self._send_connected_message()

    def _player_payload(self):
        """Construit le payload minimal du joueur (game : sans is_admin)."""
        return build_player_websocket_payload(self.player, include_admin=False)

    async def disconnect(self, close_code):
        """Quitte le groupe à la déconnexion."""
        if self._joined_group:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def position_updated(self, event):
        """Reçoit position_updated du groupe et transmet au client."""
        payload = {k: v for k, v in event.items() if k != "type"}
        await self._forward_to_client("position_updated", payload)
