"""
Settings spécifiques pour les tests.

Ces settings sont utilisés uniquement lors de l'exécution des tests.
Ils optimisent les performances et réduisent le bruit dans la sortie des tests.
"""
# L'import * est intentionnel pour hériter de tous les settings de base
# C'est la pratique standard Django pour les fichiers de settings
from .base import *  # noqa: F401, F403


class DisableMigrations:
    """
    Classe pour désactiver les migrations pendant les tests.
    
    Cela accélère considérablement l'exécution des tests en évitant
    l'application des migrations. Django crée directement les tables
    en mémoire à partir des modèles.
    """
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None


# Optimisations pour les tests
MIGRATION_MODULES = DisableMigrations()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CACHES = {
    'default': {
        # LocMemCache requis pour les tests du lobby_service (exclusion après déconnexion)
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

DEBUG = False

# Password hashing rapide pour les tests uniquement
# ATTENTION: Ne jamais utiliser MD5 en production !
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Logging optimisé pour les tests - Sortie claire et lisible
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'test': {
            'format': '{levelname:8} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'test',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',  # Ignorer les 4xx (Forbidden, Not Found) pendant les tests
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'bridgequest': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
