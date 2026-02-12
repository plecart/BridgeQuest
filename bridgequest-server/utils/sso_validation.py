"""
Validation SSO partagée pour Bridge Quest.

Fonctions de validation communes aux services Google et Apple Sign-In.
Constantes partagées pour les appels HTTP (ex. timeout).
"""
from rest_framework import status
from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages

# Timeout (secondes) pour les appels HTTP vers les APIs SSO (Google tokeninfo, Apple keys)
REQUEST_TIMEOUT_SECONDS = 10


def require_sso_config(value):
    """
    Vérifie qu'une valeur de configuration SSO est présente.

    Args:
        value: La valeur à vérifier (chaîne, liste, etc. — toute valeur falsy est rejetée)

    Raises:
        BridgeQuestException: Si la valeur est vide/None (500, erreur serveur)
    """
    if not value:
        raise BridgeQuestException(
            message_key=ErrorMessages.AUTH_SSO_CONFIG_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def require_non_empty_sso_token(token):
    """
    Vérifie que le token SSO n'est pas vide.

    Args:
        token: Le token à valider (chaîne ou None)

    Raises:
        BridgeQuestException: Si le token est vide ou None
    """
    if not token:
        raise BridgeQuestException(message_key=ErrorMessages.AUTH_SSO_TOKEN_REQUIRED)
