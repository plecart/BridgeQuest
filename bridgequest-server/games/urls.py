"""
URLs pour le module Games.
"""
from django.urls import path

from games.views.game_views import (
    create_game_view,
    game_detail_view,
    game_players_view,
    join_game_view,
)

app_name = 'games'

urlpatterns = [
    path('', create_game_view, name='create'),
    path('join/', join_game_view, name='join'),
    path('<int:pk>/', game_detail_view, name='detail'),
    path('<int:pk>/players/', game_players_view, name='players'),
]
