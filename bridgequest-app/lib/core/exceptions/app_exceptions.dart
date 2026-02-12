/// Exception de base pour l'application.
///
/// [message] : Message technique (anglais) pour les logs.
/// [code] : Clé de traduction pour l'affichage localisé.
/// [serverMessage] : Message déjà traduit renvoyé par le serveur (prioritaire).
abstract class AppException implements Exception {
  final String message;
  final String? code;
  final String? serverMessage;

  AppException(this.message, {this.code, this.serverMessage});

  /// Message à afficher à l'utilisateur.
  ///
  /// Priorité : serverMessage > code (pour traduction) > message technique.
  String get displayMessage => serverMessage ?? code ?? message;

  @override
  String toString() => message;
}

/// Exception d'authentification.
class AuthException extends AppException {
  AuthException(super.message, {super.code, super.serverMessage});
}

/// Exception réseau.
class NetworkException extends AppException {
  NetworkException(super.message, {super.code, super.serverMessage});
}

/// Exception API.
class ApiException extends AppException {
  final int? statusCode;

  ApiException(
    super.message, {
    super.code,
    this.statusCode,
    super.serverMessage,
  });
}

/// Exception de validation.
class ValidationException extends AppException {
  ValidationException(super.message, {super.code, super.serverMessage});
}

/// Exception de configuration.
class ConfigurationException extends AppException {
  ConfigurationException(super.message, {super.code, super.serverMessage});
}

/// Exception liée aux parties de jeu.
class GameException extends AppException {
  GameException(super.message, {super.code, super.serverMessage});
}
