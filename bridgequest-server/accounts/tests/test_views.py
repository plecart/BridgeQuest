"""
Tests pour les vues API du module Accounts.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthViewsTestCase(TestCase):
    """Tests pour les vues d'authentification."""
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.client = APIClient()
        self.user_username = 'testuser'
        self.user_email = 'test@example.com'
        self.user_password = 'testpass123'
        self.user = User.objects.create_user(
            username=self.user_username,
            email=self.user_email,
            password=self.user_password,
            first_name='Test',
            last_name='User'
        )
    
    def _authenticate_client(self):
        """Helper pour authentifier le client avec l'utilisateur de test."""
        self.client.force_authenticate(user=self.user)
    
    def test_current_user_view_authenticated_success(self):
        """Test de l'endpoint current_user avec utilisateur authentifié."""
        # Arrange
        self._authenticate_client()
        
        # Act
        response = self.client.get('/api/auth/me/')
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], self.user_email)
        self.assertEqual(response.data['id'], self.user.id)
    
    def test_current_user_view_unauthenticated_forbidden(self):
        """Test de l'endpoint current_user sans authentification."""
        # Arrange & Act
        response = self.client.get('/api/auth/me/')
        
        # Assert - DRF retourne 403 Forbidden au lieu de 401 Unauthorized
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )
    
    def test_logout_view_authenticated_success(self):
        """Test de l'endpoint logout avec utilisateur authentifié."""
        # Arrange
        self._authenticate_client()
        
        # Act
        response = self.client.post('/api/auth/logout/')
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_logout_view_unauthenticated_success(self):
        """Test de l'endpoint logout sans authentification."""
        # Arrange & Act
        response = self.client.post('/api/auth/logout/')
        
        # Assert - Logout peut fonctionner même sans authentification
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_profile_view_success(self):
        """Test de l'endpoint user_profile avec utilisateur existant."""
        # Arrange
        self._authenticate_client()
        
        # Act
        response = self.client.get(f'/api/auth/profile/{self.user.id}/')
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertNotIn('email', response.data)  # Email non inclus dans UserPublicSerializer
    
    def test_user_profile_view_not_found(self):
        """Test de l'endpoint user_profile avec utilisateur inexistant."""
        # Arrange
        self._authenticate_client()
        non_existent_id = 99999
        
        # Act
        response = self.client.get(f'/api/auth/profile/{non_existent_id}/')
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_user_profile_view_unauthenticated_forbidden(self):
        """Test de l'endpoint user_profile sans authentification."""
        # Arrange & Act
        response = self.client.get(f'/api/auth/profile/{self.user.id}/')
        
        # Assert - DRF retourne 403 Forbidden au lieu de 401 Unauthorized
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )
