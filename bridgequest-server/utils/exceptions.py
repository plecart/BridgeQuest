"""
Exceptions personnalisées pour Bridge Quest.

Toutes les exceptions métier doivent hériter de BridgeQuestException.
"""
from django.utils.translation import gettext_lazy as _
from utils.messages import ErrorMessages


class BridgeQuestException(Exception):
    """
    Exception de base pour Bridge Quest.
    
    Toutes les exceptions métier doivent hériter de cette classe.
    """
    
    def __init__(self, message_key=None, message=None):
        """
        Initialise l'exception.
        
        Args:
            message_key: Clé de traduction (de ErrorMessages)
            message: Message direct (déconseillé, utiliser message_key)
        """
        if message_key:
            self.message = _(message_key)
        elif message:
            self.message = message
        else:
            self.message = _(ErrorMessages.INTERNAL_ERROR)
        
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
