"""
Tests pour le service de calcul des scores.
"""
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from games.models import Game, GameSettings, GameState, Player, PlayerRole
from games.services.score_service import (
    _compute_human_minutes,
    _compute_passive_score,
    apply_deployment_scores,
    calculate_final_scores,
)

User = get_user_model()


class ComputePassiveScoreTestCase(TestCase):
    """Tests pour _compute_passive_score."""

    def test_ten_minutes_ten_points(self):
        """10 minutes * 10 pts/min = 100."""
        self.assertEqual(_compute_passive_score(10.0, 10), 100)

    def test_zero_minutes_returns_zero(self):
        """0 minutes = 0 points."""
        self.assertEqual(_compute_passive_score(0.0, 10), 0)

    def test_fractional_minutes_rounds(self):
        """Les minutes fractionnaires sont arrondies."""
        self.assertEqual(_compute_passive_score(1.5, 10), 15)


class ComputeHumanMinutesTestCase(TestCase):
    """Tests pour _compute_human_minutes."""

    def setUp(self):
        """Configuration initiale."""
        self.user = User.objects.create_user(
            username="timeuser", email="time@test.com",
        )
        self.game = Game.objects.create(code="TIME01")
        self.game_start = timezone.now()
        self.game_end = self.game_start + datetime.timedelta(minutes=30)

    def test_human_gets_full_duration(self):
        """Un humain non converti recoit la duree complete."""
        # Arrange
        player = Player.objects.create(
            game=self.game, user=self.user, role=PlayerRole.HUMAN,
        )

        # Act
        minutes = _compute_human_minutes(player, self.game_start, self.game_end)

        # Assert
        self.assertAlmostEqual(minutes, 30.0, places=1)

    def test_spirit_gets_zero(self):
        """Un esprit initial ne recoit aucune minute."""
        # Arrange
        player = Player.objects.create(
            game=self.game, user=self.user, role=PlayerRole.SPIRIT,
        )

        # Act
        minutes = _compute_human_minutes(player, self.game_start, self.game_end)

        # Assert
        self.assertEqual(minutes, 0.0)

    def test_converted_spirit_gets_zero(self):
        """Un humain converti en esprit ne recoit aucune minute."""
        # Arrange
        player = Player.objects.create(
            game=self.game, user=self.user, role=PlayerRole.SPIRIT,
            converted_at=self.game_start + datetime.timedelta(minutes=10),
        )

        # Act
        minutes = _compute_human_minutes(player, self.game_start, self.game_end)

        # Assert
        self.assertEqual(minutes, 0.0)


class ApplyDeploymentScoresTestCase(TestCase):
    """Tests pour apply_deployment_scores."""

    def _create_game_with_players(self, player_count=2):
        """Cree une partie avec settings et joueurs."""
        game = Game.objects.create(code="DEPL01")
        GameSettings.objects.create(
            game=game, deployment_duration=5, points_per_minute=10,
        )
        for i in range(player_count):
            user = User.objects.create_user(
                username=f"depluser{i}", email=f"depl{i}@test.com",
            )
            Player.objects.create(game=game, user=user, is_admin=(i == 0))
        return game

    def test_all_players_receive_deployment_points(self):
        """Tous les joueurs recoivent les memes points de deploiement."""
        # Arrange
        game = self._create_game_with_players(3)
        expected = round(5 * 10)  # deployment_duration * points_per_minute

        # Act
        apply_deployment_scores(game)

        # Assert
        for player in Player.objects.filter(game=game):
            self.assertEqual(player.score, expected)

    def test_zero_duration_no_update(self):
        """Aucun point si la duree de deploiement est 0."""
        # Arrange
        game = self._create_game_with_players(2)
        game.settings.deployment_duration = 0
        game.settings.save()

        # Act
        apply_deployment_scores(game)

        # Assert
        for player in Player.objects.filter(game=game):
            self.assertEqual(player.score, 0)

    def test_scores_are_additive(self):
        """Les points s'ajoutent au score existant."""
        # Arrange
        game = self._create_game_with_players(1)
        player = Player.objects.filter(game=game).first()
        player.score = 100
        player.save()

        # Act
        apply_deployment_scores(game)

        # Assert
        player.refresh_from_db()
        self.assertEqual(player.score, 100 + round(5 * 10))


class CalculateFinalScoresTestCase(TestCase):
    """Tests pour calculate_final_scores."""

    def _create_in_progress_game(self):
        """
        Cree une partie IN_PROGRESS dont le timer vient d'expirer.

        game_ends_at = now (fin de partie), donc le debut de IN_PROGRESS
        = now - game_duration, ce qui donne une duree complete de jeu.
        """
        game = Game.objects.create(
            code="FINAL1",
            state=GameState.IN_PROGRESS,
        )
        GameSettings.objects.create(
            game=game, game_duration=30, points_per_minute=10,
        )
        game.game_ends_at = timezone.now()
        game.save()
        return game

    def test_humans_receive_passive_points(self):
        """Les humains recoivent des points passifs pour IN_PROGRESS."""
        # Arrange
        game = self._create_in_progress_game()
        user = User.objects.create_user(username="human1", email="h1@test.com")
        Player.objects.create(
            game=game, user=user, role=PlayerRole.HUMAN, score=0,
        )

        # Act
        scores = calculate_final_scores(game)

        # Assert
        self.assertEqual(len(scores), 1)
        self.assertGreater(scores[0]["score"], 0)

    def test_spirits_no_passive_points(self):
        """Les esprits ne recoivent pas de points passifs."""
        # Arrange
        game = self._create_in_progress_game()
        user = User.objects.create_user(username="spirit1", email="s1@test.com")
        Player.objects.create(
            game=game, user=user, role=PlayerRole.SPIRIT, score=0,
        )

        # Act
        scores = calculate_final_scores(game)

        # Assert
        self.assertEqual(scores[0]["score"], 0)

    def test_sorted_by_score_descending(self):
        """Le resultat est trie par score decroissant."""
        # Arrange
        game = self._create_in_progress_game()
        u1 = User.objects.create_user(username="high", email="high@test.com")
        u2 = User.objects.create_user(username="low", email="low@test.com")
        Player.objects.create(
            game=game, user=u1, role=PlayerRole.HUMAN, score=100,
        )
        Player.objects.create(
            game=game, user=u2, role=PlayerRole.SPIRIT, score=0,
        )

        # Act
        scores = calculate_final_scores(game)

        # Assert
        self.assertGreaterEqual(scores[0]["score"], scores[1]["score"])

    def test_payload_contains_required_fields(self):
        """Chaque entree du payload contient player_id, role, score."""
        # Arrange
        game = self._create_in_progress_game()
        user = User.objects.create_user(username="payload", email="p@test.com")
        Player.objects.create(
            game=game, user=user, role=PlayerRole.HUMAN, score=0,
        )

        # Act
        scores = calculate_final_scores(game)

        # Assert
        entry = scores[0]
        self.assertIn("player_id", entry)
        self.assertIn("role", entry)
        self.assertIn("score", entry)
        self.assertIn("username", entry)
