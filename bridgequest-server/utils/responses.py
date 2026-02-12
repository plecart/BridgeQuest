"""
Utilitaires pour les réponses API.

Fonctions partagées pour construire des réponses HTTP standardisées.
"""
from rest_framework import status
from rest_framework.response import Response


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
