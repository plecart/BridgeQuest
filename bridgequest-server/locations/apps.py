from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from utils.messages import Messages


class LocationsConfig(AppConfig):
    """Configuration de l'application Locations."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "locations"
    verbose_name = _(Messages.APP_LOCATIONS)