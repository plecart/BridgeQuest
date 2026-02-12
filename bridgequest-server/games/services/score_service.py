"""
Service de calcul des scores pour Bridge Quest.

Calcule les scores finaux des joueurs à la fin de la partie :
- Humains : points par minute passée en tant qu'Humain.
- Esprits : points basés sur les conversions effectuées.
"""
from games.services.player_payload import build_player_websocket_payload


def calculate_final_scores(game):
    """
    Calcule les scores finaux de tous les joueurs.

    Args:
        game: La partie (state IN_PROGRESS, sur le point de passer FINISHED).

    Returns:
        list[dict]: Liste triée par score décroissant.
            Chaque dict contient : player_id, user (id, username), role, score.
    """
    # TODO(tâche F): calcul réel (points_per_minute, conversion_points_percentage)
    players = list(game.players.select_related("user").all())
    return sorted(
        [
            {
                **build_player_websocket_payload(player, include_admin=False),
                "role": player.role,
                "score": player.score,
            }
            for player in players
        ],
        key=lambda p: p["score"],
        reverse=True,
    )
