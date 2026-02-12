"""
Service de diffusion WebSocket pour la partie en cours.

Diffuse les événements de jeu aux clients connectés au canal game.
Canal séparé du lobby (salle d'attente).

Événements diffusés :
- position_updated : mise à jour de position d'un joueur.
- roles_assigned : rôles attribués à chaque joueur (fin du déploiement).
- game_in_progress : partie en cours, inclut game_ends_at.
- game_finished : partie terminée, scores finaux et classement.
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def get_game_group_name(game_id):
    """Retourne le nom du groupe WebSocket pour une partie en cours."""
    return f"game_{game_id}"


def _send_to_game(game_id, event_type, **event_payload):
    """
    Envoie un événement au groupe game.

    Args:
        game_id: Identifiant de la partie (pour le nom du groupe).
        event_type: Type de l'événement.
        **event_payload: Données de l'événement envoyées aux clients.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        get_game_group_name(game_id),
        {"type": event_type, **event_payload},
    )


def broadcast_position_updated(position):
    """
    Diffuse une mise à jour de position aux clients du canal game.

    Appelé après chaque POST /api/locations/ réussi. Les clients connectés
    à ws/game/{game_id}/ reçoivent position_updated sans polling.

    Args:
        position: Instance Position avec player et player.user chargés.
    """
    from accounts.serializers.user_serializers import UserPublicSerializer

    user_data = UserPublicSerializer(position.player.user).data
    _send_to_game(
        position.player.game_id,
        "position_updated",
        player_id=position.player_id,
        user=user_data,
        latitude=str(position.latitude),
        longitude=str(position.longitude),
        recorded_at=position.recorded_at.isoformat(),
    )


def broadcast_roles_assigned(game_id, roles_data):
    """
    Diffuse les rôles attribués aux joueurs (fin du déploiement).

    Chaque client reçoit la liste complète pour afficher
    les rôles de tous les joueurs.

    Args:
        game_id: Identifiant de la partie.
        roles_data: Liste de dicts joueur avec leur rôle.
    """
    _send_to_game(game_id, "roles_assigned", players=roles_data)


def broadcast_game_in_progress(game_id, *, game_ends_at):
    """
    Diffuse le passage en phase IN_PROGRESS.

    Les clients utilisent ``game_ends_at`` pour afficher le
    compte à rebours de la partie.

    Args:
        game_id: Identifiant de la partie.
        game_ends_at: ISO 8601 datetime de fin de partie.
    """
    _send_to_game(
        game_id,
        "game_in_progress",
        game_id=game_id,
        game_ends_at=game_ends_at,
    )


def broadcast_game_finished(game_id, scores_data):
    """
    Diffuse la fin de la partie avec les scores finaux.

    Les clients affichent le classement et les résultats.

    Args:
        game_id: Identifiant de la partie.
        scores_data: Liste de dicts joueur triée par score décroissant.
    """
    _send_to_game(game_id, "game_finished", game_id=game_id, scores=scores_data)
