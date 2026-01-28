"""
Modèle User étendu pour Bridge Quest.

Ce modèle étend le modèle User de Django pour ajouter des champs spécifiques
à l'application Bridge Quest.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.messages import ModelMessages


class User(AbstractUser):
    """
    Modèle utilisateur étendu pour Bridge Quest.
    
    Hérite de AbstractUser pour avoir tous les champs Django par défaut
    et ajoute des champs spécifiques à l'application.
    """
    
    avatar = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_(ModelMessages.USER_AVATAR),
        help_text=_(ModelMessages.USER_AVATAR)
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_(ModelMessages.USER_CREATED_AT)
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_(ModelMessages.USER_UPDATED_AT)
    )
    
    class Meta:
        verbose_name = _(ModelMessages.USER_VERBOSE_NAME)
        verbose_name_plural = _(ModelMessages.USER_VERBOSE_NAME_PLURAL)
        ordering = ['-date_joined']
    
    def __str__(self):
        """Représentation string de l'utilisateur."""
        return self.username or self.email
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username or self.email
    
    def get_display_name(self):
        """Retourne le nom d'affichage de l'utilisateur."""
        return self.get_full_name() or self.username or self.email
