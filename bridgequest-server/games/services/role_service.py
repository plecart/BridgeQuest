"""
Service d'attribution des rôles pour Bridge Quest.

Gère l'attribution aléatoire des rôles (Humain / Esprit)
à la fin de la phase de déploiement.
"""
from games.services.player_payload import build_player_websocket_payload


def assign_roles(game, spirit_percentage):
    """
    Attribue les rôles aux joueurs de la partie.

    Sélectionne aléatoirement un pourcentage de joueurs comme Esprits
    (minimum 1). Les autres restent Humains.

    Args:
        game: La partie.
        spirit_percentage: Pourcentage de joueurs à convertir en Esprit.

    Returns:
        list[dict]: Liste des joueurs avec leur rôle attribué.
            Chaque dict contient : player_id, user (id, username), role.
    """
    # TODO(tâche E): sélection aléatoire, bulk_update, min 1 esprit
    players = list(game.players.select_related("user").all())
    return [
        {
            **build_player_websocket_payload(player, include_admin=False),
            "role": player.role,
        }
        for player in players
    ]
