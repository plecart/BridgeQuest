"""
Construction des payloads joueur pour les événements WebSocket.

Payload minimal utilisé par les consumers et les broadcasts.
"""


def build_player_websocket_payload(player, *, include_admin=False):
    """
    Construit le payload minimal d'un joueur pour les événements WebSocket.

    Args:
        player: Instance Player avec user chargé (select_related).
        include_admin: Si True, inclut is_admin (pour le lobby).

    Returns:
        dict: {player_id, user_id, username} ou + is_admin si include_admin.
    """
    user = player.user
    payload = {
        "player_id": player.id,
        "user_id": user.id,
        "username": user.username or "",
    }
    if include_admin:
        payload["is_admin"] = player.is_admin
    return payload
