"""
Exceptions personnalisées pour Bridge Quest.

Toutes les exceptions métier doivent hériter de BridgeQuestException.
Voir CODING_STANDARDS.md pour la sémantique des codes HTTP (4xx vs 5xx).
"""
from django.utils.translation import gettext_lazy as _
from utils.messages import ErrorMessages

# Code HTTP pour erreur serveur (éviter magic number dans les services)
HTTP_SERVER_ERROR = 500


class BridgeQuestException(Exception):
    """
    Exception de base pour Bridge Quest.

    Toutes les exceptions métier doivent hériter de cette classe.
    Utiliser status_code pour distinguer erreurs client (4xx) et serveur (5xx)
    afin de renvoyer le bon code HTTP (voir CODING_STANDARDS.md).
    """

    # Code HTTP par défaut : erreur client (bad request)
    DEFAULT_STATUS_CODE = 400

    def __init__(self, message_key=None, message=None, status_code=None):
        """
        Initialise l'exception.

        Args:
            message_key: Clé de traduction (de ErrorMessages)
            message: Message direct (déconseillé, utiliser message_key)
            status_code: Code HTTP à renvoyer (400 par défaut pour erreur client,
                HTTP_SERVER_ERROR pour erreur serveur ex. configuration manquante)
        """
        if message_key:
            self.message = _(message_key)
        elif message:
            self.message = message
        else:
            self.message = _(ErrorMessages.INTERNAL_ERROR)

        self.status_code = (
            status_code if status_code is not None else self.DEFAULT_STATUS_CODE
        )
        super().__init__(self.message)

    def __str__(self):
        return str(self.message)


class GameException(BridgeQuestException):
    """Exception liée aux parties de jeu."""
    pass


class PlayerException(BridgeQuestException):
    """Exception liée aux joueurs."""
    pass


class InteractionException(BridgeQuestException):
    """Exception liée aux interactions (QR codes, scans, etc.)."""
    pass


class LocationException(BridgeQuestException):
    """Exception liée à la géolocalisation."""
    pass


class PowerException(BridgeQuestException):
    """Exception liée aux pouvoirs des Esprits."""
    pass
