"""
Tests pour le service d'attribution des roles.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from games.models import Game, GameSettings, Player, PlayerRole
from games.services.role_service import (
    _compute_spirit_count,
    assign_roles,
)

User = get_user_model()


class ComputeSpiritCountTestCase(TestCase):
    """Tests pour _compute_spirit_count."""

    def test_two_players_returns_one_spirit(self):
        """Avec 2 joueurs et 20%, au moins 1 esprit."""
        result = _compute_spirit_count(2, 20)
        self.assertEqual(result, 1)

    def test_ten_players_twenty_percent(self):
        """Avec 10 joueurs et 20%, 2 esprits."""
        result = _compute_spirit_count(10, 20)
        self.assertEqual(result, 2)

    def test_minimum_one_spirit(self):
        """Toujours au moins 1 esprit meme avec 0%."""
        result = _compute_spirit_count(5, 0)
        self.assertEqual(result, 1)

    def test_maximum_n_minus_one(self):
        """Maximum N-1 esprits (au moins 1 humain)."""
        result = _compute_spirit_count(3, 100)
        self.assertEqual(result, 2)

    def test_less_than_two_players_returns_zero(self):
        """Moins de 2 joueurs : 0 esprit."""
        self.assertEqual(_compute_spirit_count(1, 50), 0)
        self.assertEqual(_compute_spirit_count(0, 50), 0)

    def test_large_group_fifty_percent(self):
        """Avec 20 joueurs et 50%, 10 esprits."""
        result = _compute_spirit_count(20, 50)
        self.assertEqual(result, 10)


class AssignRolesTestCase(TestCase):
    """Tests pour assign_roles."""

    def _create_game_with_players(self, player_count):
        """Cree une partie avec N joueurs."""
        game = Game.objects.create(code="ROLE01")
        GameSettings.objects.create(game=game)
        for i in range(player_count):
            user = User.objects.create_user(
                username=f"roleuser{i}", email=f"role{i}@test.com",
            )
            Player.objects.create(game=game, user=user, is_admin=(i == 0))
        return game

    def test_assign_roles_at_least_one_spirit(self):
        """Il y a toujours au moins 1 esprit."""
        # Arrange
        game = self._create_game_with_players(4)

        # Act
        roles_data = assign_roles(game, spirit_percentage=20)

        # Assert
        spirit_count = sum(1 for r in roles_data if r["role"] == PlayerRole.SPIRIT)
        self.assertGreaterEqual(spirit_count, 1)

    def test_assign_roles_at_least_one_human(self):
        """Il y a toujours au moins 1 humain."""
        # Arrange
        game = self._create_game_with_players(4)

        # Act
        roles_data = assign_roles(game, spirit_percentage=90)

        # Assert
        human_count = sum(1 for r in roles_data if r["role"] == PlayerRole.HUMAN)
        self.assertGreaterEqual(human_count, 1)

    def test_assign_roles_updates_database(self):
        """Les roles sont persistes en base."""
        # Arrange
        game = self._create_game_with_players(4)

        # Act
        assign_roles(game, spirit_percentage=50)

        # Assert
        spirit_count = Player.objects.filter(
            game=game, role=PlayerRole.SPIRIT,
        ).count()
        self.assertGreaterEqual(spirit_count, 1)

    def test_assign_roles_returns_payload_with_role(self):
        """Le payload retourne contient le role de chaque joueur."""
        # Arrange
        game = self._create_game_with_players(2)

        # Act
        roles_data = assign_roles(game, spirit_percentage=50)

        # Assert
        self.assertEqual(len(roles_data), 2)
        for entry in roles_data:
            self.assertIn("role", entry)
            self.assertIn("player_id", entry)
            self.assertIn("username", entry)

    def test_assign_roles_two_players_one_spirit_one_human(self):
        """Avec 2 joueurs, exactement 1 esprit et 1 humain."""
        # Arrange
        game = self._create_game_with_players(2)

        # Act
        roles_data = assign_roles(game, spirit_percentage=50)

        # Assert
        roles = [r["role"] for r in roles_data]
        self.assertIn(PlayerRole.SPIRIT, roles)
        self.assertIn(PlayerRole.HUMAN, roles)
