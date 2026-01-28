"""
Permissions personnalisées pour Bridge Quest.

Toutes les permissions DRF personnalisées doivent être définies ici.
"""
from rest_framework import permissions


class IsGameAdmin(permissions.BasePermission):
    """
    Permission pour vérifier si l'utilisateur est administrateur d'une partie.
    
    Cette permission sera implémentée lorsque le modèle Game sera créé.
    Elle vérifie que l'utilisateur authentifié est l'administrateur de la partie.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est administrateur de la partie.
        
        Args:
            request: La requête HTTP
            view: La vue appelée
            obj: L'objet Game sur lequel vérifier la permission
            
        Returns:
            bool: True si l'utilisateur est admin de la partie, False sinon
        """
        # À implémenter lorsque le modèle Game sera créé
        # return hasattr(obj, 'admin') and obj.admin == request.user
        return False
    
    def has_permission(self, request, view):
        """
        Vérifie la permission au niveau de la vue.
        
        Args:
            request: La requête HTTP
            view: La vue appelée
            
        Returns:
            bool: True si l'utilisateur est authentifié, False sinon
        """
        return request.user and request.user.is_authenticated
