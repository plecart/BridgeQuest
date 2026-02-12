"""
Serializers pour le module Games.

Ces serializers gèrent la sérialisation/désérialisation des données de parties.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from accounts.serializers.user_serializers import UserPublicSerializer
from games.models import Game, Player
from utils.messages import ModelMessages
from utils.validators import validate_game_code


class GameSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Game.

    Expose les champs : id, code, state, created_at, updated_at.
    """

    class Meta:
        model = Game
        fields = ['id', 'code', 'state', 'created_at', 'updated_at']
        read_only_fields = ['id', 'code', 'state', 'created_at', 'updated_at']


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
