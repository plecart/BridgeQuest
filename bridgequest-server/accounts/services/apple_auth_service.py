"""
Service de validation des tokens Apple Sign-In pour Bridge Quest.

Ce service valide les tokens ID obtenus via Apple Sign-In SDK
depuis l'application mobile Flutter.
"""
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from django.conf import settings
from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages
from utils.sso_validation import REQUEST_TIMEOUT_SECONDS, require_non_empty_sso_token, require_sso_config

# Constantes de configuration
APPLE_PUBLIC_KEYS_URL = 'https://appleid.apple.com/auth/keys'
APPLE_ISSUER = 'https://appleid.apple.com'


def validate_apple_token(token):
    """
    Valide un token ID Apple et retourne les informations de l'utilisateur.
    
    Note: Apple Sign-In peut ne pas fournir l'email dans le token
    si l'utilisateur a déjà autorisé l'app. Dans ce cas, une exception
    est levée car l'email est requis pour créer un compte.
    
    Args:
        token: Le token ID (JWT) obtenu via Apple Sign-In SDK
        
    Returns:
        dict: Dictionnaire contenant les informations de l'utilisateur Apple :
            - email: Email de l'utilisateur (requis)
            - sub: ID unique Apple de l'utilisateur
            - given_name: Prénom (peut être vide)
            - family_name: Nom de famille (peut être vide)
            
    Raises:
        BridgeQuestException: Si la validation échoue ou si l'email est manquant
    """
    require_non_empty_sso_token(token)
    
    try:
        decoded_token = _decode_and_verify_token(token)
        return _extract_user_data(decoded_token)
    except jwt.InvalidTokenError as e:
        raise BridgeQuestException(message_key=ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED) from e
    except BridgeQuestException:
        raise
    except Exception as e:
        raise BridgeQuestException(message_key=ErrorMessages.AUTH_SSO_FAILED) from e


def _decode_and_verify_token(token):
    """
    Décode et vérifie un token Apple.
    
    Args:
        token: Le token JWT à décoder
        
    Returns:
        dict: Le token décodé et vérifié
        
    Raises:
        BridgeQuestException: Si la validation échoue
    """
    unverified_header = jwt.get_unverified_header(token)
    apple_keys = _fetch_apple_public_keys()
    public_key = _find_matching_public_key(apple_keys, unverified_header)
    
    if not public_key:
        raise BridgeQuestException(message_key=ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED)
    
    return _decode_token_with_key(token, public_key)


def _fetch_apple_public_keys():
    """
    Récupère les clés publiques Apple pour valider les tokens.
    
    Returns:
        dict: Dictionnaire des clés publiques Apple
        
    Raises:
        BridgeQuestException: Si la récupération échoue
    """
    try:
        response = requests.get(APPLE_PUBLIC_KEYS_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code != 200:
            raise BridgeQuestException(message_key=ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED)
        return response.json()
    except requests.RequestException as e:
        raise BridgeQuestException(message_key=ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED) from e


def _find_matching_public_key(apple_keys, unverified_header):
    """
    Trouve la clé publique Apple correspondante au header du token.
    
    Args:
        apple_keys: Dictionnaire contenant les clés publiques Apple
        unverified_header: Header du token JWT non vérifié
        
    Returns:
        RSAPublicKey: La clé publique trouvée ou None
    """
    kid = unverified_header.get('kid')
    
    for key in apple_keys.get('keys', []):
        if key['kid'] == kid:
            # PyJWT 2.0+ accepte un dict ; les versions <2.0 requirent json.dumps(key)
            return RSAAlgorithm.from_jwk(key)
    
    return None


def _get_apple_client_id():
    """
    Récupère le Client ID Apple depuis la configuration.

    Returns:
        str: Le Client ID Apple

    Raises:
        BridgeQuestException: Si la configuration est manquante
    """
    apple_client_id = getattr(settings, 'APPLE_CLIENT_ID', None)
    require_sso_config(apple_client_id)
    return apple_client_id


def _decode_token_with_key(token, public_key):
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
    apple_client_id = _get_apple_client_id()
    
    return jwt.decode(
        token,
        public_key,
        algorithms=['RS256'],
        issuer=APPLE_ISSUER,
        audience=apple_client_id
    )


def _extract_user_data(decoded_token):
    """
    Extrait et normalise les données utilisateur depuis le token décodé.
    
    Args:
        decoded_token: Token JWT décodé
        
    Returns:
        dict: Données utilisateur normalisées
        
    Raises:
        BridgeQuestException: Si les données requises sont manquantes
    """
    sub = decoded_token.get('sub')
    if not sub:
        raise BridgeQuestException(message_key=ErrorMessages.AUTH_SSO_TOKEN_VALIDATION_FAILED)
    
    email = decoded_token.get('email')
    if not email:
        raise BridgeQuestException(message_key=ErrorMessages.USER_EMAIL_REQUIRED)
    
    return {
        'email': email,
        'given_name': decoded_token.get('given_name', ''),
        'family_name': decoded_token.get('family_name', ''),
        'sub': sub,
    }
