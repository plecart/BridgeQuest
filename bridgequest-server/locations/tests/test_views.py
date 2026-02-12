"""
Tests pour les vues API du module Locations.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from games.models import Game, GameState, Player, PlayerRole
from locations.models import Position

User = get_user_model()


class LocationViewsTestCase(TestCase):
    """Tests pour les vues de positions."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
        )
        self.game = Game.objects.create(code="ABC123")
        self.player = Player.objects.create(
            game=self.game,
            user=self.user,
            is_admin=True,
            role=PlayerRole.HUMAN,
        )

    def _authenticate_client(self, user=None):
        """Authentifie le client avec l'utilisateur spécifié."""
        self.client.force_authenticate(user=user or self.user)

    def test_update_position_authenticated_success(self):
        """Test de mise à jour de position avec utilisateur authentifié."""
        self.game.state = GameState.DEPLOYMENT
        self.game.save()

        self._authenticate_client()
        response = self.client.post(
            "/api/locations/",
            {"game_id": self.game.id, "latitude": 48.8566, "longitude": 2.3522},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["player_id"], self.player.id)
        self.assertEqual(float(response.data["latitude"]), 48.8566)
        self.assertIn("recorded_at", response.data)

    def test_update_position_unauthenticated_forbidden(self):
        """Test de mise à jour sans authentification."""
        self.game.state = GameState.DEPLOYMENT
        self.game.save()

        response = self.client.post(
            "/api/locations/",
            {"game_id": self.game.id, "latitude": 48.8566, "longitude": 2.3522},
            format="json",
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_update_position_game_waiting_returns_error(self):
        """Test que la mise à jour en WAITING retourne une erreur."""
        self._authenticate_client()
        response = self.client.post(
            "/api/locations/",
            {"game_id": self.game.id, "latitude": 48.8566, "longitude": 2.3522},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_update_position_validation_error(self):
        """Test de validation des coordonnées."""
        self.game.state = GameState.DEPLOYMENT
        self.game.save()

        self._authenticate_client()
        response = self.client.post(
            "/api/locations/",
            {"game_id": self.game.id, "latitude": 999, "longitude": 2.3522},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GamePositionsViewTestCase(TestCase):
    """Tests pour GET /api/games/{id}/positions/."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
        )
        self.game = Game.objects.create(code="ABC123")
        self.player = Player.objects.create(
            game=self.game,
            user=self.user,
            is_admin=True,
            role=PlayerRole.HUMAN,
        )

    def _authenticate_client(self, user=None):
        """Authentifie le client."""
        self.client.force_authenticate(user=user or self.user)

    def test_game_positions_success(self):
        """Test de récupération des positions avec succès."""
        Position.objects.create(
            player=self.player,
            latitude=Decimal("48.8566"),
            longitude=Decimal("2.3522"),
        )

        self._authenticate_client()
        response = self.client.get(f"/api/games/{self.game.id}/positions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["player_id"], self.player.id)
        self.assertIn("user", response.data[0])
        self.assertEqual(
            float(response.data[0]["latitude"]),
            48.8566,
        )

    def test_game_positions_player_not_in_game_forbidden(self):
        """Test qu'un non-joueur ne peut pas voir les positions."""
        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
        )
        self._authenticate_client(other_user)
        response = self.client.get(f"/api/games/{self.game.id}/positions/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)
