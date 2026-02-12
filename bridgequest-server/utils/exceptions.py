"""
Exceptions personnalisées pour Bridge Quest.

Toutes les exceptions métier doivent hériter de BridgeQuestException.
"""
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from utils.messages import ErrorMessages


class BridgeQuestException(Exception):
    """
    Exception de base pour Bridge Quest.
    
    Toutes les exceptions métier doivent hériter de cette classe.
    """
    
    # Code HTTP par défaut pour les erreurs client (validation, etc.)
    default_status_code = status.HTTP_400_BAD_REQUEST
    
    def __init__(self, message_key=None, message=None, status_code=None):
        """
        Initialise l'exception.
        
        Args:
            message_key: Clé de traduction (de ErrorMessages)
            message: Message direct (déconseillé, utiliser message_key)
            status_code: Code HTTP à renvoyer (400 par défaut pour erreur client,
                HTTP_500_INTERNAL_SERVER_ERROR pour erreur serveur ex. configuration manquante)
        """
        if message_key:
            self.message = _(message_key)
        elif message:
            self.message = message
        else:
            self.message = _(ErrorMessages.INTERNAL_ERROR)
        
        self.status_code = status_code if status_code is not None else self.default_status_code
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
