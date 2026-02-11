"""
Consumers WebSocket pour le module Games.

Ce fichier contient les consumers Django Channels pour la synchronisation
temps réel (salle d'attente, positions, événements).
"""
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class LobbyConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer WebSocket pour la salle d'attente d'une partie.

    Groupe : lobby_{game_id}
    Diffusion des événements : joueur rejoint, joueur quitte, partie lancée.

    L'authentification et la logique métier seront implémentées à l'étape 5.
    """

    async def connect(self):
        """Accepte la connexion et rejoint le groupe de la partie."""
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f'lobby_{self.game_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()
        await self._send_connected_message()

    async def _send_connected_message(self):
        """Envoie la confirmation de connexion au client."""
        await self.send_json({
            'type': 'connected',
            'game_id': self.game_id,
        })

    async def disconnect(self, close_code):
        """Quitte le groupe à la déconnexion."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive_json(self, content):
        """
        Reçoit un message du client.

        Pour l'instant, simple echo pour vérifier la connectivité.
        La logique métier sera ajoutée à l'étape 5.
        """
        await self._send_echo_message(content)

    async def _send_echo_message(self, content):
        """Renvoie le message reçu (echo) au client."""
        await self.send_json({
            'type': 'echo',
            'received': content,
        })
