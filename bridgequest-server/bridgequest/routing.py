"""
Configuration du routing WebSocket pour Bridge Quest.

Les connexions WebSocket sont routées vers les consumers des modules.
"""
from django.urls import path
from games.consumers import LobbyConsumer

websocket_urlpatterns = [
    path('ws/lobby/<int:game_id>/', LobbyConsumer.as_asgi()),
]
