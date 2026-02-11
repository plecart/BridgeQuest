"""
Tests pour le service de diffusion WebSocket de la salle d'attente.
"""
from django.test import TestCase

from games.services import lobby_broadcast


class LobbyBroadcastTestCase(TestCase):
    """Tests pour lobby_broadcast."""

    def test_broadcast_game_started_does_not_raise(self):
        """Test que broadcast_game_started s'exécute sans erreur."""
        lobby_broadcast.broadcast_game_started(game_id=1)

    def test_broadcast_player_excluded_does_not_raise(self):
        """Test que broadcast_player_excluded s'exécute sans erreur."""
        payload = {"player_id": 1, "user_id": 1, "username": "test", "is_admin": False}
        lobby_broadcast.broadcast_player_excluded(game_id=1, player_payload=payload)

    def test_broadcast_admin_transferred_does_not_raise(self):
        """Test que broadcast_admin_transferred s'exécute sans erreur."""
        payload = {"player_id": 2, "user_id": 2, "username": "newadmin", "is_admin": True}
        lobby_broadcast.broadcast_admin_transferred(game_id=1, new_admin_payload=payload)

    def test_broadcast_game_deleted_does_not_raise(self):
        """Test que broadcast_game_deleted s'exécute sans erreur."""
        lobby_broadcast.broadcast_game_deleted(game_id=1)
