from django.apps import AppConfig


class InteractionsConfig(AppConfig):
    """Configuration de l'application Interactions."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "interactions"
    verbose_name = "Interactions et QR codes"
