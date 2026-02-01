"""
Configuration de l'interface d'administration Django pour le module Accounts.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from accounts.models.user import User
from utils.messages import Messages

# Désinscrire le modèle Group de l'admin (non utilisé dans ce projet)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Configuration de l'admin pour le modèle User.
    
    Étend UserAdmin de Django pour ajouter les champs personnalisés.
    Les champs groups et user_permissions sont masqués car non utilisés.
    """
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_(Messages.ADMIN_PERSONAL_INFO), {
            'fields': ('first_name', 'last_name', 'email', 'avatar')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_(Messages.ADMIN_IMPORTANT_DATES), {
            'fields': ('date_joined', 'last_login', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
