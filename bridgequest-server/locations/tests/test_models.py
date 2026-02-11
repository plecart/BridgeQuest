"""
Tests pour les modèles du module Locations.
"""
from decimal import Decimal

from django.test import TestCase

from games.models import Game, Player, PlayerRole
from locations.models import Position

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class PositionModelTestCase(TestCase):
    """Tests pour le modèle Position."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
        )
        self.game = Game.objects.create(name="Partie test", code="ABC123")
        self.player = Player.objects.create(
            game=self.game,
            user=self.user,
            is_admin=True,
            role=PlayerRole.HUMAN,
        )

    def test_create_position_success(self):
        """Test de création réussie d'une position."""
        position = Position.objects.create(
            player=self.player,
            latitude=Decimal("48.8566"),
            longitude=Decimal("2.3522"),
        )
        self.assertIsNotNone(position.id)
        self.assertEqual(position.player, self.player)
        self.assertEqual(position.latitude, Decimal("48.8566"))
        self.assertEqual(position.longitude, Decimal("2.3522"))
        self.assertIsNotNone(position.recorded_at)

    def test_position_str_representation(self):
        """Test de la représentation string de la position."""
        position = Position.objects.create(
            player=self.player,
            latitude=Decimal("48.8566"),
            longitude=Decimal("2.3522"),
        )
        self.assertIn("48.8566", str(position))
        self.assertIn("2.3522", str(position))

    def test_position_ordering(self):
        """Test que les positions sont triées par recorded_at décroissant."""
        from django.utils import timezone

        p1 = Position.objects.create(
            player=self.player,
            latitude=Decimal("1"),
            longitude=Decimal("1"),
        )
        p2 = Position.objects.create(
            player=self.player,
            latitude=Decimal("2"),
            longitude=Decimal("2"),
        )
        p1.recorded_at = timezone.now() - timezone.timedelta(seconds=10)
        p1.save(update_fields=["recorded_at"])
        positions = list(Position.objects.all())
        self.assertEqual(len(positions), 2)
        self.assertEqual(positions[0].latitude, Decimal("2"))
        self.assertEqual(positions[1].latitude, Decimal("1"))
