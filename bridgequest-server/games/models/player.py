"""
Modèle Player pour Bridge Quest.

Représente un joueur dans une partie (liaison User <-> Game).
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.messages import ModelMessages


class PlayerRole(models.TextChoices):
    """Rôles possibles d'un joueur."""

    HUMAN = "HUMAN", _(ModelMessages.PLAYER_ROLE_HUMAN)
    SPIRIT = "SPIRIT", _(ModelMessages.PLAYER_ROLE_SPIRIT)


class Player(models.Model):
    """
    Modèle représentant un joueur dans une partie.

    Lie un utilisateur à une partie avec son rôle (Humain/Esprit)
    et ses droits d'administration.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="game_players",
        verbose_name=_(ModelMessages.PLAYER_USER),
    )

    game = models.ForeignKey(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="players",
        verbose_name=_(ModelMessages.PLAYER_GAME),
    )

    is_admin = models.BooleanField(
        default=False,
        verbose_name=_(ModelMessages.PLAYER_IS_ADMIN),
    )

    role = models.CharField(
        max_length=10,
        choices=PlayerRole.choices,
        default=PlayerRole.HUMAN,
        verbose_name=_(ModelMessages.PLAYER_ROLE),
    )

    score = models.IntegerField(
        default=0,
        verbose_name=_(ModelMessages.PLAYER_SCORE),
    )

    converted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_(ModelMessages.PLAYER_CONVERTED_AT),
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_(ModelMessages.PLAYER_JOINED_AT),
    )

    class Meta:
        verbose_name = _(ModelMessages.PLAYER_VERBOSE_NAME)
        verbose_name_plural = _(ModelMessages.PLAYER_VERBOSE_NAME_PLURAL)
        ordering = ["-joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "game"],
                name="unique_player_per_game",
            )
        ]

    def __str__(self):
        """Représentation string du joueur."""
        return _(ModelMessages.PLAYER_STR_DISPLAY).format(
            user=self.user,
            game=self.game,
        )
