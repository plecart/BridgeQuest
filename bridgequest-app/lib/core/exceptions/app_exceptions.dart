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

  ApiException(super.message, {super.code, this.statusCode});
}

/// Exception de validation
class ValidationException extends AppException {
  ValidationException(super.message, {super.code});
}

/// Exception de configuration
class ConfigurationException extends AppException {
  ConfigurationException(super.message, {super.code});
}
