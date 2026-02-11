"""
Service de diffusion WebSocket pour la salle d'attente.

Diffuse les événements (joueur rejoint, joueur quitte, partie lancée) aux
clients connectés au canal lobby. Canal réservé à la phase WAITING.
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from games.models import GameState


def get_lobby_group_name(game_id):
    """Retourne le nom du groupe WebSocket pour la salle d'attente."""
    return f"lobby_{game_id}"


def broadcast_game_started(game_id):
    """
    Diffuse l'événement « partie lancée » aux clients de la salle d'attente.

    Appelé après start_game lorsqu'une partie passe en DEPLOYMENT.
    Les clients doivent se déconnecter du lobby et se connecter au canal
    ws/game/{game_id}/ pour recevoir les événements de partie.

    Args:
        game_id: Identifiant de la partie.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        get_lobby_group_name(game_id),
        {
            "type": "game_started",
            "game_id": game_id,
            "state": GameState.DEPLOYMENT,
        },
    )
