"""
Vues API pour l'authentification dans le module Accounts.

Ces vues gèrent les endpoints d'authentification SSO mobile.
"""
import logging

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.serializers.sso_serializers import SSOLoginSerializer
from accounts.serializers.user_serializers import UserPublicSerializer, UserSerializer
from accounts.services.apple_auth_service import validate_apple_token
from accounts.services.auth_service import create_or_get_user_from_sso_data
from accounts.services.google_auth_service import validate_google_token
from accounts.services.jwt_service import generate_tokens_for_user
from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages, Messages

User = get_user_model()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers privés (validation, construction de réponses)
# ---------------------------------------------------------------------------

def _validate_sso_token(provider, token):
    """
    Valide un token SSO selon le provider.

    Args:
        provider: Le fournisseur SSO ('google' ou 'apple')
        token: Le token à valider

    Returns:
        dict: Les données SSO validées

    Raises:
        BridgeQuestException: Si le provider est invalide ou la validation échoue
    """
    if provider == 'google':
        return validate_google_token(token)
    elif provider == 'apple':
        return validate_apple_token(token)
    else:
        raise BridgeQuestException(ErrorMessages.AUTH_SSO_PROVIDER_INVALID)


def _build_login_response(user, tokens):
    """
    Construit la réponse de connexion avec les informations utilisateur et les tokens JWT.

    Args:
        user: L'instance User authentifiée
        tokens: Dictionnaire contenant 'access' et 'refresh' tokens

    Returns:
        dict: Données de réponse formatées
    """
    user_serializer = UserSerializer(user)
    return {
        'user': user_serializer.data,
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'message': _(Messages.SSO_LOGIN_SUCCESS)
    }


def _build_error_response(error_message, status_code):
    """
    Construit une réponse d'erreur standardisée.

    Args:
        error_message: Le message d'erreur à retourner
        status_code: Le code de statut HTTP

    Returns:
        Response: Réponse d'erreur formatée
    """
    return Response(
        {'error': error_message},
        status=status_code
    )


def _build_validation_error_response(errors):
    """
    Construit une réponse d'erreur de validation.

    Args:
        errors: Les erreurs de validation du serializer

    Returns:
        Response: Réponse d'erreur de validation formatée
    """
    return Response(
        errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ---------------------------------------------------------------------------
# Vues API
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def sso_login_view(request):
    """
    Endpoint pour l'authentification SSO mobile avec OAuth2/JWT.
    
    L'application Flutter envoie le token SSO obtenu via les SDKs natifs
    (Google Sign-In, Apple Sign-In) pour validation et création de compte.
    Le serveur retourne des tokens JWT (access_token et refresh_token) pour
    l'authentification OAuth2 pure.
    
    Body:
        {
            "provider": "google" | "apple",
            "token": "token_id_jwt"
        }
        
    Returns:
        Response: Informations de l'utilisateur, access_token et refresh_token
        
    Example Response:
        {
            "user": {...},
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "message": "Connexion réussie"
        }
    """
    serializer = SSOLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return _build_validation_error_response(serializer.errors)
    
    provider = serializer.validated_data['provider']
    token = serializer.validated_data['token']
    
    try:
        sso_data = _validate_sso_token(provider, token)
        user = create_or_get_user_from_sso_data(sso_data, provider)
        tokens = generate_tokens_for_user(user)
        
        return Response(
            _build_login_response(user, tokens),
            status=status.HTTP_200_OK
        )
        
    except BridgeQuestException as e:
        return _build_error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception:
        logger.exception(
            _(Messages.LOG_AUTH_SSO_UNEXPECTED),
            provider,
        )
        return _build_error_response(
            _(ErrorMessages.AUTH_SSO_FAILED),
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Endpoint pour récupérer les informations de l'utilisateur actuellement connecté.
    
    Returns:
        Response: Informations de l'utilisateur au format JSON
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    Endpoint pour déconnecter l'utilisateur.
    
    Avec l'authentification JWT, la déconnexion est principalement gérée côté client
    (suppression des tokens). Ce endpoint existe pour la compatibilité et peut être
    utilisé pour blacklister un refresh token si nécessaire à l'avenir.
    
    Returns:
        Response: Message de confirmation
    """
    # Avec JWT stateless, la déconnexion est gérée côté client
    # Les tokens sont supprimés par l'application Flutter
    # Si besoin de blacklist à l'avenir, utiliser rest_framework_simplejwt.token_blacklist
    return Response(
        {'message': _(Messages.LOGOUT_SUCCESS)},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request, user_id):
    """
    Endpoint pour récupérer le profil public d'un utilisateur.
    
    Args:
        user_id: L'ID de l'utilisateur
        
    Returns:
        Response: Informations publiques de l'utilisateur
    """
    try:
        user = User.objects.get(pk=user_id)
        serializer = UserPublicSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return _build_error_response(
            _(ErrorMessages.USER_NOT_FOUND),
            status.HTTP_404_NOT_FOUND
        )
