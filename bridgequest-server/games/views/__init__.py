"""
Vues du module Games.

Réexporte les vues API REST pour accès direct depuis games.views.
"""
from .game_views import (
    create_game_view,
    game_detail_view,
    game_players_view,
    game_positions_view,
    game_start_view,
    join_game_view,
)
