"""
Serializers pour le module Accounts.

Ces serializers gèrent la sérialisation/désérialisation des données utilisateur.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from utils.messages import ModelMessages

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle User.
    
    Utilisé pour exposer les informations utilisateur via l'API.
    """
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'date_joined',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'date_joined',
            'created_at',
            'updated_at',
        ]
    
    username = serializers.CharField(
        label=_(ModelMessages.USER_USERNAME),
        help_text=_(ModelMessages.USER_USERNAME)
    )
    
    email = serializers.EmailField(
        label=_(ModelMessages.USER_EMAIL),
        help_text=_(ModelMessages.USER_EMAIL)
    )
    
    first_name = serializers.CharField(
        label=_(ModelMessages.USER_FIRST_NAME),
        help_text=_(ModelMessages.USER_FIRST_NAME),
        required=False,
        allow_blank=True
    )
    
    last_name = serializers.CharField(
        label=_(ModelMessages.USER_LAST_NAME),
        help_text=_(ModelMessages.USER_LAST_NAME),
        required=False,
        allow_blank=True
    )
    
    avatar = serializers.URLField(
        label=_(ModelMessages.USER_AVATAR),
        help_text=_(ModelMessages.USER_AVATAR),
        required=False,
        allow_blank=True
    )


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Serializer public pour le modèle User.
    
    Utilisé pour exposer uniquement les informations publiques d'un utilisateur.
    """
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
        ]
        read_only_fields = ['id']
    
    username = serializers.CharField(
        label=_(ModelMessages.USER_USERNAME)
    )
    
    first_name = serializers.CharField(
        label=_(ModelMessages.USER_FIRST_NAME),
        required=False
    )
    
    last_name = serializers.CharField(
        label=_(ModelMessages.USER_LAST_NAME),
        required=False
    )
    
    avatar = serializers.URLField(
        label=_(ModelMessages.USER_AVATAR),
        required=False
    )
