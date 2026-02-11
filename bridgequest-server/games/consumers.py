"""
Consumers WebSocket pour le module Games.

Deux canaux distincts :
- LobbyConsumer : salle d'attente (phase WAITING)
- GameConsumer : partie en cours (phases DEPLOYMENT, IN_PROGRESS)
"""
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from games.models import Game, GameState, Player
from games.services.game_broadcast import get_game_group_name
from games.services.lobby_broadcast import get_lobby_group_name

# Codes de fermeture WebSocket
_WS_CLOSE_UNAUTHORIZED = 4001
_WS_CLOSE_NOT_IN_GAME = 4002
_WS_CLOSE_WRONG_CHANNEL = 4003


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

    def _player_payload_base(self):
        """Payload minimal du joueur (player_id, user_id, username)."""
        user = self.player.user
        return {
            "player_id": self.player.id,
            "user_id": user.id,
            "username": user.username or "",
        }

    async def _send_connected_message(self):
        """Envoie la confirmation de connexion au client."""
        await self.send_json({
            "type": "connected",
            "game_id": self.game_id,
            "player": self._player_payload(),
        })


class LobbyConsumer(_BaseGameConsumerMixin, AsyncJsonWebsocketConsumer):
    """
    Consumer WebSocket pour la salle d'attente d'une partie.

    Canal : ws/lobby/{game_id}/
    Groupe : lobby_{game_id}
    Phase : WAITING uniquement.
    Événements : player_joined, player_left, game_started.
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

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        self._joined_group = True
        await self.accept()
        await self._send_connected_message()
        await self._broadcast_player_joined()

    def _player_payload(self):
        """Construit le payload d'un joueur (lobby : inclut is_admin)."""
        return {**self._player_payload_base(), "is_admin": self.player.is_admin}

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

    async def disconnect(self, close_code):
        """Quitte le groupe et diffuse joueur quitte avant de se déconnecter."""
        if self._joined_group and hasattr(self, "player") and close_code not in (
            _WS_CLOSE_UNAUTHORIZED,
            _WS_CLOSE_NOT_IN_GAME,
            _WS_CLOSE_WRONG_CHANNEL,
        ):
            await self._broadcast_player_left()
        if self._joined_group:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

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

    async def receive_json(self, content):
        """Reçoit un message du client. Simple echo pour vérifier la connectivité."""
        await self.send_json({"type": "echo", "received": content})


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
        return self._player_payload_base()

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

    async def receive_json(self, content):
        """Reçoit un message du client. Echo pour vérifier la connectivité."""
        await self.send_json({"type": "echo", "received": content})
