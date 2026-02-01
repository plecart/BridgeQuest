"""
Service pour la génération et gestion des tokens JWT.

Ce service encapsule la logique de génération des tokens JWT pour l'authentification OAuth2.
"""
from rest_framework_simplejwt.tokens import RefreshToken


def generate_tokens_for_user(user):
    """
    Génère un access token et un refresh token pour un utilisateur.
    
    Args:
        user: L'instance User pour laquelle générer les tokens
        
    Returns:
        dict: Dictionnaire contenant 'access' et 'refresh' tokens
        
    Example:
        tokens = generate_tokens_for_user(user)
        # tokens = {
        #     'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
        #     'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
        # }
    """
    refresh = RefreshToken.for_user(user)
    
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }
