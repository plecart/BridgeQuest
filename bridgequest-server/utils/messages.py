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
    # Utiliser du texte lisible comme msgid pour affichage correct sans .mo compilé
    APP_ACCOUNTS = "Authentication"
    APP_GAMES = "Games"
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
    USER_VERBOSE_NAME = "User"
    USER_VERBOSE_NAME_PLURAL = "Users"
    
    # Game
    GAME_CODE = "model.game.code"
    GAME_STATE = "model.game.state"
    GAME_STATE_WAITING = "model.game.state.waiting"
    GAME_STATE_DEPLOYMENT = "model.game.state.deployment"
    GAME_STATE_IN_PROGRESS = "model.game.state.in_progress"
    GAME_STATE_FINISHED = "model.game.state.finished"
    GAME_DEPLOYMENT_ENDS_AT = "model.game.deployment_ends_at"
    GAME_GAME_ENDS_AT = "model.game.game_ends_at"
    GAME_CREATED_AT = "model.game.created_at"
    GAME_UPDATED_AT = "model.game.updated_at"
    GAME_VERBOSE_NAME = "Game"
    GAME_VERBOSE_NAME_PLURAL = "Games"

    # Player
    PLAYER_USER = "model.player.user"
    PLAYER_GAME = "model.player.game"
    PLAYER_IS_ADMIN = "model.player.is_admin"
    PLAYER_ROLE = "model.player.role"
    PLAYER_SCORE = "model.player.score"
    PLAYER_CONVERTED_AT = "model.player.converted_at"
    PLAYER_JOINED_AT = "model.player.joined_at"
    PLAYER_VERBOSE_NAME = "Player"
    PLAYER_VERBOSE_NAME_PLURAL = "Players"
    PLAYER_STR_DISPLAY = "{user} in {game}"
    PLAYER_ROLE_HUMAN = "model.player.role.human"
    PLAYER_ROLE_SPIRIT = "model.player.role.spirit"

    # GameSettings
    SETTINGS_VERBOSE_NAME = "Game Settings"
    SETTINGS_VERBOSE_NAME_PLURAL = "Game Settings"
    SETTINGS_STR_DISPLAY = "Settings for {game}"
    SETTINGS_GAME = "model.settings.game"
    SETTINGS_GAME_DURATION = "model.settings.game_duration"
    SETTINGS_DEPLOYMENT_DURATION = "model.settings.deployment_duration"
    SETTINGS_SPIRIT_PERCENTAGE = "model.settings.spirit_percentage"
    SETTINGS_POINTS_PER_MINUTE = "model.settings.points_per_minute"
    SETTINGS_CONVERSION_POINTS_PERCENTAGE = "model.settings.conversion_points_percentage"

    # Position
    POSITION_PLAYER = "model.position.player"
    POSITION_LATITUDE = "model.position.latitude"
    POSITION_LONGITUDE = "model.position.longitude"
    POSITION_RECORDED_AT = "model.position.recorded_at"
    POSITION_VERBOSE_NAME = "Position"
    POSITION_VERBOSE_NAME_PLURAL = "Positions"


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
    GAME_NOT_FOUND = "error.game.not_found"
    GAME_CODE_NOT_FOUND = "error.game.code.not_found"
    GAME_ALREADY_STARTED = "error.game.already_started"

    # Player errors
    PLAYER_NOT_IN_GAME = "error.player.not_in_game"
    PLAYER_ALREADY_IN_GAME = "error.player.already_in_game"
    PLAYER_NOT_ADMIN = "error.player.not_admin"
    
    # Settings errors
    SETTINGS_NOT_FOUND = "error.settings.not_found"
    SETTINGS_GAME_NOT_WAITING = "error.settings.game_not_waiting"

    # Lifecycle errors
    GAME_NOT_ENOUGH_PLAYERS = "error.game.not_enough_players"
    GAME_NOT_DEPLOYMENT = "error.game.not_deployment"
    GAME_NOT_IN_PROGRESS = "error.game.not_in_progress"

    # Interaction errors
    QR_CODE_INVALID = "error.interaction.qr_code.invalid"
    QR_CODE_ALREADY_SCANNED = "error.interaction.qr_code.already_scanned"

    # Position/Location errors
    POSITION_GAME_NOT_ACTIVE = "error.position.game_not_active"
    POSITION_COORDINATES_INVALID = "error.position.coordinates_invalid"
    
    # Generic
    UNAUTHORIZED = "error.generic.unauthorized"
    NOT_FOUND = "error.generic.not_found"
    INTERNAL_ERROR = "error.generic.internal"
