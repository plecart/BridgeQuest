"""
Tests pour le service de cycle de vie des parties.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from games.models import Game, GameSettings, GameState, Player
from games.services.lifecycle_service import (
    begin_deployment,
    begin_in_progress,
    finish_game,
)
from utils.exceptions import GameException

User = get_user_model()


class _LifecycleBaseTestCase(TestCase):
    """Base pour les tests du cycle de vie."""

    def _create_game_with_players(self, *, player_count=2):
        """Crée une partie WAITING avec N joueurs et ses settings."""
        game = Game.objects.create(code="LIFE01")
        GameSettings.objects.create(game=game)
        for i in range(player_count):
            user = User.objects.create_user(
                username=f"player{i}", email=f"player{i}@test.com",
            )
            Player.objects.create(
                game=game, user=user, is_admin=(i == 0),
            )
        return game


class BeginDeploymentTestCase(_LifecycleBaseTestCase):
    """Tests pour begin_deployment (WAITING -> DEPLOYMENT)."""

    def test_begin_deployment_success(self):
        """Test de transition WAITING -> DEPLOYMENT avec 2 joueurs."""
        # Arrange
        game = self._create_game_with_players(player_count=2)

        # Act
        begin_deployment(game)

        # Assert
        game.refresh_from_db()
        self.assertEqual(game.state, GameState.DEPLOYMENT)
        self.assertIsNotNone(game.deployment_ends_at)

    def test_begin_deployment_not_enough_players_raises(self):
        """Test qu'une partie avec 1 joueur ne peut pas demarrer."""
        # Arrange
        game = self._create_game_with_players(player_count=1)

        # Act & Assert
        with self.assertRaises(GameException):
            begin_deployment(game)

    def test_begin_deployment_wrong_state_raises(self):
        """Test qu'une partie non-WAITING ne peut pas lancer le deploiement."""
        # Arrange
        game = self._create_game_with_players(player_count=2)
        game.state = GameState.DEPLOYMENT
        game.save()

        # Act & Assert
        with self.assertRaises(GameException):
            begin_deployment(game)


class BeginInProgressTestCase(_LifecycleBaseTestCase):
    """Tests pour begin_in_progress (DEPLOYMENT -> IN_PROGRESS)."""

    def _prepare_deployment_game(self, player_count=2):
        """Cree une partie en DEPLOYMENT avec settings et joueurs."""
        game = self._create_game_with_players(player_count=player_count)
        begin_deployment(game)
        game.refresh_from_db()
        return game

    def test_begin_in_progress_success(self):
        """Test de transition DEPLOYMENT -> IN_PROGRESS."""
        # Arrange
        game = self._prepare_deployment_game()

        # Act
        begin_in_progress(game)

        # Assert
        game.refresh_from_db()
        self.assertEqual(game.state, GameState.IN_PROGRESS)
        self.assertIsNotNone(game.game_ends_at)

    def test_begin_in_progress_assigns_roles(self):
        """Test que begin_in_progress attribue les roles."""
        # Arrange
        game = self._prepare_deployment_game(player_count=4)

        # Act
        begin_in_progress(game)

        # Assert
        players = list(game.players.all())
        roles = {p.role for p in players}
        self.assertIn("SPIRIT", roles)
        self.assertIn("HUMAN", roles)

    def test_begin_in_progress_applies_deployment_scores(self):
        """Test que begin_in_progress persiste les scores de deploiement."""
        # Arrange
        game = self._prepare_deployment_game()

        # Act
        begin_in_progress(game)

        # Assert
        for player in game.players.all():
            self.assertGreater(player.score, 0)

    def test_begin_in_progress_wrong_state_raises(self):
        """Test qu'une partie non-DEPLOYMENT ne peut pas passer IN_PROGRESS."""
        # Arrange
        game = self._create_game_with_players(player_count=2)

        # Act & Assert
        with self.assertRaises(GameException):
            begin_in_progress(game)


class FinishGameTestCase(_LifecycleBaseTestCase):
    """Tests pour finish_game (IN_PROGRESS -> FINISHED)."""

    def _prepare_in_progress_game(self):
        """Cree une partie en IN_PROGRESS."""
        game = self._create_game_with_players(player_count=2)
        begin_deployment(game)
        game.refresh_from_db()
        begin_in_progress(game)
        game.refresh_from_db()
        return game

    def test_finish_game_success(self):
        """Test de transition IN_PROGRESS -> FINISHED."""
        # Arrange
        game = self._prepare_in_progress_game()

        # Act
        finish_game(game)

        # Assert
        game.refresh_from_db()
        self.assertEqual(game.state, GameState.FINISHED)

    def test_finish_game_wrong_state_raises(self):
        """Test qu'une partie non-IN_PROGRESS ne peut pas etre terminee."""
        # Arrange
        game = self._create_game_with_players(player_count=2)

        # Act & Assert
        with self.assertRaises(GameException):
            finish_game(game)
