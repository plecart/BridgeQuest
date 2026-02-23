"""
Configuration de l'interface d'administration Django pour le module Games.
"""
from django.contrib import admin
from games.models import Game, GameSettings, Player


class GameSettingsInline(admin.StackedInline):
    """Inline pour afficher les settings dans l'admin Game."""

    model = GameSettings
    extra = 0
    max_num = 1
    can_delete = False


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Game."""

    list_display = ["code", "state", "created_at"]
    list_filter = ["state"]
    search_fields = ["code"]
    readonly_fields = ["created_at", "updated_at", "deployment_ends_at", "game_ends_at"]
    date_hierarchy = "created_at"
    inlines = [GameSettingsInline]


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Player."""

    list_display = ["user", "game", "role", "is_admin", "score", "joined_at"]
    list_filter = ["role", "is_admin"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["joined_at", "converted_at"]
    autocomplete_fields = ["user", "game"]
