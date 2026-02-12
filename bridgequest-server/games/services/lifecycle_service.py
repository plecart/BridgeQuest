"""
Service de gestion du cycle de vie d'une partie.

Orchestre les transitions d'état automatiques :
WAITING → DEPLOYMENT → IN_PROGRESS → FINISHED

Chaque transition met à jour l'état, calcule les timestamps de fin
de phase, délègue aux services spécialisés (rôles, scores) et
diffuse l'événement correspondant via WebSocket.
"""
import datetime

from django.utils import timezone

from games.models import GameState
from games.services import game_broadcast, lobby_broadcast
from utils.exceptions import GameException
from utils.messages import ErrorMessages

_MIN_PLAYERS_TO_START = 2


def _require_enough_players(game):
    """
    Vérifie que la partie a assez de joueurs pour démarrer.

    Minimum 2 joueurs requis pour garantir au moins 1 Humain et 1 Esprit.

    Args:
        game: La partie.

    Raises:
        GameException: Si le nombre de joueurs est insuffisant.
    """
    player_count = game.players.count()
    if player_count < _MIN_PLAYERS_TO_START:
        raise GameException(
            message_key=ErrorMessages.GAME_NOT_ENOUGH_PLAYERS,
        )


def begin_deployment(game):
    """
    Lance la phase de déploiement (WAITING → DEPLOYMENT).

    Vérifie qu'il y a au moins 2 joueurs, calcule ``deployment_ends_at``
    à partir du paramètre ``deployment_duration`` (en minutes) et diffuse
    ``game_started`` aux clients du lobby. Les clients doivent ensuite se
    déconnecter du lobby et se connecter au canal ``ws/game/``.

    Args:
        game: La partie (state doit être WAITING, min 2 joueurs).

    Raises:
        GameException: Si la partie n'est pas en WAITING ou pas assez de joueurs.
    """
    if game.state != GameState.WAITING:
        raise GameException(message_key=ErrorMessages.GAME_ALREADY_STARTED)

    _require_enough_players(game)

    settings = game.settings
    now = timezone.now()
    deployment_ends_at = now + datetime.timedelta(
        minutes=settings.deployment_duration,
    )

    game.state = GameState.DEPLOYMENT
    game.deployment_ends_at = deployment_ends_at
    game.save(update_fields=["state", "deployment_ends_at", "updated_at"])

    lobby_broadcast.broadcast_game_started(
        game.id,
        deployment_ends_at=deployment_ends_at.isoformat(),
    )


def begin_in_progress(game):
    """
    Lance la phase de jeu (DEPLOYMENT → IN_PROGRESS).

    Attribue les rôles (via ``role_service``), calcule ``game_ends_at``
    à partir du paramètre ``game_duration`` (en minutes), et diffuse
    ``roles_assigned`` puis ``game_in_progress`` aux clients du canal game.

    Args:
        game: La partie (state doit être DEPLOYMENT).

    Raises:
        GameException: Si la partie n'est pas en DEPLOYMENT.
    """
    if game.state != GameState.DEPLOYMENT:
        raise GameException(message_key=ErrorMessages.GAME_NOT_DEPLOYMENT)

    from games.services.role_service import assign_roles

    settings = game.settings
    now = timezone.now()
    game_ends_at = now + datetime.timedelta(minutes=settings.game_duration)

    roles_data = assign_roles(game, settings.spirit_percentage)

    game.state = GameState.IN_PROGRESS
    game.game_ends_at = game_ends_at
    game.save(update_fields=["state", "game_ends_at", "updated_at"])

    game_broadcast.broadcast_roles_assigned(game.id, roles_data)
    game_broadcast.broadcast_game_in_progress(
        game.id,
        game_ends_at=game_ends_at.isoformat(),
    )


def finish_game(game):
    """
    Termine la partie (IN_PROGRESS → FINISHED).

    Calcule les scores finaux (via ``score_service``) et diffuse
    ``game_finished`` aux clients du canal game.

    Args:
        game: La partie (state doit être IN_PROGRESS).

    Raises:
        GameException: Si la partie n'est pas en IN_PROGRESS.
    """
    if game.state != GameState.IN_PROGRESS:
        raise GameException(message_key=ErrorMessages.GAME_NOT_IN_PROGRESS)

    from games.services.score_service import calculate_final_scores

    scores_data = calculate_final_scores(game)

    game.state = GameState.FINISHED
    game.save(update_fields=["state", "updated_at"])

    game_broadcast.broadcast_game_finished(game.id, scores_data)
