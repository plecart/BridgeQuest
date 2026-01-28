"""
Service de validation des tokens Apple Sign-In pour Bridge Quest.

Ce service valide les tokens ID obtenus via Apple Sign-In SDK
depuis l'application mobile Flutter.
"""
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages

# URL pour obtenir les clés publiques Apple
APPLE_PUBLIC_KEYS_URL = 'https://appleid.apple.com/auth/keys'


def get_apple_public_keys():
    """
    Récupère les clés publiques Apple pour valider les tokens.
    
    Returns:
        dict: Dictionnaire des clés publiques Apple
        
    Raises:
        BridgeQuestException: Si la récupération échoue
    """
    try:
        response = requests.get(APPLE_PUBLIC_KEYS_URL, timeout=10)
        if response.status_code != 200:
            raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED))
        return response.json()
    except requests.RequestException as e:
        raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED)) from e


def validate_apple_token(token):
    """
    Valide un token ID Apple et retourne les informations de l'utilisateur.
    
    Note: Apple Sign-In peut ne pas fournir l'email dans le token
    si l'utilisateur a déjà autorisé l'app. Dans ce cas, l'email
    doit être récupéré lors de la première connexion.
    
    Args:
        token: Le token ID (JWT) obtenu via Apple Sign-In SDK
        
    Returns:
        dict: Dictionnaire contenant les informations de l'utilisateur Apple :
            - email: Email de l'utilisateur (peut être None)
            - sub: ID unique Apple de l'utilisateur
            - given_name: Prénom (peut être None)
            - family_name: Nom de famille (peut être None)
            
    Raises:
        BridgeQuestException: Si la validation échoue
    """
    if not token:
        raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_REQUIRED))
    
    try:
        # Décoder le token sans vérification pour obtenir le header
        unverified_header = jwt.get_unverified_header(token)
        
        # Récupérer les clés publiques Apple
        apple_keys = get_apple_public_keys()
        
        # Trouver la clé publique correspondante
        public_key = _find_apple_public_key(apple_keys, unverified_header)
        
        if not public_key:
            raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED))
        
        # Valider et décoder le token
        decoded_token = _decode_apple_token(token, public_key)
        
        # Extraire et valider les informations utilisateur
        sub = decoded_token.get('sub')
        if not sub:
            raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED))
        
        # Retourner les données SSO normalisées
        # Note: email peut être None si l'utilisateur a déjà autorisé l'app
        return {
            'email': decoded_token.get('email'),
            'given_name': decoded_token.get('given_name', ''),
            'family_name': decoded_token.get('family_name', ''),
            'sub': sub,
        }
        
    except jwt.InvalidTokenError as e:
        raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED)) from e
    except BridgeQuestException:
        # Re-lancer les exceptions métier telles quelles
        raise
    except Exception as e:
        # Encapsuler les autres exceptions
        raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_FAILED)) from e


def _find_apple_public_key(apple_keys, unverified_header):
    """
    Trouve la clé publique Apple correspondante au header du token.
    
    Args:
        apple_keys: Dictionnaire contenant les clés publiques Apple
        unverified_header: Header du token JWT non vérifié
        
    Returns:
        RSAAlgorithm: La clé publique trouvée ou None
    """
    kid = unverified_header.get('kid')
    
    for key in apple_keys.get('keys', []):
        if key['kid'] == kid:
            return RSAAlgorithm.from_jwk(key)
    
    return None


def _decode_apple_token(token, public_key):
    """
    Décode et valide un token Apple avec la clé publique.
    
    Args:
        token: Le token JWT à décoder
        public_key: La clé publique RSA pour valider le token
        
    Returns:
        dict: Le token décodé
        
    Raises:
        jwt.InvalidTokenError: Si le token est invalide
    """
    decode_kwargs = {
        'algorithms': ['RS256'],
        'issuer': 'https://appleid.apple.com'
    }
    
    # Ajouter l'audience seulement si configuré
    if hasattr(settings, 'APPLE_CLIENT_ID') and settings.APPLE_CLIENT_ID:
        decode_kwargs['audience'] = settings.APPLE_CLIENT_ID
    
    return jwt.decode(token, public_key, **decode_kwargs)


def _find_apple_public_key(apple_keys, unverified_header):
    """
    Trouve la clé publique Apple correspondante au header du token.
    
    Args:
        apple_keys: Dictionnaire contenant les clés publiques Apple
        unverified_header: Header du token JWT non vérifié
        
    Returns:
        RSAAlgorithm: La clé publique trouvée ou None
    """
    kid = unverified_header.get('kid')
    
    for key in apple_keys.get('keys', []):
        if key['kid'] == kid:
            return RSAAlgorithm.from_jwk(key)
    
    return None


def _decode_apple_token(token, public_key):
    """
    Décode et valide un token Apple avec la clé publique.
    
    Args:
        token: Le token JWT à décoder
        public_key: La clé publique RSA pour valider le token
        
    Returns:
        dict: Le token décodé
        
    Raises:
        jwt.InvalidTokenError: Si le token est invalide
    """
    decode_kwargs = {
        'algorithms': ['RS256'],
        'issuer': 'https://appleid.apple.com'
    }
    
    # Ajouter l'audience seulement si configuré
    if hasattr(settings, 'APPLE_CLIENT_ID') and settings.APPLE_CLIENT_ID:
        decode_kwargs['audience'] = settings.APPLE_CLIENT_ID
    
    return jwt.decode(token, public_key, **decode_kwargs)
