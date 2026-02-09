"""
Tests pour les services du module Accounts.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.services.auth_service import get_user_by_email, create_or_get_user_from_sso_data
from utils.exceptions import BridgeQuestException

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
