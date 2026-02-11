"""
Configuration de l'interface d'administration Django pour le module Games.
"""
from django.contrib import admin
from games.models import Game, Player


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Game."""

    list_display = ["name", "code", "state", "created_at"]
    list_filter = ["state"]
    search_fields = ["name", "code"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Player."""

    list_display = ["user", "game", "role", "is_admin", "score", "joined_at"]
    list_filter = ["role", "is_admin"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["joined_at"]
    autocomplete_fields = ["user", "game"]
