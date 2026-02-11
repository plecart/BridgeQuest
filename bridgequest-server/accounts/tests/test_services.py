"""
Tests pour les services du module Accounts.
"""
from unittest.mock import Mock, patch

import jwt
import requests
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken

from accounts.services import apple_auth_service, google_auth_service
from accounts.services.auth_service import (
    create_or_get_user_from_sso_data,
    get_user_by_email,
)
from accounts.services.jwt_service import generate_tokens_for_user
from utils.exceptions import BridgeQuestException
from utils.sso_validation import REQUEST_TIMEOUT_SECONDS

User = get_user_model()


class JwtServiceTestCase(TestCase):
    """Tests pour le service de génération des tokens JWT."""

    JWT_SEGMENTS_COUNT = 3  # header.payload.signature

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user = User.objects.create_user(
            username='jwtuser',
            email='jwt@example.com',
            first_name='Jwt',
            last_name='User',
        )

    def _assert_jwt_format(self, token):
        """Vérifie qu'un token a le format JWT (3 segments base64 séparés par des points)."""
        parts = token.split('.')
        self.assertEqual(
            len(parts),
            self.JWT_SEGMENTS_COUNT,
            "Un JWT doit contenir header.payload.signature",
        )

    def test_generate_tokens_for_user_returns_access_and_refresh(self):
        """Test que le dictionnaire retourné contient les clés access et refresh."""
        tokens = generate_tokens_for_user(self.user)
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertIsInstance(tokens['access'], str)
        self.assertIsInstance(tokens['refresh'], str)
        self.assertGreater(len(tokens['access']), 0)
        self.assertGreater(len(tokens['refresh']), 0)

    def test_generate_tokens_for_user_access_format_jwt(self):
        """Test que le token access a le format JWT (3 segments base64)."""
        tokens = generate_tokens_for_user(self.user)
        self._assert_jwt_format(tokens['access'])

    def test_generate_tokens_for_user_refresh_format_jwt(self):
        """Test que le token refresh a le format JWT (3 segments base64)."""
        tokens = generate_tokens_for_user(self.user)
        self._assert_jwt_format(tokens['refresh'])

    def test_generate_tokens_for_user_access_token_compatible_simple_jwt(self):
        """Test que le token access est compatible SIMPLE_JWT (payload contient user_id)."""
        tokens = generate_tokens_for_user(self.user)
        access = AccessToken(tokens['access'])
        # Simple JWT peut sérialiser user_id en int ou str selon la config
        self.assertEqual(int(access['user_id']), self.user.id)

    def test_generate_tokens_for_user_different_users_different_tokens(self):
        """Test que deux utilisateurs différents reçoivent des tokens différents."""
        other_user = User.objects.create_user(
            username='otherjwt',
            email='otherjwt@example.com',
        )
        tokens_user = generate_tokens_for_user(self.user)
        tokens_other = generate_tokens_for_user(other_user)
        self.assertNotEqual(tokens_user['access'], tokens_other['access'])
        self.assertNotEqual(tokens_user['refresh'], tokens_other['refresh'])


class AuthServiceTestCase(TestCase):
    """Tests pour le service d'authentification."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user_email = 'test@example.com'
        self.user_username = 'testuser'
        self.user = User.objects.create_user(
            username=self.user_username,
            email=self.user_email,
            first_name='Test',
            last_name='User'
        )

    def test_get_user_by_email_success(self):
        """Test de récupération d'un utilisateur par email."""
        user = get_user_by_email(self.user_email)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.user_email)

    def test_get_user_by_email_not_found(self):
        """Test de récupération d'un utilisateur inexistant."""
        user = get_user_by_email('nonexistent@example.com')
        self.assertIsNone(user)

    def test_get_user_by_email_empty(self):
        """Test avec un email vide."""
        with self.assertRaises(BridgeQuestException):
            get_user_by_email('')

    def test_get_user_by_email_none(self):
        """Test avec None."""
        with self.assertRaises(BridgeQuestException):
            get_user_by_email(None)

    def test_create_or_get_user_from_sso_data_new_user(self):
        """Test de création d'un nouvel utilisateur depuis des données SSO."""
        sso_data = {
            'email': 'newuser@example.com',
            'given_name': 'New',
            'family_name': 'User',
            'picture': 'https://example.com/avatar.jpg'
        }

        user = create_or_get_user_from_sso_data(sso_data, 'google')

        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.avatar, 'https://example.com/avatar.jpg')

    def test_create_or_get_user_from_sso_data_existing_user(self):
        """Test de récupération d'un utilisateur existant depuis des données SSO."""
        sso_data = {
            'email': self.user_email,
            'given_name': 'Updated',
            'family_name': 'Name',
            'picture': 'https://example.com/newavatar.jpg'
        }

        user = create_or_get_user_from_sso_data(sso_data, 'google')

        self.assertEqual(user.id, self.user.id)
        # Les informations existantes ne doivent pas être écrasées
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')

    def test_create_or_get_user_from_sso_data_no_email_raises_exception(self):
        """Test qu'un SSO sans email lève une exception."""
        sso_data = {
            'given_name': 'Test',
            'family_name': 'User'
        }

        with self.assertRaises(BridgeQuestException):
            create_or_get_user_from_sso_data(sso_data, 'google')

    def test_create_or_get_user_from_sso_data_updates_empty_fields(self):
        """Test que les champs vides sont mis à jour."""
        user = User.objects.create_user(
            username='incomplete',
            email='incomplete@example.com',
            first_name='',
            last_name='',
            avatar=''
        )

        sso_data = {
            'email': 'incomplete@example.com',
            'given_name': 'Complete',
            'family_name': 'User',
            'picture': 'https://example.com/avatar.jpg'
        }

        updated_user = create_or_get_user_from_sso_data(sso_data, 'google')

        self.assertEqual(updated_user.id, user.id)
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Complete')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.avatar, 'https://example.com/avatar.jpg')


