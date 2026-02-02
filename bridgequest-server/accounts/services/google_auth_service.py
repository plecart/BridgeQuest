"""
Service de validation des tokens Google Sign-In pour Bridge Quest.

Ce service valide les tokens ID obtenus via Google Sign-In SDK
depuis l'application mobile Flutter.
"""
import requests
from django.conf import settings

from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages
from utils.sso_validation import require_non_empty_sso_token

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
        BridgeQuestException: Si la validation échoue ou si la configuration est manquante
    """
    require_non_empty_sso_token(token)
    google_client_ids = _get_google_client_ids()
    token_info = _fetch_token_info(token)
    _validate_token_audience(token_info, google_client_ids)
    return _extract_user_data(token_info)


def _get_google_client_ids():
    """
    Récupère la liste des Client IDs Google autorisés depuis la configuration.
    
    Returns:
        list: Liste des Client IDs autorisés
        
    Raises:
        BridgeQuestException: Si la configuration est manquante
    """
    google_client_ids = getattr(settings, 'GOOGLE_CLIENT_IDS', None)
    if not google_client_ids:
        raise BridgeQuestException(ErrorMessages.AUTH_SSO_CONFIG_ERROR)
    return google_client_ids


def _fetch_token_info(token):
    """
    Récupère les informations du token depuis l'API Google.
    
    Args:
        token: Le token ID à valider
        
    Returns:
        dict: Informations du token retournées par Google
        
    Raises:
        BridgeQuestException: Si l'appel API échoue
    """
    try:
        response = requests.get(
            GOOGLE_TOKEN_INFO_URL,
            params={'id_token': token},
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        
        if response.status_code != 200:
            raise BridgeQuestException(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED)
        
        token_info = response.json()
        
        if 'error' in token_info:
            raise BridgeQuestException(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED)
        
        return token_info
        
    except requests.RequestException as e:
        raise BridgeQuestException(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED) from e


def _validate_token_audience(token_info, google_client_ids):
    """
    Vérifie que l'audience du token correspond à un Client ID autorisé.
    
    Args:
        token_info: Informations du token retournées par Google
        google_client_ids: Liste des Client IDs autorisés
        
    Raises:
        BridgeQuestException: Si l'audience ne correspond pas
    """
    token_audience = token_info.get('aud')
    if not token_audience or token_audience not in google_client_ids:
        raise BridgeQuestException(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED)


def _extract_user_data(token_info):
    """
    Extrait et normalise les données utilisateur depuis les informations du token.
    
    Args:
        token_info: Informations du token retournées par Google
        
    Returns:
        dict: Données utilisateur normalisées
        
    Raises:
        BridgeQuestException: Si l'email est manquant
    """
    email = token_info.get('email')
    if not email:
        raise BridgeQuestException(ErrorMessages.USER_EMAIL_REQUIRED)
    
    return {
        'email': email,
        'given_name': token_info.get('given_name', ''),
        'family_name': token_info.get('family_name', ''),
        'picture': token_info.get('picture', ''),
        'sub': token_info.get('sub', ''),
    }
