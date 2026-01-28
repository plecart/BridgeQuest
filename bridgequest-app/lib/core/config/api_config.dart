/// Configuration de l'API
class ApiConfig {
  ApiConfig._();

  /// URL de base de l'API backend
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  /// Timeout pour les requêtes HTTP (en secondes)
  static const int timeoutSeconds = 30;

  /// Endpoints de l'API
  static const String authSSOLogin = '/api/auth/sso/login/';
  static const String authMe = '/api/auth/me/';
  static const String authLogout = '/api/auth/logout/';
}
