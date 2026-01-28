"""
Validateurs personnalisés pour Bridge Quest.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_game_code(value):
    """
    Valide le format d'un code de partie.
    
    Un code de partie doit être alphanumérique et faire 6 caractères.
    
    Args:
        value: La valeur à valider
        
    Raises:
        ValidationError: Si le code n'est pas valide
    """
    if not value.isalnum():
        raise ValidationError(_('Le code de partie doit être alphanumérique.'))
    if len(value) != 6:
        raise ValidationError(_('Le code de partie doit faire exactement 6 caractères.'))
