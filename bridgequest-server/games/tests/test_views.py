"""
Tests pour les vues API du module Games.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from games.models import Game, Player

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

    def test_create_game_authenticated_success(self):
        """Test de création de partie avec utilisateur authentifié."""
        self._authenticate_client()
        response = self.client.post(
            '/api/games/',
            {'name': 'Ma partie'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('code', response.data)
        self.assertEqual(response.data['name'], 'Ma partie')
        self.assertEqual(response.data['state'], 'WAITING')
        self.assertEqual(len(response.data['code']), 6)

    def test_create_game_unauthenticated_forbidden(self):
        """Test de création de partie sans authentification."""
        response = self.client.post(
            '/api/games/',
            {'name': 'Ma partie'},
            format='json',
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_create_game_empty_name_validation_error(self):
        """Test de création avec nom vide."""
        self._authenticate_client()
        response = self.client.post(
            '/api/games/',
            {'name': ''},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_join_game_authenticated_success(self):
        """Test de jonction à une partie via code."""
        game = Game.objects.create(name='Partie existante', code='ABC123')
        Player.objects.create(game=game, user=self.user, is_admin=True)

        self._authenticate_client(self.other_user)
        response = self.client.post(
            '/api/games/join/',
            {'code': 'ABC123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'ABC123')
        self.assertTrue(
            Player.objects.filter(game=game, user=self.other_user).exists()
        )

    def test_join_game_code_insensitive_to_case(self):
        """Test que le code est insensible à la casse."""
        game = Game.objects.create(name='Partie', code='XYZ789')
        Player.objects.create(game=game, user=self.user, is_admin=True)

        self._authenticate_client(self.other_user)
        response = self.client.post(
            '/api/games/join/',
            {'code': 'xyz789'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'XYZ789')

    def test_join_game_code_not_found(self):
        """Test de jonction avec code inexistant."""
        self._authenticate_client()
        response = self.client.post(
            '/api/games/join/',
            {'code': '000000'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_join_game_already_in_game(self):
        """Test de jonction quand l'utilisateur est déjà dans la partie."""
        game = Game.objects.create(name='Partie', code='DEF456')
        Player.objects.create(game=game, user=self.user, is_admin=True)

        self._authenticate_client()
        response = self.client.post(
            '/api/games/join/',
            {'code': 'DEF456'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_game_detail_authenticated_success(self):
        """Test de récupération des détails d'une partie."""
        game = Game.objects.create(name='Partie', code='GHI012')
        Player.objects.create(game=game, user=self.user, is_admin=True)

        self._authenticate_client()
        response = self.client.get(f'/api/games/{game.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], game.id)
        self.assertEqual(response.data['name'], game.name)

    def test_game_detail_not_found(self):
        """Test de récupération d'une partie inexistante."""
        self._authenticate_client()
        response = self.client.get('/api/games/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_game_players_list_success(self):
        """Test de récupération de la liste des joueurs."""
        game = Game.objects.create(name='Partie', code='JKL345')
        Player.objects.create(game=game, user=self.user, is_admin=True)
        Player.objects.create(game=game, user=self.other_user, is_admin=False)

        self._authenticate_client()
        response = self.client.get(f'/api/games/{game.id}/players/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
