"""
Production settings for Bridge Quest project.

These settings are used for production deployment.
"""
# L'import * est intentionnel pour hériter de tous les settings de base
# C'est la pratique standard Django pour les fichiers de settings
from .base import *  # noqa: F401, F403
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)

# Security settings pour la production
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database - PostgreSQL en production (à configurer)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='5432'),
#     }
# }

# Static files - servir via Nginx ou CDN en production
STATIC_ROOT = config('STATIC_ROOT', default=BASE_DIR / 'staticfiles')

# Redis — requis pour WebSocket (channel layers) et cache partagé (lobby_service)
# Fail-fast : pas de fallback vers InMemoryChannelLayer/LocMemCache (non partagé entre workers)
_REDIS_URL_REQUIRED_MSG = (
    'REDIS_URL doit être défini en production pour les WebSockets. '
    'Exemple : redis://localhost:6379/0'
)
_redis_url = config('REDIS_URL', default='')
if not _redis_url:
    raise ValueError(_REDIS_URL_REQUIRED_MSG)

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [_redis_url]},
    },
}

# Cache partagé requis pour lobby_service (exclusions en attente)
# Sans CACHES explicite : LocMemCache par process → incohérences multi-workers
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': _redis_url,
    },
}

# Logging pour la production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'bridgequest': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
