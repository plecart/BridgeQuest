"""
Tests pour les modèles du module Accounts.
"""
from django.test import TestCase
from accounts.models.user import User


class UserModelTestCase(TestCase):
    """Tests pour le modèle User."""
    
    def setUp(self):
        """Configuration initiale pour tous les tests."""
        self.test_username = 'testuser'
        self.test_email = 'test@example.com'
        self.test_password = 'testpass123'
    
    def test_create_user_success(self):
        """Test de création réussie d'un utilisateur."""
        # Arrange & Act
        user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )
        
        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.username, self.test_username)
        self.assertEqual(user.email, self.test_email)
        self.assertTrue(user.check_password(self.test_password))
    
    def test_user_str_representation_with_username(self):
        """Test de la représentation string avec username."""
        # Arrange & Act
        user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email
        )
        
        # Assert
        self.assertEqual(str(user), self.test_username)
    
    def test_user_str_representation_with_email_only(self):
        """Test de la représentation string avec email uniquement."""
        # Arrange & Act
        user = User(email=self.test_email)
        user.save()
        
        # Assert
        self.assertEqual(str(user), self.test_email)
    
    def test_get_full_name_with_first_and_last_name(self):
        """Test de get_full_name avec prénom et nom."""
        # Arrange & Act
        user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            first_name='John',
            last_name='Doe'
        )
        
        # Assert
        self.assertEqual(user.get_full_name(), 'John Doe')
    
    def test_get_full_name_without_names_falls_back_to_username(self):
        """Test de get_full_name sans prénom/nom retourne le username."""
        # Arrange & Act
        user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email
        )
        
        # Assert
        self.assertEqual(user.get_full_name(), self.test_username)
    
    def test_get_display_name_returns_full_name(self):
        """Test de get_display_name retourne le nom complet."""
        # Arrange & Act
        user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            first_name='John',
            last_name='Doe'
        )
        
        # Assert
        self.assertEqual(user.get_display_name(), 'John Doe')
    
    def test_user_avatar_field_stored_correctly(self):
        """Test que le champ avatar est stocké correctement."""
        # Arrange
        avatar_url = 'https://example.com/avatar.jpg'
        
        # Act
        user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            avatar=avatar_url
        )
        
        # Assert
        self.assertEqual(user.avatar, avatar_url)
    
    def test_user_timestamps_auto_set(self):
        """Test que created_at et updated_at sont automatiquement définis."""
        # Arrange & Act
        user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email
        )
        
        # Assert
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        self.assertIsNotNone(user.date_joined)
