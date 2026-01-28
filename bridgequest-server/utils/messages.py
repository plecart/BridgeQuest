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
    
    # Apps verbose names
    APP_ACCOUNTS = "app.accounts.name"
    APP_GAMES = "app.games.name"
    APP_INTERACTIONS = "app.interactions.name"
    APP_LOCATIONS = "app.locations.name"
    APP_POWERS = "app.powers.name"
    APP_LOGS = "app.logs.name"


class ModelMessages:
    """Clés de traduction pour les modèles."""
    
    # Game
    GAME_NAME = "model.game.name"
    GAME_CODE = "model.game.code"
    GAME_VERBOSE_NAME = "model.game.verbose_name"
    GAME_VERBOSE_NAME_PLURAL = "model.game.verbose_name_plural"


class ErrorMessages:
    """Clés de traduction pour les messages d'erreur."""
    
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
