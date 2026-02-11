"""
Configuration du routing WebSocket pour Bridge Quest.

Deux canaux distincts :
- ws/lobby/{game_id}/ : salle d'attente (phase WAITING)
- ws/game/{game_id}/ : partie en cours (phases DEPLOYMENT, IN_PROGRESS)
"""
from django.urls import path
from games.consumers import GameConsumer, LobbyConsumer

websocket_urlpatterns = [
    path("ws/lobby/<int:game_id>/", LobbyConsumer.as_asgi()),
    path("ws/game/<int:game_id>/", GameConsumer.as_asgi()),
]
