"""
Modèle Game pour Bridge Quest.

Représente une partie avec son cycle de vie :
WAITING -> DEPLOYMENT -> IN_PROGRESS -> FINISHED
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.messages import ModelMessages
from utils.validators import validate_game_code


class GameState(models.TextChoices):
    """États possibles d'une partie."""

    WAITING = "WAITING", _(ModelMessages.GAME_STATE_WAITING)
    DEPLOYMENT = "DEPLOYMENT", _(ModelMessages.GAME_STATE_DEPLOYMENT)
    IN_PROGRESS = "IN_PROGRESS", _(ModelMessages.GAME_STATE_IN_PROGRESS)
    FINISHED = "FINISHED", _(ModelMessages.GAME_STATE_FINISHED)


class Game(models.Model):
    """
    Modèle représentant une partie de Bridge Quest.

    Une partie traverse les états : WAITING (salle d'attente),
    DEPLOYMENT (déploiement des joueurs), IN_PROGRESS (jeu en cours),
    FINISHED (terminée).
    """

    name = models.CharField(
        max_length=100,
        verbose_name=_(ModelMessages.GAME_NAME),
    )

    code = models.CharField(
        max_length=6,
        unique=True,
        validators=[validate_game_code],
        verbose_name=_(ModelMessages.GAME_CODE),
    )

    state = models.CharField(
        max_length=20,
        choices=GameState.choices,
        default=GameState.WAITING,
        verbose_name=_(ModelMessages.GAME_STATE),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_(ModelMessages.GAME_CREATED_AT),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_(ModelMessages.GAME_UPDATED_AT),
    )

    class Meta:
        verbose_name = _(ModelMessages.GAME_VERBOSE_NAME)
        verbose_name_plural = _(ModelMessages.GAME_VERBOSE_NAME_PLURAL)
        ordering = ["-created_at"]

    def __str__(self):
        """Représentation string de la partie."""
        return self.name
