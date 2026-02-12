"""
Vues API pour le module Locations.

Gestion des mises à jour de position GPS.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from games.services.game_broadcast import broadcast_position_updated
from locations.serializers import PositionSerializer, UpdatePositionSerializer
from locations.services.position_service import update_position
from utils.exceptions import GameException, LocationException, PlayerException
from utils.responses import error_response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_position_view(request):
    """
    Met à jour la position GPS du joueur dans une partie.

    Body: {"game_id": int, "latitude": float, "longitude": float}
    La partie doit être en DEPLOYMENT ou IN_PROGRESS.
    """
    serializer = UpdatePositionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    try:
        position = update_position(
            game_id=data["game_id"],
            user=request.user,
            latitude=data["latitude"],
            longitude=data["longitude"],
        )
        broadcast_position_updated(position)
        return Response(
            PositionSerializer(position).data,
            status=status.HTTP_201_CREATED,
        )
    except (GameException, PlayerException, LocationException) as e:
        return error_response(e, getattr(e, "status_code", status.HTTP_400_BAD_REQUEST))
