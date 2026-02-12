"""
Vues API pour le module Games.

Ces vues gèrent les endpoints de création, jonction et consultation des parties.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from games.models import GameState
from games.serializers import (
    GameSerializer,
    GameSettingsSerializer,
    JoinGameSerializer,
    PlayerSerializer,
)
from games.services import (
    create_game,
    get_game_by_id,
    get_game_settings,
    get_player_in_game,
    join_game,
    start_game,
)
from games.services import lobby_broadcast
from locations.serializers import PositionWithPlayerSerializer
from locations.services.position_service import get_latest_positions_for_game
from utils.exceptions import GameException, PlayerException
from utils.messages import ErrorMessages
from utils.responses import error_response


def _game_detail_response(game):
    """Construit la réponse de détail d'une partie."""
    return Response(GameSerializer(game).data, status=status.HTTP_200_OK)


def _game_players_response(game):
    """Construit la réponse liste des joueurs d'une partie."""
    players = game.players.select_related("user").all()
    return Response(
        PlayerSerializer(players, many=True).data,
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_game_view(request):
    """
    Crée une nouvelle partie.

    L'utilisateur authentifié devient administrateur de la partie.
    Body: {} (aucun champ requis)
    """
    try:
        game = create_game(request.user)
        return Response(
            GameSerializer(game).data,
            status=status.HTTP_201_CREATED,
        )
    except GameException as e:
        return error_response(e, e.status_code)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_game_view(request):
    """
    Rejoint une partie via son code.

    Body: {"code": "ABC123"}
    Retourne la partie rejointe.
    """
    serializer = JoinGameSerializer(data=request.data)
    if not serializer.is_valid():
        first_error = next(iter(serializer.errors.values()))[0]
        return error_response(first_error, status.HTTP_400_BAD_REQUEST)

    try:
        player = join_game(serializer.validated_data["code"], request.user)
        return Response(
            GameSerializer(player.game).data,
            status=status.HTTP_200_OK,
        )
    except (GameException, PlayerException) as e:
        return error_response(e, e.status_code)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def game_detail_view(request, pk):
    """
    Récupère les détails d'une partie.

    GET /api/games/{id}/
    """
    try:
        game = get_game_by_id(pk)
        return _game_detail_response(game)
    except GameException as e:
        return error_response(e, e.status_code)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def game_players_view(request, pk):
    """
    Récupère la liste des joueurs d'une partie.

    GET /api/games/{id}/players/
    """
    try:
        game = get_game_by_id(pk)
        return _game_players_response(game)
    except GameException as e:
        return error_response(e, e.status_code)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def game_start_view(request, pk):
    """
    Lance une partie (administrateur uniquement).

    Passe la partie de WAITING à DEPLOYMENT.
    POST /api/games/{id}/start/
    """
    try:
        game = start_game(pk, request.user)
        return _game_detail_response(game)
    except (GameException, PlayerException) as e:
        return error_response(e, e.status_code)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def game_positions_view(request, pk):
    """
    Récupère les dernières positions de tous les joueurs de la partie.

    L'utilisateur doit faire partie de la partie.
    GET /api/games/{id}/positions/
    """
    try:
        game = get_game_by_id(pk)
        get_player_in_game(game, request.user)

        positions = get_latest_positions_for_game(game)
        data = PositionWithPlayerSerializer(positions, many=True).data
        return Response(data, status=status.HTTP_200_OK)
    except (GameException, PlayerException) as e:
        return error_response(e, e.status_code)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def game_settings_view(request, pk):
    """
    Consulte ou met à jour les paramètres d'une partie.

    GET  /api/games/{id}/settings/ — tout joueur de la partie.
    PATCH /api/games/{id}/settings/ — admin uniquement, state=WAITING.
    Diffuse settings_updated via le lobby WebSocket après modification.
    """
    try:
        game = get_game_by_id(pk)
        player = get_player_in_game(game, request.user)
        settings = get_game_settings(game)

        if request.method == "GET":
            return Response(
                GameSettingsSerializer(settings).data,
                status=status.HTTP_200_OK,
            )

        return _handle_settings_update(game, player, settings, request.data)
    except (GameException, PlayerException) as e:
        return error_response(e, e.status_code)


def _handle_settings_update(game, player, settings, data):
    """
    Traite la mise à jour des paramètres (PATCH).

    Vérifie les permissions, valide, sauvegarde et diffuse.

    Args:
        game: La partie.
        player: Le joueur qui fait la requête.
        settings: Les paramètres actuels.
        data: Données de la requête PATCH.

    Returns:
        Response: Les paramètres mis à jour.
    """
    if not player.is_admin:
        raise PlayerException(
            message_key=ErrorMessages.PLAYER_NOT_ADMIN,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if game.state != GameState.WAITING:
        raise GameException(
            message_key=ErrorMessages.SETTINGS_GAME_NOT_WAITING,
        )

    serializer = GameSettingsSerializer(settings, data=data, partial=True)
    if not serializer.is_valid():
        first_error = next(iter(serializer.errors.values()))[0]
        return error_response(first_error, status.HTTP_400_BAD_REQUEST)

    serializer.save()
    lobby_broadcast.broadcast_settings_updated(game.id, serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK)
