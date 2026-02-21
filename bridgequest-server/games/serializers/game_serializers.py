"""
Serializers pour le module Games.

Ces serializers gèrent la sérialisation/désérialisation des données de parties.
"""
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from accounts.serializers.user_serializers import UserPublicSerializer
from games.models import Game, GameSettings, Player
from utils.messages import ErrorMessages, ModelMessages
from utils.validators import validate_game_code


class JoinGameSerializer(serializers.Serializer):
    """
    Serializer pour rejoindre une partie via son code.

    Accepte un code de 6 caractères alphanumériques.
    """

    code = serializers.CharField(
        label=_(ModelMessages.GAME_CODE),
        help_text=_(ModelMessages.GAME_CODE),
        max_length=6,
        min_length=6,
        trim_whitespace=True,
    )

    def validate_code(self, value):
        """Valide le format alphanumérique et normalise le code (majuscules)."""
        if not value:
            return value
        normalized = value.strip()
        try:
            validate_game_code(normalized)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages[0] if e.messages else str(e))
        return normalized.upper()


class GameSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer pour les paramètres d'une partie.

    Expose les champs configurables. Le champ `game` n'est pas
    exposé (déduit du contexte URL).

    Validations métier appliquées :
    - Durées (game_duration, deployment_duration) : minimum 1 minute
    - Pourcentages (spirit_percentage, conversion_points_percentage) : 0-100
    - Points par minute : minimum 1
    """

    game_duration = serializers.IntegerField(
        validators=[
            MinValueValidator(1, message=_(ErrorMessages.SETTINGS_GAME_DURATION_TOO_LOW)),
        ],
        help_text=_(ModelMessages.SETTINGS_GAME_DURATION),
    )

    deployment_duration = serializers.IntegerField(
        validators=[
            MinValueValidator(
                1, message=_(ErrorMessages.SETTINGS_DEPLOYMENT_DURATION_TOO_LOW),
            ),
        ],
        help_text=_(ModelMessages.SETTINGS_DEPLOYMENT_DURATION),
    )

    spirit_percentage = serializers.IntegerField(
        validators=[
            MinValueValidator(
                0, message=_(ErrorMessages.SETTINGS_SPIRIT_PERCENTAGE_OUT_OF_RANGE),
            ),
            MaxValueValidator(
                100, message=_(ErrorMessages.SETTINGS_SPIRIT_PERCENTAGE_OUT_OF_RANGE),
            ),
        ],
        help_text=_(ModelMessages.SETTINGS_SPIRIT_PERCENTAGE),
    )

    points_per_minute = serializers.IntegerField(
        validators=[
            MinValueValidator(
                1, message=_(ErrorMessages.SETTINGS_POINTS_PER_MINUTE_TOO_LOW),
            ),
        ],
        help_text=_(ModelMessages.SETTINGS_POINTS_PER_MINUTE),
    )

    conversion_points_percentage = serializers.IntegerField(
        validators=[
            MinValueValidator(
                0,
                message=_(ErrorMessages.SETTINGS_CONVERSION_PERCENTAGE_OUT_OF_RANGE),
            ),
            MaxValueValidator(
                100,
                message=_(ErrorMessages.SETTINGS_CONVERSION_PERCENTAGE_OUT_OF_RANGE),
            ),
        ],
        help_text=_(ModelMessages.SETTINGS_CONVERSION_POINTS_PERCENTAGE),
    )

    class Meta:
        model = GameSettings
        fields = [
            'game_duration',
            'deployment_duration',
            'spirit_percentage',
            'points_per_minute',
            'conversion_points_percentage',
        ]


class GameSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Game.

    Expose les champs : id, code, state, created_at, updated_at, settings.

    Le champ `settings` est inclus pour permettre au client de récupérer
    l'état complet de la partie après reconnexion (GET /api/games/{id}/).
    """

    settings = GameSettingsSerializer(read_only=True)

    class Meta:
        model = Game
        fields = [
            'id',
            'code',
            'state',
            'created_at',
            'updated_at',
            'settings',
        ]
        read_only_fields = [
            'id',
            'code',
            'state',
            'created_at',
            'updated_at',
            'settings',
        ]


class PlayerSerializer(serializers.ModelSerializer):
    """
    Serializer pour un joueur dans une partie.

    Inclut les informations publiques de l'utilisateur.
    """

    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'user', 'is_admin', 'role', 'score', 'joined_at']
        read_only_fields = fields
