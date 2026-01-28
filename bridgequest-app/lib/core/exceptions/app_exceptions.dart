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
  AuthException(String message, {String? code})
      : super(message, code: code);
}

/// Exception réseau
class NetworkException extends AppException {
  NetworkException(String message, {String? code})
      : super(message, code: code);
}

/// Exception API
class ApiException extends AppException {
  final int? statusCode;

  ApiException(String message, {String? code, this.statusCode})
      : super(message, code: code);
}

/// Exception de validation
class ValidationException extends AppException {
  ValidationException(String message, {String? code})
      : super(message, code: code);
}
