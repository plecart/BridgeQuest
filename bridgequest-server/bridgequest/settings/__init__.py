"""
Settings module for Bridge Quest.

This module contains environment-specific settings:
- base.py: Common settings shared across all environments
- development.py: Settings for local development
- production.py: Settings for production deployment
"""

# Par défaut, utiliser les settings de développement
from .development import *  # noqa
