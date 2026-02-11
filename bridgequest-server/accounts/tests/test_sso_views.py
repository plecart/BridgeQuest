"""
Tests pour les vues SSO mobile du module Accounts.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages

User = get_user_model()


class SSOViewsTestCase(TestCase):
    """Tests pour les vues d'authentification SSO mobile."""
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.client = APIClient()
        self.sso_email = 'sso@example.com'
        self.sso_token = 'fake_token_12345'
        self.sso_data_google = {
            'email': self.sso_email,
            'given_name': 'John',
            'family_name': 'Doe',
            'picture': 'https://example.com/avatar.jpg',
            'sub': 'google_user_id_123'
        }
        self.sso_data_apple = {
            'email': self.sso_email,
            'given_name': 'Jane',
            'family_name': 'Smith',
            'sub': 'apple_user_id_456'
        }
    
    def test_sso_login_google_success_new_user(self):
        """Test de connexion SSO Google avec création d'un nouvel utilisateur."""
        # Arrange
        with patch('accounts.views.auth_views.validate_google_token') as mock_validate:
            mock_validate.return_value = self.sso_data_google
            
            # Act
            response = self.client.post(
                '/api/auth/sso/login/',
                {
                    'provider': 'google',
                    'token': self.sso_token
                },
                format='json'
            )
            
            # Assert
            self.assertEqual(response.status_code, status.HTTP_200_OK, 
                           f"Expected 200, got {response.status_code}. Response: {response.data}")
            self.assertIn('user', response.data)
            self.assertIn('message', response.data)
            self.assertEqual(response.data['user']['email'], self.sso_email)
            self.assertEqual(response.data['user']['first_name'], 'John')
            self.assertEqual(response.data['user']['last_name'], 'Doe')
            
            # Vérifier que l'utilisateur a été créé
            user = User.objects.get(email=self.sso_email)
            self.assertIsNotNone(user)
            self.assertEqual(user.first_name, 'John')
            self.assertEqual(user.last_name, 'Doe')
            mock_validate.assert_called_once_with(self.sso_token)
    
    def test_sso_login_google_success_existing_user(self):
        """Test de connexion SSO Google avec utilisateur existant."""
        # Arrange
        existing_user = User.objects.create_user(
            username='existing',
            email=self.sso_email,
            first_name='Old',
            last_name='Name'
        )
        
        with patch('accounts.views.auth_views.validate_google_token') as mock_validate:
            mock_validate.return_value = self.sso_data_google
            
            # Act
            response = self.client.post(
                '/api/auth/sso/login/',
                {
                    'provider': 'google',
                    'token': self.sso_token
                },
                format='json'
            )
            
            # Assert
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                           f"Expected 200, got {response.status_code}. Response: {response.data}")
            self.assertEqual(response.data['user']['id'], existing_user.id)
            # Les informations existantes ne doivent pas être écrasées si déjà présentes
            existing_user.refresh_from_db()
            self.assertEqual(existing_user.first_name, 'Old')
    
    def test_sso_login_apple_success_new_user(self):
        """Test de connexion SSO Apple avec création d'un nouvel utilisateur."""
        # Arrange
        with patch('accounts.views.auth_views.validate_apple_token') as mock_validate:
            mock_validate.return_value = self.sso_data_apple
            
            # Act
            response = self.client.post(
                '/api/auth/sso/login/',
                {
                    'provider': 'apple',
                    'token': self.sso_token
                },
                format='json'
            )
            
            # Assert
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                           f"Expected 200, got {response.status_code}. Response: {response.data}")
            self.assertIn('user', response.data)
            self.assertEqual(response.data['user']['email'], self.sso_email)
            mock_validate.assert_called_once_with(self.sso_token)
    
    def test_sso_login_invalid_provider(self):
        """Test de connexion SSO avec un provider invalide."""
        # Arrange & Act
        response = self.client.post(
            '/api/auth/sso/login/',
            {
                'provider': 'invalid_provider',
                'token': self.sso_token
            },
            format='json'
        )
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('provider', response.data)
    
    def test_sso_login_missing_token(self):
        """Test de connexion SSO sans token."""
        # Arrange & Act
        response = self.client.post(
            '/api/auth/sso/login/',
            {
                'provider': 'google'
            },
            format='json'
        )
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
    
    def test_sso_login_empty_token(self):
        """Test de connexion SSO avec un token vide."""
        # Arrange & Act
        response = self.client.post(
            '/api/auth/sso/login/',
            {
                'provider': 'google',
                'token': ''
            },
            format='json'
        )
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
    
    def test_sso_login_invalid_token(self):
        """Test de connexion SSO avec un token invalide."""
        # Arrange
        with patch('accounts.views.auth_views.validate_google_token') as mock_validate:
            mock_validate.side_effect = BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED))
            
            # Act
            response = self.client.post(
                '/api/auth/sso/login/',
                {
                    'provider': 'google',
                    'token': 'invalid_token'
                },
                format='json'
            )
            
            # Assert
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)

    def test_sso_login_config_error_returns_500(self):
        """Test que les erreurs de configuration SSO renvoient 500 (erreur serveur)."""
        # Arrange : simuler une erreur de configuration (GOOGLE_CLIENT_IDS manquant, etc.)
        with patch('accounts.views.auth_views.validate_google_token') as mock_validate:
            mock_validate.side_effect = BridgeQuestException(
                message_key=ErrorMessages.AUTH_SSO_CONFIG_ERROR,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

            # Act
            response = self.client.post(
                '/api/auth/sso/login/',
                {
                    'provider': 'google',
                    'token': self.sso_token
                },
                format='json'
            )

            # Assert
            self.assertEqual(
                response.status_code,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Expected 500 for config error, got {response.status_code}. Response: {response.data}"
            )
            self.assertIn('error', response.data)
