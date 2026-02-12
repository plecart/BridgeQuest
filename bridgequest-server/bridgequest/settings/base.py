"""
Base settings for Bridge Quest project.

These settings are shared across all environments (development, production, etc.)
"""
from datetime import timedelta
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# Application definition
# daphne doit être en premier pour gérer HTTP et WebSocket
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'channels',
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'accounts',
    'games',
    'interactions',
    'locations',
    'powers',
    'logs',
]

# Configuration de l'authentification personnalisée
AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware (avant CommonMiddleware)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.middleware.AccessLogMiddleware',  # Logs HTTP unifiés (format cohérent avec Daphne)
]

ROOT_URLCONF = 'bridgequest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bridgequest.wsgi.application'
ASGI_APPLICATION = 'bridgequest.asgi.application'

# Channel layers pour WebSocket (synchronisation temps réel)
# En développement : InMemoryChannelLayer (pas de Redis requis)
# En production : configurer channels_redis avec REDIS_URL
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Gardé pour compatibilité admin Django
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

# CORS settings (pour permettre les requêtes depuis Flutter en développement)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)

CORS_ALLOW_CREDENTIALS = True

# Authentification
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# SSO Configuration
# Apple Sign-In - Client ID (Bundle ID de l'app iOS)
APPLE_CLIENT_ID = config('APPLE_CLIENT_ID', default='')

# Google Sign-In - Liste des Client IDs autorisés (Web, iOS, Android)
# Plusieurs IDs car Google génère un ID différent par plateforme
GOOGLE_CLIENT_IDS = config(
    'GOOGLE_CLIENT_IDS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()] if v else []
)

# Simple JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Token d'accès valide 1 heure
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # Refresh token valide 30 jours
    'ROTATE_REFRESH_TOKENS': True,  # Générer un nouveau refresh token à chaque refresh
    'BLACKLIST_AFTER_ROTATION': True,  # Blacklister l'ancien refresh token après rotation
    'UPDATE_LAST_LOGIN': True,  # Mettre à jour last_login à chaque authentification
    'ALGORITHM': 'HS256',  # Algorithme de signature
    'SIGNING_KEY': SECRET_KEY,  # Clé de signature (utilise SECRET_KEY Django)
    'AUTH_HEADER_TYPES': ('Bearer',),  # Format du header Authorization
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',  # Nom du header HTTP
    'USER_ID_FIELD': 'id',  # Champ utilisé comme identifiant utilisateur dans le token
    'USER_ID_CLAIM': 'user_id',  # Claim JWT contenant l'ID utilisateur
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}
