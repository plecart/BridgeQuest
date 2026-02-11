/// Exception de base pour l'application
abstract class AppException implements Exception {
  final String message;
  final String? code;

  AppException(this.message, {this.code});

  @override
  String toString() => message;
}

/// Exception d'authentification
class AuthException extends AppException {
  AuthException(super.message, {super.code});
}

/// Exception réseau
class NetworkException extends AppException {
  NetworkException(super.message, {super.code});
}

/// Exception API
class ApiException extends AppException {
  final int? statusCode;

  /// Message d'erreur renvoyé par le serveur (ex: {"error": "..."}).
  /// Utiliser pour l'affichage quand le backend envoie un message déjà traduit.
  final String? serverMessage;

  ApiException(
    super.message, {
    super.code,
    this.statusCode,
    this.serverMessage,
  });
}

/// Exception de validation
class ValidationException extends AppException {
  ValidationException(super.message, {super.code});
}

/// Exception de configuration
class ConfigurationException extends AppException {
  ConfigurationException(super.message, {super.code});
}

/// Exception liée aux parties de jeu
///
/// [serverMessage] : Message déjà traduit renvoyé par le backend (prioritaire pour l'affichage).
/// [code] : Clé de traduction à utiliser si [serverMessage] est null.
class GameException extends AppException {
  final String? serverMessage;

  GameException(super.message, {super.code, this.serverMessage});

  /// Message à afficher à l'utilisateur (serverMessage ou code pour traduction).
  String get displayMessage => serverMessage ?? code ?? message;
}
