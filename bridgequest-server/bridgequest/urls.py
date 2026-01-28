"""
URL configuration for bridgequest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),
    
    # API REST
    path('api/auth/', include('accounts.urls')),
    path('api/games/', include('games.urls')),
    path('api/interactions/', include('interactions.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/powers/', include('powers.urls')),
    path('api/logs/', include('logs.urls')),
]
