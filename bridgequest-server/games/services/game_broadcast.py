"""
Service de diffusion WebSocket pour la partie en cours.

Diffuse les événements de jeu (positions, conversions, etc.) aux clients
connectés au canal game. Canal séparé du lobby (salle d'attente).
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def get_game_group_name(game_id):
    """Retourne le nom du groupe WebSocket pour une partie en cours."""
    return f"game_{game_id}"


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
    payload = {
        "player_id": position.player_id,
        "user": user_data,
        "latitude": str(position.latitude),
        "longitude": str(position.longitude),
        "recorded_at": position.recorded_at.isoformat(),
    }

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        get_game_group_name(position.player.game_id),
        {
            "type": "position_updated",
            **payload,
        },
    )
