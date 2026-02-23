# Data migration: create GameSettings for existing games.
#
# Valeurs par défaut alignées avec GameSettings (modèle actuel).
# Ne pas modifier après déploiement — ajouter une nouvelle migration si besoin.

from django.db import migrations

_DEFAULTS = {
    "game_duration": 30,
    "deployment_duration": 5,
    "spirit_percentage": 20,
    "points_per_minute": 10,
    "conversion_points_percentage": 50,
}


def create_settings_for_existing_games(apps, schema_editor):
    """
    Crée des GameSettings par défaut pour toutes les parties existantes
    qui n'en ont pas.

    Nécessaire car la migration 0002 ajoute GameSettings sans backfill :
    les parties créées avant (0001) n'ont pas de settings associés,
    ce qui provoquerait DoesNotExist lors de l'accès à game.settings.
    """
    Game = apps.get_model("games", "Game")
    GameSettings = apps.get_model("games", "GameSettings")

    for game in Game.objects.all():
        GameSettings.objects.get_or_create(game=game, defaults=_DEFAULTS)


def noop(apps, schema_editor):
    """Pas de rollback : supprimer les settings créés serait risqué."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0002_add_game_settings_and_lifecycle_fields"),
    ]

    operations = [
        migrations.RunPython(create_settings_for_existing_games, noop),
    ]
