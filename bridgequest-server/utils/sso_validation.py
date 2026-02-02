"""
Validation SSO partagée pour Bridge Quest.

Fonctions de validation communes aux services Google et Apple Sign-In.
"""
from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages


def require_non_empty_sso_token(token):
    """
    Vérifie que le token SSO n'est pas vide.

    Args:
        token: Le token à valider (chaîne ou None)

    Raises:
        BridgeQuestException: Si le token est vide ou None
    """
    if not token:
        raise BridgeQuestException(ErrorMessages.AUTH_SSO_TOKEN_REQUIRED)
