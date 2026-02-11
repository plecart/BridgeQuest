"""
Modèle Position pour Bridge Quest.

Représente une position GPS enregistrée pour un joueur dans une partie.
Une nouvelle entrée est créée à chaque mise à jour (historique des positions).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.messages import ModelMessages


class Position(models.Model):
    """
    Position GPS d'un joueur à un instant donné.

    Permet de conserver un historique des positions et de récupérer
    la dernière position connue en cas de déconnexion.
    """

    player = models.ForeignKey(
        "games.Player",
        on_delete=models.CASCADE,
        related_name="positions",
        verbose_name=_(ModelMessages.POSITION_PLAYER),
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_(ModelMessages.POSITION_LATITUDE),
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_(ModelMessages.POSITION_LONGITUDE),
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_(ModelMessages.POSITION_RECORDED_AT),
    )

    class Meta:
        verbose_name = _(ModelMessages.POSITION_VERBOSE_NAME)
        verbose_name_plural = _(ModelMessages.POSITION_VERBOSE_NAME_PLURAL)
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["player", "-recorded_at"]),
        ]

    def __str__(self):
        """Représentation string de la position."""
        return f"{self.player} @ ({self.latitude}, {self.longitude})"
