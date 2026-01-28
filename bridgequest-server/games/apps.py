from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from utils.messages import Messages


class GamesConfig(AppConfig):
    """Configuration de l'application Games."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "games"
    verbose_name = _(Messages.APP_GAMES)