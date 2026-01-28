"""
Services du module Accounts.

Les services de logique métier seront importés ici lorsqu'ils seront créés.
"""
from .auth_service import (
    get_or_create_user_from_social_account,
    get_user_by_email,
    create_or_get_user_from_sso_data,
)
from .google_auth_service import validate_google_token
from .apple_auth_service import validate_apple_token

__all__ = [
    'get_or_create_user_from_social_account',
    'get_user_by_email',
    'create_or_get_user_from_sso_data',
    'validate_google_token',
    'validate_apple_token',
]
