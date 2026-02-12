"""
Tests pour le module player_payload.

Payload WebSocket des joueurs (consumers, lobby_service).
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from games.models import Game, Player
from games.services.player_payload import build_player_websocket_payload

User = get_user_model()


class PlayerPayloadTestCase(TestCase):
    """Tests pour build_player_websocket_payload."""

    def setUp(self):
        """Configuration initiale pour tous les tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
        )
        self.game = Game.objects.create(code="ABC123")
        self.player = Player.objects.create(
            user=self.user,
            game=self.game,
            is_admin=True,
        )

    def test_payload_without_admin_includes_base_fields(self):
        """Test que le payload sans is_admin contient les champs de base."""
        payload = build_player_websocket_payload(self.player, include_admin=False)
        self.assertEqual(payload["player_id"], self.player.id)
        self.assertEqual(payload["user_id"], self.user.id)
        self.assertEqual(payload["username"], "testuser")
        self.assertNotIn("is_admin", payload)

    def test_payload_with_admin_includes_is_admin(self):
        """Test que le payload avec include_admin inclut is_admin."""
        payload = build_player_websocket_payload(self.player, include_admin=True)
        self.assertEqual(payload["player_id"], self.player.id)
        self.assertTrue(payload["is_admin"])

    def test_payload_username_empty_fallback(self):
        """Test que username vide est remplacé par chaîne vide."""
        self.user.username = ""
        self.user.save()
        payload = build_player_websocket_payload(self.player, include_admin=False)
        self.assertEqual(payload["username"], "")
