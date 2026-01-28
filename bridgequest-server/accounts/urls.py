"""
URLs pour le module Accounts.
"""
from django.urls import path, include
from accounts.views.auth_views import current_user_view, logout_view, user_profile_view

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('me/', current_user_view, name='current-user'),
    path('logout/', logout_view, name='logout'),
    path('profile/<int:user_id>/', user_profile_view, name='user-profile'),
    
    # URLs django-allauth pour SSO
    path('', include('allauth.urls')),
]
