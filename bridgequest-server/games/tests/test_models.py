"""
Tests pour les modèles du module Games.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from games.models import Game, GameState, Player, PlayerRole

User = get_user_model()

# Données de test réutilisables
_GAME_CODE = "GAME01"
_GAME_CODE_ALT = "GAME02"


class GameModelTestCase(TestCase):
    """Tests pour le modèle Game."""

    def test_create_game_success(self):
        """Test de création réussie d'une partie."""
        # Arrange
        code = "ABC123"

        # Act
        game = Game.objects.create(code=code)

        # Assert
        self.assertIsNotNone(game)
        self.assertEqual(game.code, code)
        self.assertEqual(game.state, GameState.WAITING)
        self.assertIsNotNone(game.created_at)
        self.assertIsNotNone(game.updated_at)

    def test_game_str_representation(self):
        """Test de la représentation string d'une partie."""
        # Arrange & Act
        game = Game.objects.create(code="XYZ789")

        # Assert
        self.assertEqual(str(game), "XYZ789")

    def test_game_default_state_is_waiting(self):
        """Test que l'état par défaut est WAITING."""
        # Arrange & Act
        game = Game.objects.create(code="CODE12")

        # Assert
        self.assertEqual(game.state, GameState.WAITING)

    def test_game_code_unique_raises_integrity_error(self):
        """Test que le code doit être unique."""
        # Arrange
        Game.objects.create(code="UNIQUE")

        # Act & Assert
        with self.assertRaises(IntegrityError):
            Game.objects.create(code="UNIQUE")

    def test_game_code_validation_alphanumeric(self):
        """Test que le code doit être alphanumérique."""
        # Arrange & Act & Assert
        game = Game(code="AB-123")
        with self.assertRaises(ValidationError):
            game.full_clean()

    def test_game_code_validation_length(self):
        """Test que le code doit faire 6 caractères."""
        # Arrange & Act & Assert
        game = Game(code="ABC12")
        with self.assertRaises(ValidationError):
            game.full_clean()


class PlayerModelTestCase(TestCase):
    """Tests pour le modèle Player."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
        )
        self.game = Game.objects.create(code=_GAME_CODE)

    def test_create_player_success(self):
        """Test de création réussie d'un joueur."""
        # Act
        player = Player.objects.create(
            user=self.user,
            game=self.game,
            is_admin=True,
        )

        # Assert
        self.assertIsNotNone(player)
        self.assertEqual(player.user, self.user)
        self.assertEqual(player.game, self.game)
        self.assertTrue(player.is_admin)
        self.assertEqual(player.role, PlayerRole.HUMAN)
        self.assertEqual(player.score, 0)
        self.assertIsNotNone(player.joined_at)

    def test_player_str_representation(self):
        """Test de la représentation string d'un joueur."""
        # Arrange & Act
        player = Player.objects.create(user=self.user, game=self.game)

        # Assert
        self.assertIn("testuser", str(player))
        self.assertIn(_GAME_CODE, str(player))

    def test_player_unique_per_game_raises_integrity_error(self):
        """Test qu'un utilisateur ne peut être qu'une fois dans une partie."""
        # Arrange
        Player.objects.create(user=self.user, game=self.game)

        # Act & Assert
        with self.assertRaises(IntegrityError):
            Player.objects.create(user=self.user, game=self.game)

    def test_player_can_join_multiple_games(self):
        """Test qu'un utilisateur peut rejoindre plusieurs parties."""
        # Arrange
        game2 = Game.objects.create(code=_GAME_CODE_ALT)

        # Act
        player1 = Player.objects.create(user=self.user, game=self.game)
        player2 = Player.objects.create(user=self.user, game=game2)

        # Assert
        self.assertNotEqual(player1, player2)
        self.assertEqual(Player.objects.filter(user=self.user).count(), 2)
