"""
Permissions personnalisées pour Bridge Quest.
"""
from rest_framework import permissions


class IsGameAdmin(permissions.BasePermission):
    """
    Permission pour vérifier si l'utilisateur est administrateur d'une partie.
    
    Cette permission sera implémentée lorsque le modèle Game sera créé.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est administrateur de la partie.
        
        Args:
            request: La requête HTTP
            view: La vue appelée
            obj: L'objet sur lequel vérifier la permission
            
        Returns:
            bool: True si l'utilisateur est admin, False sinon
        """
        # À implémenter lorsque le modèle Game sera créé
        # return obj.admin == request.user
        return False
