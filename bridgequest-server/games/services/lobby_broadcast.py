"""
Service de diffusion WebSocket pour la salle d'attente.

Diffuse les événements (joueur rejoint, joueur quitte, partie lancée,
exclusion, transfert admin) aux clients connectés au canal lobby.
Canal réservé à la phase WAITING.
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from games.models import GameState


def get_lobby_group_name(game_id):
    """Retourne le nom du groupe WebSocket pour la salle d'attente."""
    return f"lobby_{game_id}"


def _send_to_lobby(group_game_id, event_type, **event_payload):
    """
    Envoie un événement au groupe lobby.

    Args:
        group_game_id: Identifiant de la partie (pour le nom du groupe).
        event_type: Type de l'événement (ex: game_started, player_excluded).
        **event_payload: Données de l'événement envoyées aux clients.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        get_lobby_group_name(group_game_id),
        {"type": event_type, **event_payload},
    )


def broadcast_game_started(game_id):
    """
    Diffuse l'événement « partie lancée » aux clients de la salle d'attente.

    Appelé après start_game lorsqu'une partie passe en DEPLOYMENT.
    Les clients doivent se déconnecter du lobby et se connecter au canal
    ws/game/{game_id}/ pour recevoir les événements de partie.

    Args:
        game_id: Identifiant de la partie.
    """
    _send_to_lobby(game_id, "game_started", game_id=game_id, state=GameState.DEPLOYMENT)


def broadcast_player_excluded(game_id, player_payload):
    """
    Diffuse l'événement « joueur exclu » aux clients du lobby.

    Appelé après exclusion d'un joueur suite à une déconnexion
    prolongée (> 30 s sans reconnexion).

    Args:
        game_id: Identifiant de la partie.
        player_payload: dict avec player_id, user_id, username, is_admin.
    """
    _send_to_lobby(game_id, "player_excluded", player=player_payload)


def broadcast_admin_transferred(game_id, new_admin_payload):
    """
    Diffuse l'événement « admin transféré » aux clients du lobby.

    Appelé lorsque l'admin a été exclu et qu'un autre joueur
    reçoit les droits d'administration.

    Args:
        game_id: Identifiant de la partie.
        new_admin_payload: dict du nouveau joueur admin.
    """
    _send_to_lobby(game_id, "admin_transferred", new_admin=new_admin_payload)


def broadcast_game_deleted(game_id):
    """
    Diffuse l'événement « partie supprimée » aux clients du lobby.

    Appelé lorsque la partie est supprimée (admin exclu et plus
    aucun joueur restant). Les clients doivent quitter le lobby.

    Args:
        game_id: Identifiant de la partie supprimée.
    """
    _send_to_lobby(game_id, "game_deleted", game_id=game_id)
