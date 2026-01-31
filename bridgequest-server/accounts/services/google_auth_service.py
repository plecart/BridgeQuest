"""
Service de validation des tokens Google Sign-In pour Bridge Quest.

Ce service valide les tokens ID obtenus via Google Sign-In SDK
depuis l'application mobile Flutter.
"""
import requests
from django.utils.translation import gettext_lazy as _
from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages

# Constantes de configuration
GOOGLE_TOKEN_INFO_URL = 'https://oauth2.googleapis.com/tokeninfo'
REQUEST_TIMEOUT_SECONDS = 10


def validate_google_token(token):
    """
    Valide un token ID Google et retourne les informations de l'utilisateur.
    
    Args:
        token: Le token ID (JWT) obtenu via Google Sign-In SDK
        
    Returns:
        dict: Dictionnaire contenant les informations de l'utilisateur Google :
            - email: Email de l'utilisateur
            - given_name: Prénom
            - family_name: Nom de famille
            - picture: URL de l'avatar
            - sub: ID unique Google de l'utilisateur
            
    Raises:
        BridgeQuestException: Si la validation échoue
    """
    if not token:
        raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_REQUIRED))
    
    try:
        # Valider le token avec Google
        response = requests.get(
            GOOGLE_TOKEN_INFO_URL,
            params={'id_token': token},
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        
        if response.status_code != 200:
            raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED))
        
        token_info = response.json()
        
        # Vérifier que le token est valide
        if 'error' in token_info:
            raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED))
        
        # Extraire les informations utilisateur
        email = token_info.get('email')
        if not email:
            raise BridgeQuestException(_(ErrorMessages.USER_EMAIL_REQUIRED))
        
        return {
            'email': email,
            'given_name': token_info.get('given_name', ''),
            'family_name': token_info.get('family_name', ''),
            'picture': token_info.get('picture', ''),
            'sub': token_info.get('sub', ''),
        }
        
    except requests.RequestException as e:
        raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED)) from e
    except BridgeQuestException:
        # Re-lancer les exceptions métier telles quelles
        raise
    except Exception as e:
        # Encapsuler les autres exceptions
        raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_FAILED)) from e
