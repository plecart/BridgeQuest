"""
Services du module Accounts.

Les services de logique métier seront importés ici lorsqu'ils seront créés.
"""
from .auth_service import get_or_create_user_from_social_account, get_user_by_email

__all__ = ['get_or_create_user_from_social_account', 'get_user_by_email']