class GoogleAuthServiceTestCase(TestCase):
    """Tests pour le service de validation des tokens Google Sign-In."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.valid_token = 'valid-google-id-token'
        self.valid_client_id = '123456789-xxx.apps.googleusercontent.com'
        self.valid_token_info = {
            'aud': self.valid_client_id,
            'email': 'user@example.com',
            'given_name': 'John',
            'family_name': 'Doe',
            'picture': 'https://example.com/photo.jpg',
            'sub': 'google-sub-id',
        }

    def _assert_google_user_data(self, result, email, given_name, family_name, picture, sub):
        """Vérifie que le dictionnaire contient les données utilisateur Google attendues."""
        self.assertEqual(result['email'], email)
        self.assertEqual(result['given_name'], given_name)
        self.assertEqual(result['family_name'], family_name)
        self.assertEqual(result['picture'], picture)
        self.assertEqual(result['sub'], sub)

    @patch.object(google_auth_service, 'settings')
    @patch('accounts.services.google_auth_service.requests.get')
    def test_validate_google_token_success(self, mock_get, mock_settings):
        """Test de validation réussie d'un token Google."""
        mock_settings.GOOGLE_CLIENT_IDS = [self.valid_client_id]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.valid_token_info
        mock_get.return_value = mock_response

        result = google_auth_service.validate_google_token(self.valid_token)

        self._assert_google_user_data(
            result,
            email='user@example.com',
            given_name='John',
            family_name='Doe',
            picture='https://example.com/photo.jpg',
            sub='google-sub-id',
        )
        mock_get.assert_called_once()

    def test_validate_google_token_empty_raises_exception(self):
        """Test qu'un token vide lève une exception."""
        with self.assertRaises(BridgeQuestException):
            google_auth_service.validate_google_token('')

    def test_validate_google_token_none_raises_exception(self):
        """Test que None lève une exception."""
        with self.assertRaises(BridgeQuestException):
            google_auth_service.validate_google_token(None)

    @patch.object(google_auth_service, 'settings')
    def test_get_google_client_ids_success(self, mock_settings):
        """Test de récupération des Client IDs depuis la configuration."""
        mock_settings.GOOGLE_CLIENT_IDS = [self.valid_client_id]

        result = google_auth_service._get_google_client_ids()

        self.assertEqual(result, [self.valid_client_id])

    @patch.object(google_auth_service, 'settings')
    def test_get_google_client_ids_missing_raises_exception(self, mock_settings):
        """Test qu'une configuration manquante lève une exception."""
        mock_settings.GOOGLE_CLIENT_IDS = None
        with self.assertRaises(BridgeQuestException):
            google_auth_service._get_google_client_ids()

    @patch.object(google_auth_service, 'settings')
    def test_get_google_client_ids_empty_list_raises_exception(self, mock_settings):
        """Test qu'une liste vide de Client IDs lève une exception."""
        mock_settings.GOOGLE_CLIENT_IDS = []
        with self.assertRaises(BridgeQuestException):
            google_auth_service._get_google_client_ids()

    @patch('accounts.services.google_auth_service.requests.get')
    def test_fetch_token_info_success(self, mock_get):
        """Test de récupération des informations du token depuis l'API Google."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.valid_token_info
        mock_get.return_value = mock_response

        result = google_auth_service._fetch_token_info(self.valid_token)

        self.assertEqual(result, self.valid_token_info)
        mock_get.assert_called_once_with(
            google_auth_service.GOOGLE_TOKEN_INFO_URL,
            params={'id_token': self.valid_token},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    @patch('accounts.services.google_auth_service.requests.get')
    def test_fetch_token_info_non_200_raises_exception(self, mock_get):
        """Test qu'un statut HTTP non 200 lève une exception."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(BridgeQuestException):
            google_auth_service._fetch_token_info(self.valid_token)

    @patch('accounts.services.google_auth_service.requests.get')
    def test_fetch_token_info_error_in_response_raises_exception(self, mock_get):
        """Test qu'une réponse contenant 'error' lève une exception."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'error': 'invalid_token', 'error_description': 'Invalid'}
        mock_get.return_value = mock_response

        with self.assertRaises(BridgeQuestException):
            google_auth_service._fetch_token_info(self.valid_token)

    @patch('accounts.services.google_auth_service.requests.get')
    def test_fetch_token_info_request_exception_raises_exception(self, mock_get):
        """Test qu'une RequestException lève une exception."""
        mock_get.side_effect = requests.RequestException('Network error')

        with self.assertRaises(BridgeQuestException):
            google_auth_service._fetch_token_info(self.valid_token)

    def test_validate_token_audience_success(self):
        """Test de validation de l'audience lorsque le Client ID est autorisé."""
        google_auth_service._validate_token_audience(
            self.valid_token_info, [self.valid_client_id]
        )

    def test_validate_token_audience_missing_aud_raises_exception(self):
        """Test qu'une audience manquante lève une exception."""
        token_info = {k: v for k, v in self.valid_token_info.items() if k != 'aud'}
        with self.assertRaises(BridgeQuestException):
            google_auth_service._validate_token_audience(
                token_info, [self.valid_client_id]
            )

    def test_validate_token_audience_wrong_aud_raises_exception(self):
        """Test qu'une audience non autorisée lève une exception."""
        token_info = {**self.valid_token_info, 'aud': 'wrong-client-id.apps.googleusercontent.com'}
        with self.assertRaises(BridgeQuestException):
            google_auth_service._validate_token_audience(
                token_info, [self.valid_client_id]
            )

    def test_extract_user_data_success(self):
        """Test d'extraction des données utilisateur depuis le token info."""
        result = google_auth_service._extract_user_data(self.valid_token_info)
        self._assert_google_user_data(
            result,
            email='user@example.com',
            given_name='John',
            family_name='Doe',
            picture='https://example.com/photo.jpg',
            sub='google-sub-id',
        )

    def test_extract_user_data_missing_email_raises_exception(self):
        """Test qu'un email manquant lève une exception."""
        token_info = {k: v for k, v in self.valid_token_info.items() if k != 'email'}
        with self.assertRaises(BridgeQuestException):
            google_auth_service._extract_user_data(token_info)

    def test_extract_user_data_empty_email_raises_exception(self):
        """Test qu'un email vide lève une exception."""
        token_info = {**self.valid_token_info, 'email': ''}
        with self.assertRaises(BridgeQuestException):
            google_auth_service._extract_user_data(token_info)

    def test_extract_user_data_handles_missing_optional_fields(self):
        """Test que les champs optionnels absents sont renvoyés comme chaînes vides."""
        token_info = {'aud': self.valid_client_id, 'email': 'minimal@example.com', 'sub': 'sub-id'}
        result = google_auth_service._extract_user_data(token_info)

        self.assertEqual(result['email'], 'minimal@example.com')
        self.assertEqual(result['given_name'], '')
        self.assertEqual(result['family_name'], '')
        self.assertEqual(result['picture'], '')
        self.assertEqual(result['sub'], 'sub-id')


