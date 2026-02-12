"""
Service de calcul des scores pour Bridge Quest.

Scoring en deux phases :

1. **Déploiement** (tous les joueurs) :
   Tous les joueurs accumulent des points passifs pendant la phase
   de déploiement (avant l'attribution des rôles). Persistés en base
   à la transition DEPLOYMENT -> IN_PROGRESS via ``apply_deployment_scores``.

2. **IN_PROGRESS** (Humains uniquement) :
   Seuls les joueurs encore Humains à la fin de la partie reçoivent
   des points passifs supplémentaires. Un Humain converti en Esprit
   passe au système de scoring Esprit et ne reçoit plus de points
   passifs pour la phase IN_PROGRESS.

Les points de conversion (Esprit convertit un Humain) sont appliqués
en temps réel lors de l'interaction et ne sont pas recalculés ici.
"""
import datetime

from django.utils import timezone

from games.models import Player, PlayerRole
from games.services.player_payload import build_player_websocket_payload


def apply_deployment_scores(game):
    """
    Applique les points passifs de la phase de déploiement à tous les joueurs.

    Pendant le déploiement, tous les joueurs sont techniquement Humains
    et accumulent ``deployment_duration * points_per_minute`` points.
    Cette fonction est appelée par ``lifecycle_service.begin_in_progress``
    juste après l'attribution des rôles, afin que les scores soient
    persistés en base avant le début de la phase IN_PROGRESS.

    Cela garantit que les conversions en début de partie ont de la
    valeur (le score de l'Humain converti inclut ses points de déploiement).

    Args:
        game: La partie (doit avoir ``settings`` pré-chargé).
    """
    settings = game.settings
    deployment_points = _compute_passive_score(
        settings.deployment_duration, settings.points_per_minute,
    )

    if deployment_points <= 0:
        return

    players = list(game.players.all())
    for player in players:
        player.score += deployment_points
    Player.objects.bulk_update(players, ["score"])


def _compute_in_progress_start(game, settings):
    """
    Calcule le moment où la phase IN_PROGRESS a débuté.

    Déduit à partir de ``game_ends_at - game_duration``.

    Args:
        game: La partie (doit avoir ``game_ends_at`` renseigné).
        settings: GameSettings de la partie.

    Returns:
        datetime: Début de la phase IN_PROGRESS.
    """
    return game.game_ends_at - datetime.timedelta(
        minutes=settings.game_duration,
    )


def _compute_human_minutes(player, game_start, game_end):
    """
    Calcule le temps passé en tant qu'Humain pendant IN_PROGRESS (en minutes).

    Seuls les joueurs encore Humains à la fin de la partie reçoivent
    des points passifs pour la phase IN_PROGRESS. Un joueur converti
    en Esprit passe au système de scoring Esprit (pas de points passifs).

    Deux cas :
    - Humain non converti (role=HUMAN) : durée complète de la phase IN_PROGRESS.
    - Esprit (initial ou converti) : 0 minute (scoring Esprit).

    Args:
        player: Le joueur.
        game_start: Début de la phase IN_PROGRESS.
        game_end: Fin de la partie (now ou game_ends_at).

    Returns:
        float: Minutes passées en tant qu'Humain (>= 0).
    """
    if player.role != PlayerRole.HUMAN:
        return 0.0

    seconds = (game_end - game_start).total_seconds()
    return max(seconds / 60, 0.0)


def _compute_passive_score(minutes, points_per_minute):
    """
    Calcule le score passif (minutes * points par minute).

    Utilisé pour le déploiement (tous les joueurs) et pour
    la phase IN_PROGRESS (Humains uniquement).

    Args:
        minutes: Durée en minutes.
        points_per_minute: Points accordés par minute (configurable).

    Returns:
        int: Score passif (arrondi à l'entier le plus proche).
    """
    return round(minutes * points_per_minute)


def _apply_passive_scores(players, game_start, game_end, points_per_minute):
    """
    Calcule et ajoute les scores passifs à chaque joueur.

    Met à jour le champ ``score`` en place puis sauvegarde
    via ``bulk_update`` en une seule requête.

    Args:
        players: Liste des joueurs.
        game_start: Début de la phase IN_PROGRESS.
        game_end: Fin de la partie.
        points_per_minute: Points par minute (configurable).
    """
    for player in players:
        human_minutes = _compute_human_minutes(player, game_start, game_end)
        player.score += _compute_passive_score(
            human_minutes, points_per_minute,
        )
    Player.objects.bulk_update(players, ["score"])


def _build_scores_payload(players):
    """
    Construit le payload de scores pour le broadcast WebSocket.

    Trie les joueurs par score décroissant (classement).

    Args:
        players: Liste des joueurs avec score mis à jour.

    Returns:
        list[dict]: Chaque dict contient player_id, user_id, username, role, score.
    """
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


def calculate_final_scores(game):
    """
    Calcule les scores finaux de tous les joueurs.

    Ajoute les points passifs (temps en tant qu'Humain) au score
    existant, sauvegarde en base, et retourne le classement.

    Les points de conversion (Esprit -> Humain) sont déjà
    comptabilisés dans ``player.score`` au moment de l'interaction
    et ne sont pas recalculés ici.

    Args:
        game: La partie (state IN_PROGRESS, sur le point de passer FINISHED).

    Returns:
        list[dict]: Liste triée par score décroissant.
            Chaque dict contient : player_id, user_id, username, role, score.
    """
    settings = game.settings
    players = list(game.players.select_related("user").all())

    game_start = _compute_in_progress_start(game, settings)
    game_end = timezone.now()

    _apply_passive_scores(
        players, game_start, game_end, settings.points_per_minute,
    )

    return _build_scores_payload(players)
