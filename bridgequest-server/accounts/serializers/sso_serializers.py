"""
Serializers pour l'authentification SSO mobile.

Ces serializers gèrent la sérialisation/désérialisation des données
pour l'authentification SSO depuis l'application mobile Flutter.
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from utils.messages import ErrorMessages


class SSOLoginSerializer(serializers.Serializer):
    """
    Serializer pour la requête de connexion SSO mobile.
    
    L'application Flutter envoie le token SSO obtenu via les SDKs natifs
    (Google Sign-In, Apple Sign-In) pour validation et création de compte.
    """
    
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('apple', 'Apple'),
    ]
    
    provider = serializers.ChoiceField(
        choices=PROVIDER_CHOICES,
        help_text=_("Fournisseur SSO (google ou apple)")
    )
    
    token = serializers.CharField(
        help_text=_("Token ID (JWT) obtenu du fournisseur SSO"),
        required=True
    )
    
    def validate_token(self, value):
        """
        Valide que le token n'est pas vide.
        
        Args:
            value: Le token à valider
            
        Returns:
            str: Le token validé (stripped)
            
        Raises:
            serializers.ValidationError: Si le token est vide
        """
        if not value or not value.strip():
            raise serializers.ValidationError(_(ErrorMessages.AUTH_SSO_TOKEN_REQUIRED))
        return value.strip()
