"""
Vues du module Accounts.

Les vues API REST seront importées ici lorsqu'elles seront créées.
"""
from .auth_views import (
    sso_login_view,
    current_user_view,
    logout_view,
    user_profile_view
)

__all__ = [
    'sso_login_view',
    'current_user_view',
    'logout_view',
    'user_profile_view'
]
