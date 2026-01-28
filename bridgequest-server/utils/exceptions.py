"""
Exceptions personnalisées pour Bridge Quest.
"""


class BridgeQuestException(Exception):
    """Exception de base pour Bridge Quest."""
    pass


class GameException(BridgeQuestException):
    """Exception liée aux parties."""
    pass


class PlayerException(BridgeQuestException):
    """Exception liée aux joueurs."""
    pass


class InteractionException(BridgeQuestException):
    """Exception liée aux interactions."""
    pass
