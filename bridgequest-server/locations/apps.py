from django.apps import AppConfig


class LocationsConfig(AppConfig):
    """Configuration de l'application Locations."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "locations"
    verbose_name = "Géolocalisation"
