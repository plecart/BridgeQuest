"""
Vues du module Accounts.

Les vues API REST seront importées ici lorsqu'elles seront créées.
"""
from .auth_views import current_user_view, logout_view, user_profile_view

__all__ = ['current_user_view', 'logout_view', 'user_profile_view']
