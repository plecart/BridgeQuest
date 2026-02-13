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
        game = Game.objects.create(code="ABC123")
        player = Player.objects.create(
            game=game, user=user, is_admin=True, role=PlayerRole.HUMAN
        )
        position = Position.objects.create(
            player=player,
            latitude=Decimal("48.8566"),
            longitude=Decimal("2.3522"),
        )
        game_broadcast.broadcast_position_updated(position)

    def test_broadcast_roles_assigned_does_not_raise(self):
        """Test que broadcast_roles_assigned s'exécute sans erreur."""
        roles_data = [
            {"player_id": 1, "user_id": 1, "username": "p1", "role": "HUMAN"},
            {"player_id": 2, "user_id": 2, "username": "p2", "role": "SPIRIT"},
        ]
        game_broadcast.broadcast_roles_assigned(game_id=1, roles_data=roles_data)

    def test_broadcast_game_in_progress_does_not_raise(self):
        """Test que broadcast_game_in_progress s'exécute sans erreur."""
        game_broadcast.broadcast_game_in_progress(
            game_id=1, game_ends_at="2026-01-01T00:30:00Z",
        )

    def test_broadcast_game_finished_does_not_raise(self):
        """Test que broadcast_game_finished s'exécute sans erreur."""
        scores_data = [
            {"player_id": 1, "username": "p1", "role": "HUMAN", "score": 100},
        ]
        game_broadcast.broadcast_game_finished(game_id=1, scores_data=scores_data)
