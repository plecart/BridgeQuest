"""
Tests pour les vues SSO mobile du module Accounts.
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages

User = get_user_model()

SSO_LOGIN_URL = '/api/auth/sso/login/'


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
            'sub': 'google_user_id_123',
        }
        self.sso_data_apple = {
            'email': self.sso_email,
            'given_name': 'Jane',
            'family_name': 'Smith',
            'sub': 'apple_user_id_456',
        }

    def _post_sso_login(self, provider='google', token=None):
        """Envoie une requête POST vers l'endpoint SSO login."""
        if token is None:
            token = self.sso_token
        return self.client.post(
            SSO_LOGIN_URL,
            {'provider': provider, 'token': token},
            format='json',
        )

    def _assert_login_response_contains_valid_tokens(self, data):
        """
        Vérifie que la réponse contient des champs access et refresh non vides
        et au format JWT (3 parties séparées par des points).
        """
        self.assertIn('access', data, msg="Response must contain 'access' token")
        self.assertIn('refresh', data, msg="Response must contain 'refresh' token")
        access = data['access']
        refresh = data['refresh']
        self.assertTrue(access, msg="access token must be non-empty")
        self.assertTrue(refresh, msg="refresh token must be non-empty")
        self.assertIsInstance(access, str, msg="access must be a string")
        self.assertIsInstance(refresh, str, msg="refresh must be a string")
        for name, token in [('access', access), ('refresh', refresh)]:
            parts = token.split('.')
            self.assertEqual(len(parts), 3, msg=f"{name} token must be a JWT (3 parts), got {len(parts)}")

    def test_sso_login_google_success_new_user(self):
        """Test de connexion SSO Google avec création d'un nouvel utilisateur."""
        with patch('accounts.views.auth_views.validate_google_token') as mock_validate:
            mock_validate.return_value = self.sso_data_google

            response = self._post_sso_login(provider='google')

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                msg=f"Expected 200, got {response.status_code}. Response: {response.data}",
            )
            self.assertIn('user', response.data)
            self.assertIn('message', response.data)
            self.assertEqual(response.data['user']['email'], self.sso_email)
            self.assertEqual(response.data['user']['first_name'], 'John')
            self.assertEqual(response.data['user']['last_name'], 'Doe')
            self._assert_login_response_contains_valid_tokens(response.data)
            user = User.objects.get(email=self.sso_email)
            self.assertIsNotNone(user)
            self.assertEqual(user.first_name, 'John')
            self.assertEqual(user.last_name, 'Doe')
            mock_validate.assert_called_once_with(self.sso_token)
    
    def test_sso_login_google_success_existing_user(self):
        """Test de connexion SSO Google avec utilisateur existant."""
        existing_user = User.objects.create_user(
            username='existing',
            email=self.sso_email,
            first_name='Old',
            last_name='Name',
        )
        with patch('accounts.views.auth_views.validate_google_token') as mock_validate:
            mock_validate.return_value = self.sso_data_google

            response = self._post_sso_login(provider='google')

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                msg=f"Expected 200, got {response.status_code}. Response: {response.data}",
            )
            self.assertIn('user', response.data)
            self.assertEqual(response.data['user']['id'], existing_user.id)
            self._assert_login_response_contains_valid_tokens(response.data)
            existing_user.refresh_from_db()
            self.assertEqual(existing_user.first_name, 'Old')
    
    def test_sso_login_apple_success_new_user(self):
        """Test de connexion SSO Apple avec création d'un nouvel utilisateur."""
        with patch('accounts.views.auth_views.validate_apple_token') as mock_validate:
            mock_validate.return_value = self.sso_data_apple

            response = self._post_sso_login(provider='apple')

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                msg=f"Expected 200, got {response.status_code}. Response: {response.data}",
            )
            self.assertIn('user', response.data)
            self.assertEqual(response.data['user']['email'], self.sso_email)
            self._assert_login_response_contains_valid_tokens(response.data)
            mock_validate.assert_called_once_with(self.sso_token)
    
    def test_sso_login_invalid_provider(self):
        """Test de connexion SSO avec un provider invalide."""
        response = self.client.post(
            SSO_LOGIN_URL,
            {'provider': 'invalid_provider', 'token': self.sso_token},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('provider', response.data)

    def test_sso_login_missing_token(self):
        """Test de connexion SSO sans token."""
        response = self.client.post(
            SSO_LOGIN_URL,
            {'provider': 'google'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)

    def test_sso_login_empty_token(self):
        """Test de connexion SSO avec un token vide."""
        response = self._post_sso_login(provider='google', token='')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)

    def test_sso_login_invalid_token(self):
        """Test de connexion SSO avec un token invalide."""
        with patch('accounts.views.auth_views.validate_google_token') as mock_validate:
            mock_validate.side_effect = BridgeQuestException(
                ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED
            )

            response = self._post_sso_login(provider='google', token='invalid_token')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)
