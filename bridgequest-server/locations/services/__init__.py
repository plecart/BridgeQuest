"""
Services du module Locations.
"""
from .position_service import get_latest_positions_for_game, update_position

__all__ = [
    "get_latest_positions_for_game",
    "update_position",
]
