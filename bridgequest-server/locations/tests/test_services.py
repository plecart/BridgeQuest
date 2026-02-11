"""
Tests pour les services du module Locations.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from games.models import Game, GameState, Player, PlayerRole
from locations.models import Position
from locations.services.position_service import (
    get_latest_positions_for_game,
    update_position,
)
from utils.exceptions import GameException, LocationException, PlayerException

User = get_user_model()


class PositionServiceTestCase(TestCase):
    """Tests pour le service de positions."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
        )
        self.game = Game.objects.create(name="Partie", code="ABC123")
        self.player = Player.objects.create(
            game=self.game,
            user=self.user,
            is_admin=True,
            role=PlayerRole.HUMAN,
        )

    def test_update_position_success(self):
        """Test de mise à jour réussie en phase DEPLOYMENT."""
        self.game.state = GameState.DEPLOYMENT
        self.game.save()

        position = update_position(
            game_id=self.game.id,
            user=self.user,
            latitude=48.8566,
            longitude=2.3522,
        )

        self.assertIsNotNone(position.id)
        self.assertEqual(position.player, self.player)
        self.assertEqual(float(position.latitude), 48.8566)
        self.assertEqual(float(position.longitude), 2.3522)
        self.assertEqual(Position.objects.filter(player=self.player).count(), 1)

    def test_update_position_in_progress(self):
        """Test de mise à jour en phase IN_PROGRESS."""
        self.game.state = GameState.IN_PROGRESS
        self.game.save()

        position = update_position(
            game_id=self.game.id,
            user=self.user,
            latitude=-33.8688,
            longitude=151.2093,
        )
        self.assertIsNotNone(position.id)

    def test_update_position_game_waiting_raises_exception(self):
        """Test que la mise à jour en WAITING lève une exception."""
        with self.assertRaises(LocationException) as ctx:
            update_position(
                game_id=self.game.id,
                user=self.user,
                latitude=48.8566,
                longitude=2.3522,
            )
        self.assertIsNotNone(ctx.exception)

    def test_update_position_game_finished_raises_exception(self):
        """Test que la mise à jour en FINISHED lève une exception."""
        self.game.state = GameState.FINISHED
        self.game.save()

        with self.assertRaises(LocationException):
            update_position(
                game_id=self.game.id,
                user=self.user,
                latitude=48.8566,
                longitude=2.3522,
            )

    def test_update_position_player_not_in_game_raises_exception(self):
        """Test que la mise à jour par un non-joueur lève une exception."""
        self.game.state = GameState.DEPLOYMENT
        self.game.save()

        with self.assertRaises(PlayerException):
            update_position(
                game_id=self.game.id,
                user=self.other_user,
                latitude=48.8566,
                longitude=2.3522,
            )

    def test_update_position_game_not_found_raises_exception(self):
        """Test que la mise à jour avec partie inexistante lève une exception."""
        self.game.state = GameState.DEPLOYMENT
        self.game.save()

        with self.assertRaises(GameException):
            update_position(
                game_id=99999,
                user=self.user,
                latitude=48.8566,
                longitude=2.3522,
            )

    def test_update_position_invalid_coordinates_raises_exception(self):
        """Test que des coordonnées invalides lèvent une exception."""
        self.game.state = GameState.DEPLOYMENT
        self.game.save()

        with self.assertRaises(LocationException):
            update_position(
                game_id=self.game.id,
                user=self.user,
                latitude=100,  # Invalide (> 90)
                longitude=2.3522,
            )

    def test_get_latest_positions_for_game_empty(self):
        """Test sans position enregistrée."""
        positions = get_latest_positions_for_game(self.game)
        self.assertEqual(positions, [])

    def test_get_latest_positions_for_game_single(self):
        """Test avec une position par joueur."""
        Position.objects.create(
            player=self.player,
            latitude=Decimal("48.8566"),
            longitude=Decimal("2.3522"),
        )
        positions = get_latest_positions_for_game(self.game)
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].player, self.player)

    def test_get_latest_positions_for_game_returns_latest_only(self):
        """Test que seule la dernière position par joueur est retournée."""
        from django.utils import timezone

        p1 = Position.objects.create(
            player=self.player,
            latitude=Decimal("1"),
            longitude=Decimal("1"),
        )
        p2 = Position.objects.create(
            player=self.player,
            latitude=Decimal("48.8566"),
            longitude=Decimal("2.3522"),
        )
        p1.recorded_at = timezone.now() - timezone.timedelta(seconds=10)
        p1.save(update_fields=["recorded_at"])
        positions = get_latest_positions_for_game(self.game)
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].latitude, Decimal("48.8566"))
