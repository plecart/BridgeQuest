"""
Service de gestion de la salle d'attente.

Logique métier : exclusion des joueurs après déconnexion (délai 30 s),
transfert des droits admin, suppression de la partie si vide.
"""
from django.core.cache import cache
from django.utils import timezone

from games.models import Game, GameState, Player
from games.services import lobby_broadcast
from games.services.player_payload import build_player_websocket_payload

# Délai en secondes avant exclusion (spec: 30 s)
LOBBY_DISCONNECT_GRACE_SECONDS = 30
_CACHE_KEY_PREFIX = "lobby_pending_exclusion"
_CACHE_TIMEOUT = LOBBY_DISCONNECT_GRACE_SECONDS + 10  # TTL légèrement supérieur


def _cache_key(game_id, player_id):
    """Clé de cache pour une exclusion en attente."""
    return f"{_CACHE_KEY_PREFIX}:{game_id}:{player_id}"


def mark_player_disconnected(game_id, player_id):
    """
    Marque un joueur comme déconnecté, démarrant le délai d'exclusion.

    Appelé lors de la déconnexion WebSocket du LobbyConsumer.
    Si le joueur se reconnecte avant 30 s, appeler cancel_pending_exclusion
    pour annuler.

    Args:
        game_id: Identifiant de la partie.
        player_id: Identifiant du joueur.
    """
    cache.set(
        _cache_key(game_id, player_id),
        timezone.now().isoformat(),
        timeout=_CACHE_TIMEOUT,
    )


def cancel_pending_exclusion(game_id, player_id):
    """
    Annule une exclusion en attente (joueur reconnecté).

    Appelé lors de la reconnexion WebSocket du joueur au lobby.

    Args:
        game_id: Identifiant de la partie.
        player_id: Identifiant du joueur.
    """
    cache.delete(_cache_key(game_id, player_id))


def exclude_player_from_lobby(game_id, player_id):
    """
    Exclut un joueur de la partie après le délai de grâce.

    Appelé 30 secondes après la déconnexion. Si le joueur s'est reconnecté,
    la clé cache est supprimée et la fonction ne fait rien.

    Logique :
    - Supprime le joueur de la partie
    - Si c'était l'admin : transfère les droits au joueur restant le plus ancien
    - S'il ne reste aucun joueur : supprime la partie et diffuse game_deleted

    Args:
        game_id: Identifiant de la partie.
        player_id: Identifiant du joueur à exclure.
    """
    key = _cache_key(game_id, player_id)
    if cache.get(key) is None:
        return  # Joueur reconnecté, ne rien faire

    cache.delete(key)

    try:
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        return

    if game.state != GameState.WAITING:
        return

    try:
        player = Player.objects.select_related("user").get(pk=player_id, game=game)
    except Player.DoesNotExist:
        return

    was_admin = player.is_admin
    player_payload = build_player_websocket_payload(player, include_admin=True)

    player.delete()
    lobby_broadcast.broadcast_player_excluded(game_id, player_payload)

    if was_admin:
        _handle_admin_exclusion(game)


def _handle_admin_exclusion(game):
    """
    Gère l'exclusion de l'administrateur.

    Transfère les droits au joueur restant le plus ancien, ou supprime
    la partie s'il ne reste aucun joueur.
    """
    next_admin = (
        Player.objects.filter(game=game)
        .select_related("user")
        .order_by("joined_at")
        .first()
    )

    if next_admin is None:
        game_id = game.id
        game.delete()
        lobby_broadcast.broadcast_game_deleted(game_id)
    else:
        next_admin.is_admin = True
        next_admin.save(update_fields=["is_admin"])
        lobby_broadcast.broadcast_admin_transferred(
            game.id,
            build_player_websocket_payload(next_admin, include_admin=True),
        )
