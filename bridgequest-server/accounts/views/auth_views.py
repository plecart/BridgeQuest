"""
Vues API pour l'authentification dans le module Accounts.

Ces vues gèrent les endpoints d'authentification SSO.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import logout, get_user_model
from django.utils.translation import gettext_lazy as _
from accounts.serializers.user_serializers import UserSerializer, UserPublicSerializer
from utils.messages import ErrorMessages, Messages

User = get_user_model()


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
    
    Returns:
        Response: Message de confirmation
    """
    logout(request)
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
        return Response(
            {'error': _(ErrorMessages.USER_NOT_FOUND)},
            status=status.HTTP_404_NOT_FOUND
        )
