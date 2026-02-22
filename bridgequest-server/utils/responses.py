"""
Utilitaires pour les réponses API.

Fonctions partagées pour construire des réponses HTTP standardisées.
"""
import logging

from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Construit une réponse d'erreur standardisée.

    Args:
        message: Message d'erreur (str ou exception avec __str__).
        status_code: Code HTTP (400 par défaut).

    Returns:
        Response: Réponse DRF avec {"error": "..."}.
    """
    return Response({"error": str(message)}, status=status_code)


def validation_error_response(serializer):
    """
    Construit une réponse d'erreur de validation avec tous les champs invalides.

    Format DRF standard : {"field": ["error1", ...], ...}
    Utile pour que le client affiche toutes les erreurs et évite les
    allers-retours par essai/erreur.

    Log les erreurs multiples pour faciliter le débogage côté serveur.

    Args:
        serializer: Serializer DRF avec errors (après is_valid() == False).

    Returns:
        Response: Réponse DRF 400 avec serializer.errors.
    """
    errors = serializer.errors
    if len(errors) > 1:
        logger.info(
            "Validation failed for %d fields: %s",
            len(errors),
            list(errors.keys()),
        )
    return Response(errors, status=status.HTTP_400_BAD_REQUEST)
