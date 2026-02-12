"""
Tests pour le service lobby_service.

Exclusion après déconnexion, transfert admin, suppression partie vide.
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from games.models import Game, GameState, Player
from games.services import lobby_service

User = get_user_model()


class LobbyServiceExclusionTestCase(TestCase):
    """Tests pour l'exclusion des joueurs en salle d'attente."""

    def setUp(self):
        """Configuration initiale pour tous les tests."""
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
        )
        self.player2 = User.objects.create_user(
            username="player2",
            email="player2@test.com",
        )
        self.game = Game.objects.create(code="ABC123")
        self.admin_player = Player.objects.create(
            user=self.admin,
            game=self.game,
            is_admin=True,
        )
        self.other_player = Player.objects.create(
            user=self.player2,
            game=self.game,
            is_admin=False,
        )

    def test_cancel_pending_exclusion_clears_cache(self):
        """Test que cancel_pending_exclusion supprime la clé cache."""
        from django.core.cache import cache

        lobby_service.mark_player_disconnected(self.game.id, self.other_player.id)
        key = f"lobby_pending_exclusion:{self.game.id}:{self.other_player.id}"
        self.assertIsNotNone(cache.get(key))
        lobby_service.cancel_pending_exclusion(self.game.id, self.other_player.id)
        self.assertIsNone(cache.get(key))

    def test_exclude_non_admin_player_removes_player(self):
        """Test que l'exclusion d'un joueur non-admin le retire de la partie."""
        lobby_service.mark_player_disconnected(self.game.id, self.other_player.id)
        with patch(
            "games.services.lobby_service.lobby_broadcast.broadcast_player_excluded"
        ) as mock_broadcast:
            lobby_service.exclude_player_from_lobby(
                self.game.id, self.other_player.id
            )
        self.assertFalse(
            Player.objects.filter(pk=self.other_player.id).exists()
        )
        mock_broadcast.assert_called_once()
        self.assertEqual(mock_broadcast.call_args[0][0], self.game.id)
        self.assertEqual(
            mock_broadcast.call_args[0][1]["player_id"],
            self.other_player.id,
        )

    def test_exclude_admin_transfers_to_next_player(self):
        """Test que l'exclusion de l'admin transfère les droits au joueur restant."""
        lobby_service.mark_player_disconnected(self.game.id, self.admin_player.id)
        with patch(
            "games.services.lobby_service.lobby_broadcast.broadcast_player_excluded"
        ), patch(
            "games.services.lobby_service.lobby_broadcast.broadcast_admin_transferred"
        ) as mock_transfer:
            lobby_service.exclude_player_from_lobby(
                self.game.id, self.admin_player.id
            )
        self.assertFalse(
            Player.objects.filter(pk=self.admin_player.id).exists()
        )
        new_admin = Player.objects.get(game=self.game)
        self.assertTrue(new_admin.is_admin)
        self.assertEqual(new_admin.user, self.player2)
        mock_transfer.assert_called_once()

    def test_exclude_admin_when_alone_deletes_game(self):
        """Test que l'exclusion de l'admin seul supprime la partie."""
        self.other_player.delete()
        game_id = self.game.id
        lobby_service.mark_player_disconnected(game_id, self.admin_player.id)

        with patch(
            "games.services.lobby_service.lobby_broadcast.broadcast_player_excluded"
        ), patch(
            "games.services.lobby_service.lobby_broadcast.broadcast_game_deleted"
        ) as mock_deleted:
            lobby_service.exclude_player_from_lobby(
                game_id, self.admin_player.id
            )
        self.assertFalse(Game.objects.filter(pk=game_id).exists())
        mock_deleted.assert_called_once_with(game_id)

    def test_exclude_does_nothing_if_player_reconnected(self):
        """Test que l'exclusion ne fait rien si le joueur s'est reconnecté."""
        lobby_service.mark_player_disconnected(self.game.id, self.other_player.id)
        lobby_service.cancel_pending_exclusion(self.game.id, self.other_player.id)

        lobby_service.exclude_player_from_lobby(
            self.game.id, self.other_player.id
        )
        self.assertTrue(
            Player.objects.filter(pk=self.other_player.id).exists()
        )

    def test_exclude_does_nothing_if_game_not_waiting(self):
        """Test que l'exclusion ne fait rien si la partie n'est plus en attente."""
        lobby_service.mark_player_disconnected(self.game.id, self.other_player.id)
        self.game.state = GameState.DEPLOYMENT
        self.game.save()
        with patch(
            "games.services.lobby_service.lobby_broadcast.broadcast_player_excluded"
        ) as mock_broadcast:
            lobby_service.exclude_player_from_lobby(
                self.game.id, self.other_player.id
            )
        self.assertTrue(
            Player.objects.filter(pk=self.other_player.id).exists()
        )
        mock_broadcast.assert_not_called()
