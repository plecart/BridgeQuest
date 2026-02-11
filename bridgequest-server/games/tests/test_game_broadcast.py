"""
Tests pour le service de diffusion WebSocket de la partie en cours.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from games.models import Game, Player, PlayerRole
from games.services import game_broadcast
from locations.models import Position

User = get_user_model()


class GameBroadcastTestCase(TestCase):
    """Tests pour game_broadcast."""

    def test_get_game_group_name(self):
        """Test du nom du groupe game."""
        self.assertEqual(game_broadcast.get_game_group_name(42), "game_42")

    def test_broadcast_position_updated_does_not_raise(self):
        """Test que broadcast_position_updated s'exécute sans erreur."""
        user = User.objects.create_user(username="test", email="test@example.com")
        game = Game.objects.create(name="Partie", code="ABC123")
        player = Player.objects.create(
            game=game, user=user, is_admin=True, role=PlayerRole.HUMAN
        )
        position = Position.objects.create(
            player=player,
            latitude=Decimal("48.8566"),
            longitude=Decimal("2.3522"),
        )
        game_broadcast.broadcast_position_updated(position)
