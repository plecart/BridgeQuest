"""
URLs pour le module Accounts.
"""
from django.urls import path, include
from accounts.views.auth_views import (
    sso_login_view,
    current_user_view,
    logout_view,
    user_profile_view
)

app_name = 'accounts'

urlpatterns = [
    # Authentification SSO mobile
    path('sso/login/', sso_login_view, name='sso-login'),
    
    # Authentification
    path('me/', current_user_view, name='current-user'),
    path('logout/', logout_view, name='logout'),
    path('profile/<int:user_id>/', user_profile_view, name='user-profile'),
    
    # URLs django-allauth pour SSO (conservées pour compatibilité future)
    path('', include('allauth.urls')),
]
