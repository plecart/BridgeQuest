"""
Vues API pour le module Games.

Ces vues gèrent les endpoints de création, jonction et consultation des parties.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from games.serializers import (
    CreateGameSerializer,
    GameSerializer,
    JoinGameSerializer,
    PlayerSerializer,
)
from games.services import (
    create_game,
    get_game_by_id,
    get_player_in_game,
    join_game,
    start_game,
)
from locations.serializers import PositionWithPlayerSerializer
from locations.services.position_service import get_latest_positions_for_game
from utils.exceptions import GameException, PlayerException
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
    Body: {"name": "Nom de la partie"}
    """
    serializer = CreateGameSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        game = create_game(
            serializer.validated_data["name"],
            request.user,
        )
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
