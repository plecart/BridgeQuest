"""
Tests pour les vues API du module Games.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from games.models import Game, GameSettings, GameState, Player

User = get_user_model()


class GameViewsTestCase(TestCase):
    """Tests pour les vues de parties."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
        )

    def _authenticate_client(self, user=None):
        """Authentifie le client avec l'utilisateur spécifié."""
        self.client.force_authenticate(user=user or self.user)

    def _post_join_game(self, code, user=None):
        """Envoie une requête POST pour rejoindre une partie via son code."""
        self._authenticate_client(user)
        return self.client.post(
            '/api/games/join/',
            {'code': code},
            format='json',
        )

    def test_create_game_authenticated_success(self):
        """Test de création de partie avec utilisateur authentifié."""
        self._authenticate_client()
        response = self.client.post(
            '/api/games/',
            {},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('code', response.data)
        self.assertEqual(response.data['state'], 'WAITING')
        self.assertEqual(len(response.data['code']), 6)

    def test_create_game_unauthenticated_forbidden(self):
        """Test de création de partie sans authentification."""
        response = self.client.post(
            '/api/games/',
            {},
            format='json',
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_join_game_authenticated_success(self):
        """Test de jonction à une partie via code."""
        game = Game.objects.create(code='ABC123')
        Player.objects.create(game=game, user=self.user, is_admin=True)

        response = self._post_join_game('ABC123', user=self.other_user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'ABC123')
        self.assertTrue(
            Player.objects.filter(game=game, user=self.other_user).exists()
        )

    def test_join_game_code_insensitive_to_case(self):
        """Test que le code est insensible à la casse."""
        game = Game.objects.create(code='XYZ789')
        Player.objects.create(game=game, user=self.user, is_admin=True)

        response = self._post_join_game('xyz789', user=self.other_user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'XYZ789')

    def test_join_game_code_not_found(self):
        """Test de jonction avec code inexistant."""
        response = self._post_join_game('000000')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_join_game_code_invalid_format_rejected(self):
        """Test que les codes non alphanumériques sont rejetés par le serializer."""
        response = self._post_join_game('AB-123')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_join_game_already_in_game(self):
        """Test de jonction quand l'utilisateur est déjà dans la partie."""
        game = Game.objects.create(code='DEF456')
        Player.objects.create(game=game, user=self.user, is_admin=True)

        response = self._post_join_game('DEF456')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_game_detail_authenticated_success(self):
        """Test de récupération des détails d'une partie."""
        game = Game.objects.create(code='GHI012')
        Player.objects.create(game=game, user=self.user, is_admin=True)

        self._authenticate_client()
        response = self.client.get(f'/api/games/{game.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], game.id)
        self.assertEqual(response.data['code'], game.code)

    def test_game_detail_not_found(self):
        """Test de récupération d'une partie inexistante."""
        self._authenticate_client()
        response = self.client.get('/api/games/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_game_players_list_success(self):
        """Test de récupération de la liste des joueurs."""
        game = Game.objects.create(code='JKL345')
        Player.objects.create(game=game, user=self.user, is_admin=True)
        Player.objects.create(game=game, user=self.other_user, is_admin=False)

        self._authenticate_client()
        response = self.client.get(f'/api/games/{game.id}/players/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_game_start_admin_success(self):
        """Test de lancement de partie par l'administrateur (min 2 joueurs)."""
        game = Game.objects.create(code='MNO678')
        GameSettings.objects.create(game=game)
        Player.objects.create(game=game, user=self.user, is_admin=True)
        Player.objects.create(game=game, user=self.other_user, is_admin=False)

        self._authenticate_client()
        response = self.client.post(f'/api/games/{game.id}/start/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], GameState.DEPLOYMENT)

    def test_game_start_not_admin_forbidden(self):
        """Test de lancement par un joueur non-admin."""
        game = Game.objects.create(code='PQR901')
        Player.objects.create(game=game, user=self.user, is_admin=True)
        Player.objects.create(game=game, user=self.other_user, is_admin=False)

        self._authenticate_client(self.other_user)
        response = self.client.post(f'/api/games/{game.id}/start/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)

    def test_game_start_not_in_game_forbidden(self):
        """Test de lancement par un utilisateur non présent dans la partie."""
        game = Game.objects.create(code='STU234')
        Player.objects.create(game=game, user=self.user, is_admin=True)

        self._authenticate_client(self.other_user)
        response = self.client.post(f'/api/games/{game.id}/start/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)

    def test_game_start_already_started_bad_request(self):
        """Test de lancement d'une partie déjà commencée."""
        game = Game.objects.create(
            code='VWX567',
            state=GameState.DEPLOYMENT,
        )
        Player.objects.create(game=game, user=self.user, is_admin=True)

        self._authenticate_client()
        response = self.client.post(f'/api/games/{game.id}/start/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_game_start_not_found(self):
        """Test de lancement d'une partie inexistante."""
        self._authenticate_client()
        response = self.client.post('/api/games/99999/start/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_game_start_unauthenticated_forbidden(self):
        """Test de lancement sans authentification."""
        game = Game.objects.create(code='YZA890')
        Player.objects.create(game=game, user=self.user, is_admin=True)

        response = self.client.post(f'/api/games/{game.id}/start/')
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


class GameSettingsViewsTestCase(TestCase):
    """Tests pour les vues API des parametres de partie."""

    def setUp(self):
        """Configuration initiale."""
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="settingsadmin", email="sadmin@test.com",
        )
        self.player = User.objects.create_user(
            username="settingsplayer", email="splayer@test.com",
        )
        self.game = Game.objects.create(code="SETT01")
        GameSettings.objects.create(game=self.game)
        Player.objects.create(
            game=self.game, user=self.admin, is_admin=True,
        )
        Player.objects.create(
            game=self.game, user=self.player, is_admin=False,
        )

    def _authenticate(self, user=None):
        """Authentifie le client."""
        self.client.force_authenticate(user=user or self.admin)

    def test_get_settings_success(self):
        """Test GET settings par un joueur de la partie."""
        # Arrange
        self._authenticate(self.player)

        # Act
        response = self.client.get(f"/api/games/{self.game.id}/settings/")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("game_duration", response.data)
        self.assertIn("points_per_minute", response.data)

    def test_patch_settings_admin_success(self):
        """Test PATCH settings par l'admin."""
        # Arrange
        self._authenticate(self.admin)

        # Act
        response = self.client.patch(
            f"/api/games/{self.game.id}/settings/",
            {"game_duration": 60},
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["game_duration"], 60)

    def test_patch_settings_non_admin_forbidden(self):
        """Test PATCH settings par un joueur non-admin."""
        # Arrange
        self._authenticate(self.player)

        # Act
        response = self.client.patch(
            f"/api/games/{self.game.id}/settings/",
            {"game_duration": 60},
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_settings_game_not_waiting_forbidden(self):
        """Test PATCH settings sur une partie non-WAITING."""
        # Arrange
        self.game.state = GameState.IN_PROGRESS
        self.game.save()
        self._authenticate(self.admin)

        # Act
        response = self.client.patch(
            f"/api/games/{self.game.id}/settings/",
            {"game_duration": 60},
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_settings_unauthenticated_forbidden(self):
        """Test GET settings sans authentification."""
        # Act
        response = self.client.get(f"/api/games/{self.game.id}/settings/")

        # Assert
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
