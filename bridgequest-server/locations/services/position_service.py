"""
Service de gestion des positions GPS pour Bridge Quest.

Contient la logique métier : enregistrement et récupération des positions.
"""
from decimal import Decimal

from django.db.models import OuterRef, Subquery
from rest_framework import status

from games.models import GameState
from games.services import get_game_by_id, get_player_in_game
from locations.models import Position
from utils.exceptions import LocationException
from utils.messages import ErrorMessages

# Plages valides WGS84
_LAT_MIN = Decimal("-90")
_LAT_MAX = Decimal("90")
_LNG_MIN = Decimal("-180")
_LNG_MAX = Decimal("180")


def _require_game_active(game):
    """
    Vérifie que la partie est en phase active (DEPLOYMENT ou IN_PROGRESS).

    Les positions ne sont enregistrées que pendant le déploiement ou le jeu.

    Raises:
        LocationException: Si la partie n'est pas active.
    """
    if game.state not in (GameState.DEPLOYMENT, GameState.IN_PROGRESS):
        raise LocationException(
            message_key=ErrorMessages.POSITION_GAME_NOT_ACTIVE,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def _validate_coordinates(latitude, longitude):
    """
    Valide et convertit les coordonnées en Decimal (plages WGS84).

    Returns:
        tuple[Decimal, Decimal]: (latitude, longitude) validées.

    Raises:
        LocationException: Si les coordonnées sont invalides.
    """
    try:
        lat = Decimal(str(latitude))
        lng = Decimal(str(longitude))
    except (ValueError, TypeError):
        raise LocationException(message_key=ErrorMessages.POSITION_COORDINATES_INVALID)

    if not (_LAT_MIN <= lat <= _LAT_MAX and _LNG_MIN <= lng <= _LNG_MAX):
        raise LocationException(message_key=ErrorMessages.POSITION_COORDINATES_INVALID)

    return lat, lng


def update_position(game_id, user, latitude, longitude):
    """
    Enregistre une nouvelle position GPS pour le joueur dans la partie.

    Args:
        game_id: Identifiant de la partie.
        user: Utilisateur authentifié.
        latitude: Latitude WGS84 (-90 à 90).
        longitude: Longitude WGS84 (-180 à 180).

    Returns:
        Position: La position créée.

    Raises:
        GameException: Si la partie n'existe pas.
        PlayerException: Si l'utilisateur n'est pas dans la partie.
        LocationException: Si la partie n'est pas active ou coordonnées invalides.
    """
    game = get_game_by_id(game_id)
    _require_game_active(game)

    player = get_player_in_game(game, user)
    lat, lng = _validate_coordinates(latitude, longitude)

    return Position.objects.create(
        player=player,
        latitude=lat,
        longitude=lng,
    )


def get_latest_positions_for_game(game):
    """
    Récupère la dernière position connue de chaque joueur de la partie.

    Utilisé pour afficher les positions sur la carte et récupérer l'état
    après une déconnexion.

    Utilise une Subquery pour ne récupérer que la dernière position par joueur
    en base, évitant de charger tout l'historique (scalable avec le temps).

    Args:
        game: Instance de Game.

    Returns:
        list[Position]: Liste des dernières positions par joueur (une par joueur).
    """
    latest_per_player = Position.objects.filter(
        player=OuterRef("player")
    ).order_by("-recorded_at")

    return list(
        Position.objects.filter(player__game=game)
        .filter(pk=Subquery(latest_per_player.values("pk")[:1]))
        .select_related("player", "player__user")
        .order_by("player")
    )
