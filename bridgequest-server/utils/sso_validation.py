"""
Validation SSO partagée pour Bridge Quest.

Fonctions de validation communes aux services Google et Apple Sign-In.
Constantes partagées pour les appels HTTP (ex. timeout).
"""
from django.utils.translation import gettext_lazy as _
from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages

# Timeout (secondes) pour les appels HTTP vers les APIs SSO (Google tokeninfo, Apple keys)
REQUEST_TIMEOUT_SECONDS = 10


def require_non_empty_sso_token(token):
    """
    Vérifie que le token SSO n'est pas vide.

    Args:
        token: Le token à valider (chaîne ou None)

    Raises:
        BridgeQuestException: Si le token est vide ou None
    """
    if not token:
        raise BridgeQuestException(_(ErrorMessages.AUTH_SSO_TOKEN_REQUIRED))
