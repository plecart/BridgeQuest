"""
Configuration des URLs principales pour Bridge Quest.

Les URLs sont organisées par module via include().
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Interface d'administration Django
    path('admin/', admin.site.urls),
    
    # API REST - Organisation par module
    path('api/auth/', include('accounts.urls')),
    path('api/games/', include('games.urls')),
    path('api/interactions/', include('interactions.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/powers/', include('powers.urls')),
    path('api/logs/', include('logs.urls')),
]
