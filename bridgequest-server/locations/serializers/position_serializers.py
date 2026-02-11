"""
Serializers pour le module Locations.

Gestion de la sérialisation des positions GPS.
"""
from decimal import Decimal

from accounts.serializers.user_serializers import UserPublicSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from locations.models import Position
from utils.messages import ErrorMessages, ModelMessages


class UpdatePositionSerializer(serializers.Serializer):
    """
    Serializer pour la mise à jour d'une position GPS.

    Body: {"game_id": int, "latitude": float, "longitude": float}
    """

    game_id = serializers.IntegerField(
        label=_(ModelMessages.GAME_VERBOSE_NAME),
        help_text=_("ID de la partie dans laquelle mettre à jour la position"),
    )

    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        label=_(ModelMessages.POSITION_LATITUDE),
        help_text=_("Latitude WGS84 (-90 à 90)"),
    )

    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        label=_(ModelMessages.POSITION_LONGITUDE),
        help_text=_("Longitude WGS84 (-180 à 180)"),
    )

    def validate_latitude(self, value):
        """Valide la plage de latitude."""
        if not (Decimal("-90") <= value <= Decimal("90")):
            raise serializers.ValidationError(
                _(ErrorMessages.POSITION_COORDINATES_INVALID)
            )
        return value

    def validate_longitude(self, value):
        """Valide la plage de longitude."""
        if not (Decimal("-180") <= value <= Decimal("180")):
            raise serializers.ValidationError(
                _(ErrorMessages.POSITION_COORDINATES_INVALID)
            )
        return value


class PositionSerializer(serializers.ModelSerializer):
    """
    Serializer pour une position GPS.

    Expose : id, player_id, latitude, longitude, recorded_at.
    """

    player_id = serializers.PrimaryKeyRelatedField(
        source="player",
        read_only=True,
    )

    class Meta:
        model = Position
        fields = ["id", "player_id", "latitude", "longitude", "recorded_at"]
        read_only_fields = fields


class PositionWithPlayerSerializer(serializers.ModelSerializer):
    """
    Serializer pour une position avec les infos du joueur.

    Utilisé pour GET /api/games/{id}/positions/.
    """

    player_id = serializers.IntegerField(read_only=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ["player_id", "user", "latitude", "longitude", "recorded_at"]

    def get_user(self, obj):
        """Sérialise l'utilisateur du joueur."""
        return UserPublicSerializer(obj.player.user).data
