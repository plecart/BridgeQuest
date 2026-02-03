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

/// Exception API (réponse HTTP d'erreur).
///
/// Utiliser [isClientError] / [isServerError] pour adapter le message
/// (voir CODING_STANDARDS_FLUTTER.md : 4xx = message API, 5xx = message générique).
class ApiException extends AppException {
  final int? statusCode;

  ApiException(super.message, {super.code, this.statusCode});

  /// True si le code HTTP indique une erreur client (4xx).
  bool get isClientError =>
      statusCode != null && statusCode! >= 400 && statusCode! < 500;

  /// True si le code HTTP indique une erreur serveur (5xx).
  bool get isServerError => statusCode != null && statusCode! >= 500;
}

/// Exception de validation
class ValidationException extends AppException {
  ValidationException(super.message, {super.code});
}

/// Exception de configuration
class ConfigurationException extends AppException {
  ConfigurationException(super.message, {super.code});
}
