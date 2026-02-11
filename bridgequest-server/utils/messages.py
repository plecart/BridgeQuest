"""
Clés de traduction pour Bridge Quest.

Ce fichier centralise toutes les clés de traduction utilisées dans l'application.
Les traductions réelles sont dans les fichiers .po générés par `makemessages`.

Organisation :
- Messages : Messages généraux (apps, validators)
- ModelMessages : Labels et noms des modèles Django
- ErrorMessages : Messages d'erreur métier

Pour ajouter une nouvelle clé :
1. Ajouter la constante dans la classe appropriée
2. Utiliser la clé avec _(Messages.KEY) dans le code
3. Générer les fichiers : make makemessages
4. Traduire dans les fichiers .po
5. Compiler : make compilemessages
"""


class Messages:
    """Clés de traduction pour les messages utilisateur."""
    
    # Validators
    GAME_CODE_INVALID_ALPHANUMERIC = "validation.game.code.alphanumeric"
    GAME_CODE_INVALID_LENGTH = "validation.game.code.length"
    
    # Apps verbose names (affichés dans l'admin Django)
    APP_ACCOUNTS = "app.accounts.name"
    APP_GAMES = "app.games.name"
    APP_INTERACTIONS = "app.interactions.name"
    APP_LOCATIONS = "app.locations.name"
    APP_POWERS = "app.powers.name"
    APP_LOGS = "app.logs.name"
    
    # Auth messages
    LOGOUT_SUCCESS = "auth.logout.success"
    SSO_LOGIN_SUCCESS = "auth.sso.login.success"
    
    # Admin fieldsets
    ADMIN_PERSONAL_INFO = "admin.user.personal_info"
    ADMIN_IMPORTANT_DATES = "admin.user.important_dates"
    ADMIN_PERMISSIONS = "admin.user.permissions"
    
    # SSO Serializer
    SSO_PROVIDER_HELP_TEXT = "serializer.sso.provider.help_text"
    SSO_TOKEN_HELP_TEXT = "serializer.sso.token.help_text"


class ModelMessages:
    """Clés de traduction pour les modèles."""
    
    # User
    USER_USERNAME = "model.user.username"
    USER_EMAIL = "model.user.email"
    USER_FIRST_NAME = "model.user.first_name"
    USER_LAST_NAME = "model.user.last_name"
    USER_AVATAR = "model.user.avatar"
    USER_CREATED_AT = "model.user.created_at"
    USER_UPDATED_AT = "model.user.updated_at"
    USER_VERBOSE_NAME = "model.user.verbose_name"
    USER_VERBOSE_NAME_PLURAL = "model.user.verbose_name_plural"
    
    # Game
    GAME_NAME = "model.game.name"
    GAME_CODE = "model.game.code"
    GAME_VERBOSE_NAME = "model.game.verbose_name"
    GAME_VERBOSE_NAME_PLURAL = "model.game.verbose_name_plural"


class ErrorMessages:
    """Clés de traduction pour les messages d'erreur."""
    
    # Auth errors
    AUTH_INVALID_CREDENTIALS = "error.auth.invalid_credentials"
    AUTH_ACCOUNT_EXISTS = "error.auth.account_exists"
    AUTH_ACCOUNT_NOT_FOUND = "error.auth.account_not_found"
    AUTH_TOKEN_INVALID = "error.auth.token_invalid"
    AUTH_TOKEN_EXPIRED = "error.auth.token_expired"
    AUTH_SSO_FAILED = "error.auth.sso_failed"
    AUTH_SSO_PROVIDER_INVALID = "error.auth.sso.provider_invalid"
    AUTH_SSO_TOKEN_REQUIRED = "error.auth.sso.token_required"
    AUTH_SSO_TOKEN_VALIDATION_FAILED = "error.auth.sso.token_validation_failed"
    AUTH_SSO_CONFIG_ERROR = "error.auth.sso.config_error"
    
    # User errors
    USER_NOT_FOUND = "error.user.not_found"
    USER_EMAIL_REQUIRED = "error.user.email_required"
    USER_EMAIL_INVALID = "error.user.email_invalid"
    
    # Game errors
    GAME_NAME_REQUIRED = "error.game.name.required"
    GAME_NOT_FOUND = "error.game.not_found"
    GAME_ALREADY_STARTED = "error.game.already_started"
    
    # Player errors
    PLAYER_NOT_IN_GAME = "error.player.not_in_game"
    PLAYER_ALREADY_IN_GAME = "error.player.already_in_game"
    
    # Interaction errors
    QR_CODE_INVALID = "error.interaction.qr_code.invalid"
    QR_CODE_ALREADY_SCANNED = "error.interaction.qr_code.already_scanned"
    
    # Generic
    UNAUTHORIZED = "error.generic.unauthorized"
    NOT_FOUND = "error.generic.not_found"
    INTERNAL_ERROR = "error.generic.internal"
