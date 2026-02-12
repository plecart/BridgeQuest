"""
Service d'attribution des rôles pour Bridge Quest.

Gère l'attribution aléatoire des rôles (Humain / Esprit)
à la fin de la phase de déploiement. Un pourcentage configurable
de joueurs est désigné Esprit (minimum 1, maximum N-1).
"""
import random

from games.models import Player, PlayerRole
from games.services.player_payload import build_player_websocket_payload


def _compute_spirit_count(total_players, spirit_percentage):
    """
    Calcule le nombre d'Esprits à attribuer.

    Garantit au moins 1 Esprit et au moins 1 Humain
    (si la partie compte 2 joueurs ou plus).

    Args:
        total_players: Nombre total de joueurs.
        spirit_percentage: Pourcentage cible d'Esprits (0-100).

    Returns:
        int: Nombre d'Esprits à désigner.
    """
    if total_players < 2:
        return 0

    raw = round(total_players * spirit_percentage / 100)
    return max(1, min(raw, total_players - 1))


def _select_spirits(players, spirit_count):
    """
    Sélectionne aléatoirement les joueurs qui deviendront Esprits.

    Args:
        players: Liste de tous les joueurs.
        spirit_count: Nombre d'Esprits à choisir.

    Returns:
        set[int]: Ensemble des player_id sélectionnés comme Esprits.
    """
    chosen = random.sample(players, spirit_count)
    return {player.id for player in chosen}


def _apply_roles(players, spirit_ids):
    """
    Applique les rôles aux joueurs et sauvegarde en base.

    Met à jour le champ ``role`` de chaque joueur (SPIRIT ou HUMAN)
    puis effectue un ``bulk_update`` pour économiser les requêtes.

    Args:
        players: Liste de tous les joueurs.
        spirit_ids: Ensemble des player_id désignés Esprits.
    """
    for player in players:
        player.role = (
            PlayerRole.SPIRIT if player.id in spirit_ids
            else PlayerRole.HUMAN
        )
    Player.objects.bulk_update(players, ["role"])


def _build_roles_payload(players):
    """
    Construit le payload de rôles pour le broadcast WebSocket.

    Args:
        players: Liste des joueurs avec rôle mis à jour.

    Returns:
        list[dict]: Chaque dict contient player_id, user_id, username, role.
    """
    return [
        {
            **build_player_websocket_payload(player, include_admin=False),
            "role": player.role,
        }
        for player in players
    ]


def assign_roles(game, spirit_percentage):
    """
    Attribue les rôles aux joueurs de la partie.

    Sélectionne aléatoirement un pourcentage de joueurs comme Esprits
    (minimum 1, maximum N-1). Les autres restent Humains.
    Sauvegarde en base via ``bulk_update`` et retourne le payload
    pour le broadcast ``roles_assigned``.

    Args:
        game: La partie.
        spirit_percentage: Pourcentage de joueurs à convertir en Esprit (0-100).

    Returns:
        list[dict]: Liste des joueurs avec leur rôle attribué.
            Chaque dict contient : player_id, user_id, username, role.
    """
    players = list(game.players.select_related("user").all())
    spirit_count = _compute_spirit_count(len(players), spirit_percentage)

    if spirit_count > 0:
        spirit_ids = _select_spirits(players, spirit_count)
        _apply_roles(players, spirit_ids)

    return _build_roles_payload(players)
