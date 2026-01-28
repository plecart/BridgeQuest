from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from utils.messages import Messages


class PowersConfig(AppConfig):
    """Configuration de l'application Powers."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "powers"
    verbose_name = _(Messages.APP_POWERS)