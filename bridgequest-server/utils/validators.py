"""
Validateurs personnalisés pour Bridge Quest.

Tous les validateurs réutilisables doivent être définis ici.
Ils utilisent les clés de traduction de utils.messages.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from utils.messages import Messages


def validate_game_code(value):
    """
    Valide le format d'un code de partie.
    
    Un code de partie doit être :
    - Alphanumérique (lettres et chiffres uniquement)
    - Faire exactement 6 caractères
    
    Args:
        value: La valeur à valider (str)
        
    Raises:
        ValidationError: Si le code n'est pas valide avec un message traduit
    """
    if not isinstance(value, str):
        raise ValidationError(_(Messages.GAME_CODE_INVALID_ALPHANUMERIC))
    
    if not value.isalnum():
        raise ValidationError(_(Messages.GAME_CODE_INVALID_ALPHANUMERIC))
    
    if len(value) != 6:
        raise ValidationError(_(Messages.GAME_CODE_INVALID_LENGTH))
