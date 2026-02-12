"""
Service de gestion des parties pour Bridge Quest.

Contient la logique métier : création, jonction, récupération.
"""
import random
import string

from rest_framework import status

from games.models import Game, GameState, Player, PlayerRole
from games.services import lobby_broadcast
from utils.exceptions import GameException, PlayerException
from utils.messages import ErrorMessages

_CODE_LENGTH = 6
_CODE_CHARS = string.ascii_uppercase + string.digits


def generate_game_code():
    """
    Génère un code unique de 6 caractères pour une partie.

    Returns:
        str: Code alphanumérique majuscule de 6 caractères.
    """
    return "".join(random.choices(_CODE_CHARS, k=_CODE_LENGTH))


def _ensure_unique_code(code):
    """
    Garantit l'unicité du code en régénérant si nécessaire.

    Args:
        code: Code à vérifier.

    Returns:
        str: Code unique.
    """
    while Game.objects.filter(code=code).exists():
        code = generate_game_code()
    return code


def _add_player_to_game(game, user, *, is_admin=False):
    """
    Ajoute un joueur à une partie.

    Args:
        game: La partie.
        user: L'utilisateur.
        is_admin: Si True, le joueur est administrateur.

    Returns:
        Player: Le joueur créé.
    """
    return Player.objects.create(
        user=user,
        game=game,
        is_admin=is_admin,
        role=PlayerRole.HUMAN,
    )


def _normalize_game_code(code):
    """
    Normalise un code de partie pour la recherche.

    Args:
        code: Code saisi (peut être minuscules, espaces).

    Returns:
        str | None: Code normalisé (6 caractères majuscules) ou None si invalide.
    """
    if not code or not isinstance(code, str):
        return None
    normalized = code.strip().upper()
    if len(normalized) != _CODE_LENGTH:
        return None
    return normalized


def create_game(admin_user):
    """
    Crée une nouvelle partie avec l'utilisateur comme administrateur.

    Args:
        admin_user: Utilisateur créateur (sera admin de la partie).

    Returns:
        Game: La partie créée.
    """
    code = _ensure_unique_code(generate_game_code())
    game = Game.objects.create(code=code)
    _add_player_to_game(game, admin_user, is_admin=True)
    return game


def get_game_by_id(game_id):
    """
    Récupère une partie par son identifiant.

    Args:
        game_id: Identifiant de la partie.

    Returns:
        Game: La partie trouvée.

    Raises:
        GameException: Si la partie n'existe pas.
    """
    try:
        return Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        raise GameException(
            message_key=ErrorMessages.GAME_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )


def get_game_by_code(code):
    """
    Récupère une partie par son code.

    Args:
        code: Code de la partie (6 caractères, insensible à la casse).

    Returns:
        Game | None: La partie trouvée ou None.
    """
    normalized = _normalize_game_code(code)
    if normalized is None:
        return None
    try:
        return Game.objects.get(code=normalized)
    except Game.DoesNotExist:
        return None


def _require_game_waiting(game):
    """
    Vérifie que la partie est en attente.

    Args:
        game: La partie à vérifier.

    Raises:
        GameException: Si la partie a déjà commencé.
    """
    if game.state != GameState.WAITING:
        raise GameException(message_key=ErrorMessages.GAME_ALREADY_STARTED)


def get_player_in_game(game, user):
    """
    Récupère le joueur dans une partie, avec user chargé.

    Args:
        game: La partie.
        user: L'utilisateur recherché.

    Returns:
        Player: Le joueur trouvé.

    Raises:
        PlayerException: Si l'utilisateur n'est pas dans la partie.
    """
    try:
        return Player.objects.select_related("user").get(user=user, game=game)
    except Player.DoesNotExist:
        raise PlayerException(
            message_key=ErrorMessages.PLAYER_NOT_IN_GAME,
            status_code=status.HTTP_403_FORBIDDEN,
        )


def _validate_can_join_game(game, user):
    """
    Vérifie qu'un utilisateur peut rejoindre une partie.

    Args:
        game: La partie à rejoindre.
        user: L'utilisateur qui souhaite rejoindre.

    Raises:
        GameException: Si la partie n'est pas en attente.
        PlayerException: Si l'utilisateur est déjà dans la partie.
    """
    _require_game_waiting(game)
    if Player.objects.filter(user=user, game=game).exists():
        raise PlayerException(message_key=ErrorMessages.PLAYER_ALREADY_IN_GAME)


def join_game(code, user):
    """
    Fait rejoindre un utilisateur à une partie via son code.

    Args:
        code: Code de la partie (6 caractères).
        user: Utilisateur qui rejoint.

    Returns:
        Player: Le joueur créé dans la partie.

    Raises:
        GameException: Si le code est invalide ou la partie déjà commencée.
        PlayerException: Si l'utilisateur est déjà dans la partie.
    """
    game = get_game_by_code(code)
    if game is None:
        raise GameException(message_key=ErrorMessages.GAME_CODE_NOT_FOUND)

    _validate_can_join_game(game, user)
    return _add_player_to_game(game, user, is_admin=False)


def start_game(game_id, user):
    """
    Lance une partie (passe de WAITING à DEPLOYMENT).

    Seul l'administrateur de la partie peut lancer.

    Args:
        game_id: Identifiant de la partie.
        user: Utilisateur qui demande le lancement.

    Returns:
        Game: La partie mise à jour.

    Raises:
        GameException: Si la partie n'existe pas ou est déjà commencée.
        PlayerException: Si l'utilisateur n'est pas dans la partie ou n'est pas admin.
    """
    game = get_game_by_id(game_id)
    _require_game_waiting(game)

    player = get_player_in_game(game, user)
    if not player.is_admin:
        raise PlayerException(
            message_key=ErrorMessages.PLAYER_NOT_ADMIN,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    game.state = GameState.DEPLOYMENT
    game.save(update_fields=["state", "updated_at"])
    lobby_broadcast.broadcast_game_started(game.id)
    return game
