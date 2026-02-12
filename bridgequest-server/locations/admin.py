"""
Configuration de l'interface d'administration Django pour le module Locations.
"""
from django.contrib import admin
from .models import Position


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """Administration des positions GPS."""

    list_display = ["id", "player", "latitude", "longitude", "recorded_at"]
    list_filter = ["recorded_at"]
    search_fields = ["player__user__username"]
    readonly_fields = ["recorded_at"]
    ordering = ["-recorded_at"]
