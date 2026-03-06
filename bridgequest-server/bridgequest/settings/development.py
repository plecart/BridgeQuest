"""
Development settings for Bridge Quest project.

These settings are used for local development.
"""
# L'import * est intentionnel pour hériter de tous les settings de base
# C'est la pratique standard Django pour les fichiers de settings
from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '10.0.2.2']  # 10.0.2.2 pour l'émulateur Android

# Django REST Framework - Mode développement
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Interface browsable en dev
    ],
})

# CORS - Plus permissif en développement
# ATTENTION: Ne jamais utiliser en production !
CORS_ALLOW_ALL_ORIGINS = True

# Logging pour le développement
# Format standardisé : {levelname:8} {asctime} [{module:15}] {message}
# Tous les logs (Django, Daphne, Twisted, bridgequest) utilisent ce format unifié
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{levelname:8} {asctime} [{module:15}] {message}',
            'style': '{',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',  # Ignorer les warnings HTTP 4xx (Forbidden, Not Found) en développement
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'daphne': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Désactiver les access logs natifs de Twisted (remplacés par AccessLogMiddleware)
        # Les access logs Twisted sont également désactivés via --access-log=/dev/null dans le Makefile
        'twisted.web.http': {
            'handlers': [],
            'level': 'WARNING',
            'propagate': False,
        },
        'twisted.web': {
            'handlers': [],
            'level': 'WARNING',
            'propagate': False,
        },
        'bridgequest': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'bridgequest.access': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
