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
