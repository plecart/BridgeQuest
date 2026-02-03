"""
URLs pour le module Accounts.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
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
    
    # OAuth2/JWT - Refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Authentification
    path('me/', current_user_view, name='current-user'),
    path('logout/', logout_view, name='logout'),
    path('profile/<int:user_id>/', user_profile_view, name='user-profile'),
]
