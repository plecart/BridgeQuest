"""
Consumers WebSocket pour le module Games.

Ce fichier contient les consumers Django Channels pour la synchronisation
temps réel (salle d'attente, positions, événements).
"""
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from games.models import Player
from games.services.lobby_broadcast import get_lobby_group_name


class LobbyConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer WebSocket pour la salle d'attente d'une partie.

    Groupe : lobby_{game_id}
    Événements diffusés : player_joined, player_left, game_started.
    """

    async def connect(self):
        """Accepte la connexion si l'utilisateur est authentifié et dans la partie."""
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.room_group_name = get_lobby_group_name(self.game_id)
        self._joined_group = False
        self.user = self.scope.get("user")

        if isinstance(self.user, AnonymousUser) or not self.user:
            await self.close(code=4001)
            return

        player = await self._get_player_in_game()
        if player is None:
            await self.close(code=4002)
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

    def _player_payload(self):
        """Construit le payload minimal d'un joueur pour les événements."""
        user = self.player.user
        return {
            "player_id": self.player.id,
            "user_id": user.id,
            "username": user.username or "",
            "is_admin": self.player.is_admin,
        }

    async def _send_connected_message(self):
        """Envoie la confirmation de connexion au client."""
        await self.send_json({
            "type": "connected",
            "game_id": self.game_id,
            "player": self._player_payload(),
        })

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
        if self._joined_group and hasattr(self, "player") and close_code not in (4001, 4002):
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

    async def _forward_to_client(self, event_type, payload):
        """Transmet un événement du groupe au client WebSocket."""
        await self.send_json({"type": event_type, **payload})

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
        """
        Reçoit un message du client.

        Pour l'instant, simple echo pour vérifier la connectivité.
        """
        await self.send_json({
            "type": "echo",
            "received": content,
        })
