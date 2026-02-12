"""
Tests pour les services du module Games.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from games.models import Game, GameState, Player
from games.services import (
    create_game,
    generate_game_code,
    get_game_by_code,
    get_game_by_id,
    join_game,
    start_game,
)
from utils.exceptions import GameException, PlayerException

User = get_user_model()


class GameServiceTestCase(TestCase):
    """Base pour les tests du service game."""

    def _create_user(self, username="testuser", email="test@example.com"):
        """Crée un utilisateur de test."""
        return User.objects.create_user(username=username, email=email)


class GenerateGameCodeTestCase(GameServiceTestCase):
    """Tests pour generate_game_code."""

    def test_generate_game_code_returns_six_chars(self):
        """Test que le code généré fait 6 caractères."""
        # Act
        code = generate_game_code()

        # Assert
        self.assertEqual(len(code), 6)

    def test_generate_game_code_is_alphanumeric(self):
        """Test que le code est alphanumérique."""
        # Act
        code = generate_game_code()

        # Assert
        self.assertTrue(code.isalnum())
        self.assertEqual(code.upper(), code)

    def test_generate_game_code_uniqueness(self):
        """Test que les codes générés sont uniques."""
        # Act
        codes = {generate_game_code() for _ in range(100)}

        # Assert
        self.assertEqual(len(codes), 100)


class CreateGameTestCase(GameServiceTestCase):
    """Tests pour create_game."""

    def test_create_game_success(self):
        """Test de création réussie d'une partie."""
        # Arrange
        user = self._create_user()

        # Act
        game = create_game(user)

        # Assert
        self.assertIsNotNone(game)
        self.assertEqual(len(game.code), 6)
        self.assertEqual(game.state, GameState.WAITING)
        player = Player.objects.get(game=game, user=user)
        self.assertTrue(player.is_admin)
        self.assertEqual(Player.objects.filter(game=game).count(), 1)


class GetGameByIdTestCase(GameServiceTestCase):
    """Tests pour get_game_by_id."""

    def test_get_game_by_id_success(self):
        """Test de récupération réussie par ID."""
        # Arrange
        game = Game.objects.create(code="ABC123")

        # Act
        result = get_game_by_id(game.pk)

        # Assert
        self.assertEqual(result, game)

    def test_get_game_by_id_not_found_raises_exception(self):
        """Test qu'une partie inexistante lève GameException."""
        # Act & Assert
        with self.assertRaises(GameException):
            get_game_by_id(99999)


class GetGameByCodeTestCase(GameServiceTestCase):
    """Tests pour get_game_by_code."""

    def test_get_game_by_code_success(self):
        """Test de récupération réussie par code."""
        # Arrange
        game = Game.objects.create(code="XYZ789")

        # Act
        result = get_game_by_code("XYZ789")

        # Assert
        self.assertEqual(result, game)

    def test_get_game_by_code_case_insensitive(self):
        """Test que la recherche est insensible à la casse."""
        # Arrange
        game = Game.objects.create(code="ABC123")

        # Act
        result = get_game_by_code("abc123")

        # Assert
        self.assertEqual(result, game)

    def test_get_game_by_code_not_found_returns_none(self):
        """Test qu'un code inexistant retourne None."""
        # Act
        result = get_game_by_code("INVALID")

        # Assert
        self.assertIsNone(result)

    def test_get_game_by_code_empty_returns_none(self):
        """Test qu'un code vide retourne None."""
        # Act
        result = get_game_by_code("")

        # Assert
        self.assertIsNone(result)

    def test_get_game_by_code_invalid_length_returns_none(self):
        """Test qu'un code de longueur invalide retourne None."""
        # Act
        result = get_game_by_code("ABC")

        # Assert
        self.assertIsNone(result)


class JoinGameTestCase(GameServiceTestCase):
    """Tests pour join_game."""

    def test_join_game_success(self):
        """Test de jonction réussie à une partie."""
        # Arrange
        admin = self._create_user(username="admin")
        joiner = self._create_user(username="joiner", email="joiner@example.com")
        game = create_game(admin)

        # Act
        player = join_game(game.code, joiner)

        # Assert
        self.assertIsNotNone(player)
        self.assertEqual(player.user, joiner)
        self.assertEqual(player.game, game)
        self.assertFalse(player.is_admin)
        self.assertEqual(Player.objects.filter(game=game).count(), 2)

    def test_join_game_invalid_code_raises_exception(self):
        """Test qu'un code invalide lève GameException."""
        # Arrange
        user = self._create_user()

        # Act & Assert
        with self.assertRaises(GameException):
            join_game("INVALID", user)

    def test_join_game_already_in_game_raises_exception(self):
        """Test qu'un utilisateur déjà dans la partie lève PlayerException."""
        # Arrange
        user = self._create_user()
        game = create_game(user)

        # Act & Assert
        with self.assertRaises(PlayerException):
            join_game(game.code, user)

    def test_join_game_already_started_raises_exception(self):
        """Test qu'on ne peut pas rejoindre une partie commencée."""
        # Arrange
        admin = self._create_user()
        joiner = self._create_user(username="joiner", email="joiner@example.com")
        game = create_game(admin)
        game.state = GameState.IN_PROGRESS
        game.save()

        # Act & Assert
        with self.assertRaises(GameException):
            join_game(game.code, joiner)


class StartGameTestCase(GameServiceTestCase):
    """Tests pour start_game."""

    def test_start_game_success(self):
        """Test de lancement réussi par l'administrateur."""
        # Arrange
        admin = self._create_user()
        game = create_game(admin)

        # Act
        result = start_game(game.id, admin)

        # Assert
        self.assertEqual(result.state, GameState.DEPLOYMENT)

    def test_start_game_not_admin_raises_exception(self):
        """Test qu'un joueur non-admin lève PlayerException."""
        # Arrange
        admin = self._create_user()
        joiner = self._create_user(username="joiner", email="joiner@example.com")
        game = create_game(admin)
        join_game(game.code, joiner)

        # Act & Assert
        with self.assertRaises(PlayerException):
            start_game(game.id, joiner)

    def test_start_game_not_in_game_raises_exception(self):
        """Test qu'un utilisateur non présent dans la partie lève PlayerException."""
        # Arrange
        admin = self._create_user()
        outsider = self._create_user(username="outsider", email="out@example.com")
        game = create_game(admin)

        # Act & Assert
        with self.assertRaises(PlayerException):
            start_game(game.id, outsider)

    def test_start_game_already_started_raises_exception(self):
        """Test qu'on ne peut pas lancer une partie déjà commencée."""
        # Arrange
        admin = self._create_user()
        game = create_game(admin)
        game.state = GameState.DEPLOYMENT
        game.save()

        # Act & Assert
        with self.assertRaises(GameException):
            start_game(game.id, admin)

    def test_start_game_not_found_raises_exception(self):
        """Test qu'une partie inexistante lève GameException."""
        # Arrange
        user = self._create_user()

        # Act & Assert
        with self.assertRaises(GameException):
            start_game(99999, user)
