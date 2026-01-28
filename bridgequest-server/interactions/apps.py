from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from utils.messages import Messages


class InteractionsConfig(AppConfig):
    """Configuration de l'application Interactions."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "interactions"
    verbose_name = _(Messages.APP_INTERACTIONS)