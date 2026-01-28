"""
Tests pour les services du module Accounts.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch
from accounts.services.auth_service import get_or_create_user_from_social_account, get_user_by_email
from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages

User = get_user_model()


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
    
    def _create_mock_social_account(self, user=None, extra_data=None):
        """
        Helper pour créer un mock SocialAccount.
        
        Args:
            user: L'utilisateur associé (optionnel)
            extra_data: Les données extra du compte social
            
        Returns:
            Mock: Un mock SocialAccount
        """
        mock_account = Mock()
        mock_account.user = user
        mock_account.extra_data = extra_data or {}
        mock_account.save = Mock()
        return mock_account
    
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
    
    @patch('accounts.services.auth_service.SocialAccount')
    def test_get_or_create_user_from_social_account_existing_user(self, mock_social_account_class):
        """Test de récupération d'un utilisateur existant depuis un compte social."""
        # Arrange
        mock_social_account = self._create_mock_social_account(
            user=self.user,
            extra_data={
                'email': self.user_email,
                'given_name': 'Test',
                'family_name': 'User',
                'picture': 'https://example.com/avatar.jpg'
            }
        )
        
        # Act
        user = get_or_create_user_from_social_account(mock_social_account)
        
        # Assert
        self.assertEqual(user, self.user)
        mock_social_account.save.assert_not_called()
    
    @patch('accounts.services.auth_service.SocialAccount')
    def test_get_or_create_user_from_social_account_new_user(self, mock_social_account_class):
        """Test de création d'un nouvel utilisateur depuis un compte social."""
        # Arrange
        new_email = 'newuser@example.com'
        mock_social_account = self._create_mock_social_account(
            user=None,
            extra_data={
                'email': new_email,
                'given_name': 'New',
                'family_name': 'User',
                'picture': 'https://example.com/newavatar.jpg'
            }
        )
        
        # Act
        user = get_or_create_user_from_social_account(mock_social_account)
        
        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.email, new_email)
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.avatar, 'https://example.com/newavatar.jpg')
        mock_social_account.save.assert_called_once()
    
    @patch('accounts.services.auth_service.SocialAccount')
    def test_get_or_create_user_from_social_account_no_email_raises_exception(self, mock_social_account_class):
        """Test qu'un compte social sans email lève une exception."""
        # Arrange
        mock_social_account = self._create_mock_social_account(
            user=None,
            extra_data={}
        )
        
        # Act & Assert
        with self.assertRaises(BridgeQuestException):
            get_or_create_user_from_social_account(mock_social_account)
    
    @patch('accounts.services.auth_service.SocialAccount')
    def test_get_or_create_user_from_social_account_existing_email_links_account(self, mock_social_account_class):
        """Test qu'un email existant lie le compte social à l'utilisateur."""
        # Arrange
        existing_email = 'existing@example.com'
        existing_user = User.objects.create_user(
            username='existing',
            email=existing_email
        )
        
        mock_social_account = self._create_mock_social_account(
            user=None,
            extra_data={
                'email': existing_email,
                'given_name': 'Existing',
                'family_name': 'User'
            }
        )
        
        # Act
        user = get_or_create_user_from_social_account(mock_social_account)
        
        # Assert
        self.assertEqual(user, existing_user)
        mock_social_account.save.assert_called_once()
