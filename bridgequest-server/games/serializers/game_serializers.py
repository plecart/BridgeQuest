"""
Serializers pour le module Games.

Ces serializers gèrent la sérialisation/désérialisation des données de parties.
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from accounts.serializers.user_serializers import UserPublicSerializer
from games.models import Game, Player
from utils.messages import ErrorMessages, ModelMessages


class GameSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Game.

    Expose les champs : id, code, name, state, created_at, updated_at.
    """

    class Meta:
        model = Game
        fields = ['id', 'code', 'name', 'state', 'created_at', 'updated_at']
        read_only_fields = ['id', 'code', 'state', 'created_at', 'updated_at']

    name = serializers.CharField(
        label=_(ModelMessages.GAME_NAME),
        help_text=_(ModelMessages.GAME_NAME),
        max_length=100,
    )


class CreateGameSerializer(serializers.Serializer):
    """
    Serializer pour la création d'une partie.

    Accepte uniquement le nom de la partie.
    """

    name = serializers.CharField(
        label=_(ModelMessages.GAME_NAME),
        help_text=_(ModelMessages.GAME_NAME),
        max_length=100,
        trim_whitespace=True,
    )

    def validate_name(self, value):
        """Valide que le nom n'est pas vide après trim."""
        if not value or not value.strip():
            raise serializers.ValidationError(_(ErrorMessages.GAME_NAME_REQUIRED))
        return value.strip()


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
        """Normalise le code (majuscules)."""
        if not value or len(value.strip()) != 6:
            return value
        return value.strip().upper()


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
