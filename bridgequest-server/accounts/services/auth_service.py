"""
Service d'authentification pour Bridge Quest.

Ce service gère toute la logique métier liée à l'authentification SSO mobile.
"""
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from utils.exceptions import BridgeQuestException
from utils.messages import ErrorMessages

User = get_user_model()


def _generate_username_from_email(email):
    """
    Génère un nom d'utilisateur à partir d'un email.
    
    Args:
        email: L'email de l'utilisateur
        
    Returns:
        str: Le nom d'utilisateur généré (partie avant @)
    """
    return email.split('@')[0]


def _generate_unique_username(base_username):
    """
    Génère un nom d'utilisateur unique en ajoutant un suffixe numérique si nécessaire.
    
    Args:
        base_username: Le nom d'utilisateur de base
        
    Returns:
        str: Un nom d'utilisateur unique
    """
    username = base_username
    counter = 1
    
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username


def _update_user_from_sso_data(user, sso_data):
    """
    Met à jour les informations d'un utilisateur à partir des données SSO.
    
    Ne met à jour que les champs vides pour préserver les données existantes.
    
    Args:
        user: L'instance User à mettre à jour
        sso_data: Dictionnaire contenant les données SSO
        
    Returns:
        User: L'utilisateur mis à jour
    """
    updated = False
    
    if sso_data.get('given_name') and not user.first_name:
        user.first_name = sso_data.get('given_name', '')
        updated = True
    
    if sso_data.get('family_name') and not user.last_name:
        user.last_name = sso_data.get('family_name', '')
        updated = True
    
    if sso_data.get('picture') and not user.avatar:
        user.avatar = sso_data.get('picture', '')
        updated = True
    
    if updated:
        user.save()
    
    return user


def get_user_by_email(email):
    """
    Récupère un utilisateur par son email.
    
    Args:
        email: L'email de l'utilisateur
        
    Returns:
        User: L'utilisateur trouvé ou None
        
    Raises:
        BridgeQuestException: Si l'email est invalide
    """
    if not email:
        raise BridgeQuestException(message_key=ErrorMessages.USER_EMAIL_REQUIRED)
    
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    except Exception as e:
        raise BridgeQuestException(message_key=ErrorMessages.USER_NOT_FOUND) from e


def create_or_get_user_from_sso_data(sso_data, provider):
    """
    Crée ou récupère un utilisateur à partir des données SSO validées.
    
    Args:
        sso_data: Dictionnaire contenant les données SSO (email, given_name, etc.)
        provider: Le fournisseur SSO ('google' ou 'apple')
        
    Returns:
        User: L'utilisateur créé ou récupéré
        
    Raises:
        BridgeQuestException: Si la création/récupération échoue
    """
    try:
        email = sso_data.get('email')
        if not email:
            raise BridgeQuestException(message_key=ErrorMessages.USER_EMAIL_REQUIRED)
        
        # Vérifier si un utilisateur avec cet email existe déjà
        user = User.objects.filter(email=email).first()
        
        if user:
            # Mettre à jour les informations si nécessaire
            return _update_user_from_sso_data(user, sso_data)
        
        # Créer un nouvel utilisateur
        base_username = _generate_username_from_email(email)
        username = _generate_unique_username(base_username)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=sso_data.get('given_name', ''),
            last_name=sso_data.get('family_name', ''),
            avatar=sso_data.get('picture', '')
        )
        
        return user
        
    except BridgeQuestException:
        # Re-lancer les exceptions métier telles quelles
        raise
    except Exception as e:
        # Encapsuler les autres exceptions
        raise BridgeQuestException(message_key=ErrorMessages.AUTH_SSO_FAILED) from e