class AppleAuthServiceTestCase(TestCase):
    """Tests pour le service de validation des tokens Apple Sign-In."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.valid_token = 'valid-apple-id-token'
        self.valid_client_id = 'com.example.app'
        self.valid_decoded_token = {
            'sub': 'apple-sub-id',
            'email': 'user@example.com',
            'given_name': 'John',
            'family_name': 'Doe',
        }
        self.valid_unverified_header = {'kid': 'APPLE_KEY_ID'}
        self.valid_apple_keys = {'keys': [{'kid': 'APPLE_KEY_ID'}]}

    def _assert_apple_user_data(self, result, email, sub, given_name='', family_name=''):
        """Vérifie que le dictionnaire contient les données utilisateur Apple attendues."""
        self.assertEqual(result['email'], email)
        self.assertEqual(result['sub'], sub)
        self.assertEqual(result['given_name'], given_name)
        self.assertEqual(result['family_name'], family_name)

    @patch.object(apple_auth_service, 'settings')
    @patch('accounts.services.apple_auth_service.jwt.decode')
    @patch('accounts.services.apple_auth_service._find_matching_public_key')
    @patch('accounts.services.apple_auth_service._fetch_apple_public_keys')
    @patch('accounts.services.apple_auth_service.jwt.get_unverified_header')
    def test_validate_apple_token_success(
        self, mock_get_header, mock_fetch_keys, mock_find_key, mock_decode, mock_settings
    ):
        """Test de validation réussie d'un token Apple."""
        mock_settings.APPLE_CLIENT_ID = self.valid_client_id
        mock_get_header.return_value = self.valid_unverified_header
        mock_fetch_keys.return_value = self.valid_apple_keys
        mock_find_key.return_value = Mock()
        mock_decode.return_value = self.valid_decoded_token

        result = apple_auth_service.validate_apple_token(self.valid_token)
        self._assert_apple_user_data(
            result,
            email='user@example.com',
            sub='apple-sub-id',
            given_name='John',
            family_name='Doe',
        )

    def test_validate_apple_token_empty_raises_exception(self):
        """Test qu'un token vide lève une exception."""
        with self.assertRaises(BridgeQuestException):
            apple_auth_service.validate_apple_token('')

    def test_validate_apple_token_none_raises_exception(self):
        """Test que None lève une exception."""
        with self.assertRaises(BridgeQuestException):
            apple_auth_service.validate_apple_token(None)

    @patch('accounts.services.apple_auth_service.jwt.get_unverified_header')
    def test_validate_apple_token_invalid_token_error_raises_bridgequest(self, mock_get_header):
        """Test que jwt.InvalidTokenError est converti en BridgeQuestException."""
        mock_get_header.side_effect = jwt.InvalidTokenError('Invalid')
        with self.assertRaises(BridgeQuestException):
            apple_auth_service.validate_apple_token(self.valid_token)

    @patch('accounts.services.apple_auth_service._decode_and_verify_token')
    def test_validate_apple_token_bridgequest_exception_re_raised(self, mock_decode):
        """Test qu'une BridgeQuestException est relancée telle quelle."""
        mock_decode.side_effect = BridgeQuestException('key')
        with self.assertRaises(BridgeQuestException):
            apple_auth_service.validate_apple_token(self.valid_token)

    @patch('accounts.services.apple_auth_service._decode_and_verify_token')
    def test_validate_apple_token_generic_exception_raises_auth_sso_failed(self, mock_decode):
        """Test qu'une exception générique est convertie en AUTH_SSO_FAILED."""
        mock_decode.side_effect = ValueError('Unexpected')
        with self.assertRaises(BridgeQuestException):
            apple_auth_service.validate_apple_token(self.valid_token)

    @patch.object(apple_auth_service, 'settings')
    def test_get_apple_client_id_success(self, mock_settings):
        """Test de récupération du Client ID Apple depuis la configuration."""
        mock_settings.APPLE_CLIENT_ID = self.valid_client_id
        result = apple_auth_service._get_apple_client_id()
        self.assertEqual(result, self.valid_client_id)

    @patch.object(apple_auth_service, 'settings')
    def test_get_apple_client_id_missing_raises_exception(self, mock_settings):
        """Test qu'une configuration manquante lève une exception."""
        mock_settings.APPLE_CLIENT_ID = None
        with self.assertRaises(BridgeQuestException):
            apple_auth_service._get_apple_client_id()

    @patch.object(apple_auth_service, 'settings')
    def test_get_apple_client_id_empty_string_raises_exception(self, mock_settings):
        """Test qu'un Client ID vide lève une exception."""
        mock_settings.APPLE_CLIENT_ID = ''
        with self.assertRaises(BridgeQuestException):
            apple_auth_service._get_apple_client_id()

    @patch('accounts.services.apple_auth_service.requests.get')
    def test_fetch_apple_public_keys_success(self, mock_get):
        """Test de récupération des clés publiques Apple."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.valid_apple_keys
        mock_get.return_value = mock_response

        result = apple_auth_service._fetch_apple_public_keys()

        self.assertEqual(result, self.valid_apple_keys)
        mock_get.assert_called_once_with(
            apple_auth_service.APPLE_PUBLIC_KEYS_URL,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    @patch('accounts.services.apple_auth_service.requests.get')
    def test_fetch_apple_public_keys_non_200_raises_exception(self, mock_get):
        """Test qu'un statut HTTP non 200 lève une exception."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        with self.assertRaises(BridgeQuestException):
            apple_auth_service._fetch_apple_public_keys()

    @patch('accounts.services.apple_auth_service.requests.get')
    def test_fetch_apple_public_keys_request_exception_raises_exception(self, mock_get):
        """Test qu'une RequestException lève une exception."""
        mock_get.side_effect = requests.RequestException('Network error')
        with self.assertRaises(BridgeQuestException):
            apple_auth_service._fetch_apple_public_keys()

    @patch('accounts.services.apple_auth_service.RSAAlgorithm.from_jwk')
    def test_find_matching_public_key_success(self, mock_from_jwk):
        """Test de recherche d'une clé correspondante au kid du header."""
        mock_key = Mock()
        mock_from_jwk.return_value = mock_key
        unverified_header = {'kid': 'APPLE_KEY_ID'}
        apple_keys = {'keys': [{'kid': 'APPLE_KEY_ID'}]}

        result = apple_auth_service._find_matching_public_key(apple_keys, unverified_header)

        self.assertEqual(result, mock_key)
        # PyJWT RSAAlgorithm.from_jwk accepte un dict (clé JWK)
        mock_from_jwk.assert_called_once_with({'kid': 'APPLE_KEY_ID'})

    def test_find_matching_public_key_no_match_returns_none(self):
        """Test qu'aucune clé correspondante ne retourne None."""
        unverified_header = {'kid': 'UNKNOWN_KID'}
        apple_keys = {'keys': [{'kid': 'APPLE_KEY_ID'}]}
        result = apple_auth_service._find_matching_public_key(apple_keys, unverified_header)
        self.assertIsNone(result)

    def test_find_matching_public_key_empty_keys_returns_none(self):
        """Test qu'une liste de clés vide retourne None."""
        unverified_header = {'kid': 'APPLE_KEY_ID'}
        apple_keys = {'keys': []}
        result = apple_auth_service._find_matching_public_key(apple_keys, unverified_header)
        self.assertIsNone(result)

    @patch.object(apple_auth_service, 'settings')
    @patch('accounts.services.apple_auth_service.jwt.decode')
    def test_decode_token_with_key_success(self, mock_decode, mock_settings):
        """Test de décodage du token avec la clé publique."""
        mock_settings.APPLE_CLIENT_ID = self.valid_client_id
        mock_decode.return_value = self.valid_decoded_token
        mock_public_key = Mock()

        result = apple_auth_service._decode_token_with_key(self.valid_token, mock_public_key)

        self.assertEqual(result, self.valid_decoded_token)
        mock_decode.assert_called_once_with(
            self.valid_token,
            mock_public_key,
            algorithms=['RS256'],
            issuer=apple_auth_service.APPLE_ISSUER,
            audience=self.valid_client_id,
        )

    def test_extract_user_data_success(self):
        """Test d'extraction des données utilisateur depuis le token décodé."""
        result = apple_auth_service._extract_user_data(self.valid_decoded_token)
        self._assert_apple_user_data(
            result,
            email='user@example.com',
            sub='apple-sub-id',
            given_name='John',
            family_name='Doe',
        )

    def test_extract_user_data_missing_sub_raises_exception(self):
        """Test qu'un sub manquant lève une exception."""
        decoded = {k: v for k, v in self.valid_decoded_token.items() if k != 'sub'}
        with self.assertRaises(BridgeQuestException):
            apple_auth_service._extract_user_data(decoded)

    def test_extract_user_data_empty_sub_raises_exception(self):
        """Test qu'un sub vide lève une exception."""
        decoded = {**self.valid_decoded_token, 'sub': ''}
        with self.assertRaises(BridgeQuestException):
            apple_auth_service._extract_user_data(decoded)

    def test_extract_user_data_missing_email_raises_exception(self):
        """Test qu'un email manquant lève une exception."""
        decoded = {k: v for k, v in self.valid_decoded_token.items() if k != 'email'}
        with self.assertRaises(BridgeQuestException):
            apple_auth_service._extract_user_data(decoded)

    def test_extract_user_data_empty_email_raises_exception(self):
        """Test qu'un email vide lève une exception."""
        decoded = {**self.valid_decoded_token, 'email': ''}
        with self.assertRaises(BridgeQuestException):
            apple_auth_service._extract_user_data(decoded)

    def test_extract_user_data_handles_missing_optional_fields(self):
        """Test que les champs optionnels absents sont renvoyés comme chaînes vides."""
        decoded = {'sub': 'apple-sub-id', 'email': 'minimal@example.com'}
        result = apple_auth_service._extract_user_data(decoded)
        self._assert_apple_user_data(
            result,
            email='minimal@example.com',
            sub='apple-sub-id',
        )
