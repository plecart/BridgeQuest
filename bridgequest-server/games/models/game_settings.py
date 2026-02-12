"""
Modèle GameSettings pour Bridge Quest.

Paramètres de configuration d'une partie, éditables en salle d'attente
par l'administrateur. Verrouillés au lancement de la partie.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.messages import ModelMessages


class GameSettings(models.Model):
    """
    Paramètres de configuration d'une partie.

    Relation one-to-one avec Game. Créé automatiquement à la
    création de la partie via game_service.create_game().
    """

    game = models.OneToOneField(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="settings",
        verbose_name=_(ModelMessages.SETTINGS_GAME),
    )

    game_duration = models.PositiveIntegerField(
        default=30,
        verbose_name=_(ModelMessages.SETTINGS_GAME_DURATION),
    )

    deployment_duration = models.PositiveIntegerField(
        default=5,
        verbose_name=_(ModelMessages.SETTINGS_DEPLOYMENT_DURATION),
    )

    spirit_percentage = models.PositiveIntegerField(
        default=20,
        verbose_name=_(ModelMessages.SETTINGS_SPIRIT_PERCENTAGE),
    )

    points_per_minute = models.PositiveIntegerField(
        default=10,
        verbose_name=_(ModelMessages.SETTINGS_POINTS_PER_MINUTE),
    )

    conversion_points_percentage = models.PositiveIntegerField(
        default=50,
        verbose_name=_(ModelMessages.SETTINGS_CONVERSION_POINTS_PERCENTAGE),
    )

    class Meta:
        verbose_name = _(ModelMessages.SETTINGS_VERBOSE_NAME)
        verbose_name_plural = _(ModelMessages.SETTINGS_VERBOSE_NAME_PLURAL)

    def __str__(self):
        """Représentation string des paramètres."""
        return _(ModelMessages.SETTINGS_STR_DISPLAY).format(game=self.game)
