import '../services/api_service.dart';
import '../services/token_manager.dart';
import '../models/user.dart';
import '../../core/config/api_config.dart';
import '../../core/exceptions/app_exceptions.dart';
import '../../core/utils/logger.dart';

/// Repository pour l'authentification OAuth2/JWT
class AuthRepository {
  static const _codeGeneric = 'error.generic';
  static const _codeUnexpected = 'error.unexpected';
  static const _codeNotAuthenticated = 'error.auth.notAuthenticated';
  static const _codeTokensMissing = 'error.auth.tokensMissing';

  final ApiService _apiService;
  final TokenManager _tokenManager;

  AuthRepository({
    required ApiService apiService,
    TokenManager? tokenManager,
  })  : _apiService = apiService,
        _tokenManager = tokenManager ?? TokenManager();

  /// Authentifie un utilisateur via SSO et sauvegarde les tokens JWT
  ///
  /// [provider] : Le fournisseur SSO ('google' ou 'apple')
  /// [token] : Le token ID obtenu du fournisseur SSO
  ///
  /// Retourne l'utilisateur authentifié.
  /// Les tokens JWT (access_token et refresh_token) sont automatiquement
  /// sauvegardés dans le stockage sécurisé.
  ///
  /// Throws [AuthException] si l'authentification échoue.
  Future<User> loginWithSSO({
    required String provider,
    required String token,
  }) async {
    AppLogger.debug('SSO sign-in attempt with provider: $provider');

    return _executeApiCall(
      () => _performSSOLogin(provider, token),
      'SSO login',
    );
  }

  /// Effectue la connexion SSO et sauvegarde les tokens
  ///
  /// [provider] : Le fournisseur SSO
  /// [token] : Le token ID SSO
  ///
  /// Retourne l'utilisateur authentifié.
  Future<User> _performSSOLogin(String provider, String token) async {
    final response = await _apiService.post(
      ApiConfig.authSSOLogin,
      data: {
        'provider': provider,
        'token': token,
      },
    );

    final responseData = _normalizeResponseData(response.data);
    await _saveTokensFromResponse(responseData);

    final user = _parseUserFromResponse(responseData);
    AppLogger.debug('User authenticated: ${user.email}');
    return user;
  }

  /// Sauvegarde les tokens JWT depuis la réponse API
  ///
  /// [responseData] : Les données de réponse contenant les tokens
  ///
  /// Throws [AuthException] si les tokens sont manquants.
  Future<void> _saveTokensFromResponse(
      Map<String, dynamic> responseData) async {
    final accessToken = responseData['access'] as String?;
    final refreshToken = responseData['refresh'] as String?;

    if (accessToken == null || refreshToken == null) {
      throw _authException(
          'JWT tokens missing from API response', _codeTokensMissing);
    }

    await _tokenManager.saveTokens(
      accessToken: accessToken,
      refreshToken: refreshToken,
    );
  }

  /// Récupère l'utilisateur actuel
  ///
  /// Throws [AuthException] si l'utilisateur n'est pas authentifié ou si une erreur survient.
  /// Les erreurs 401/403 (non authentifié) sont gérées silencieusement car c'est un cas normal
  /// au démarrage de l'application.
  Future<User> getCurrentUser() async {
    try {
      final response = await _apiService.get(ApiConfig.authMe);
      final responseData = _normalizeResponseData(response.data);
      return User.fromJson(responseData);
    } on ApiException catch (e) {
      return _handleApiExceptionForCurrentUser(e);
    } catch (e) {
      return _handleUnexpectedErrorForCurrentUser(e);
    }
  }

  /// Gère les exceptions API lors de la récupération de l'utilisateur
  ///
  /// Les erreurs 401/403 sont normales si l'utilisateur n'est pas connecté.
  /// Le message est technique (anglais) pour les logs ; le code sert à l'affichage localisé.
  Never _handleApiExceptionForCurrentUser(ApiException e) {
    if (_isAuthenticationError(e)) {
      throw _authException(
          'User not authenticated', e.code ?? _codeNotAuthenticated);
    }
    AppLogger.error('API error while fetching user', e);
    throw _authException(
        'API error while fetching user', e.code ?? _codeGeneric);
  }

  /// Gère les erreurs inattendues lors de la récupération de l'utilisateur
  Never _handleUnexpectedErrorForCurrentUser(dynamic e) {
    if (e is AuthException) rethrow;
    AppLogger.error('Unexpected error while fetching user', e);
    throw _authException(
        'Unexpected error while fetching user', _codeUnexpected);
  }

  AuthException _authException(String message, String code) =>
      AuthException(message, code: code);

  /// Vérifie si l'erreur est une erreur d'authentification (401/403)
  bool _isAuthenticationError(ApiException e) {
    return e.statusCode == 401 || e.statusCode == 403;
  }

  /// Déconnecte l'utilisateur et supprime les tokens JWT
  ///
  /// Les tokens sont supprimés du stockage sécurisé même en cas d'erreur réseau
  /// pour garantir que l'utilisateur est bien déconnecté localement.
  Future<void> logout() async {
    try {
      await _apiService.post(ApiConfig.authLogout);
    } catch (e) {
      // Ignorer les erreurs lors de la déconnexion côté serveur
      // Les tokens seront supprimés localement de toute façon
      AppLogger.debug('Error ignored during logout: $e');
    } finally {
      // Toujours supprimer les tokens localement
      await _tokenManager.clearTokens();
    }
  }

  /// Exécute un appel API avec gestion d'erreur standardisée
  ///
  /// [operation] : La fonction à exécuter qui retourne le résultat
  /// [errorContext] : Le contexte de l'erreur pour les logs
  ///
  /// Throws [AuthException] si une erreur survient.
  /// Le message est technique (anglais) pour les logs ; le code sert à l'affichage localisé.
  Future<T> _executeApiCall<T>(
    Future<T> Function() operation,
    String errorContext,
  ) async {
    try {
      return await operation();
    } on ApiException catch (e) {
      AppLogger.error('API error during $errorContext', e);
      throw _authException(
          'API error during $errorContext', e.code ?? _codeGeneric);
    } catch (e) {
      if (e is AppException) rethrow;
      AppLogger.error('Unexpected error during $errorContext', e);
      throw _authException(
          'Unexpected error during $errorContext', _codeUnexpected);
    }
  }

  /// Normalise les données de réponse en Map<String, dynamic>
  Map<String, dynamic> _normalizeResponseData(dynamic data) {
    if (data is Map<String, dynamic>) {
      return data;
    }
    if (data is Map) {
      return Map<String, dynamic>.from(data);
    }
    throw _authException(
      'Invalid response format: unstructured data',
      'error.response.unstructuredData',
    );
  }

  /// Parse l'utilisateur depuis la réponse API
  ///
  /// Throws [AuthException] si le format de réponse est invalide.
  User _parseUserFromResponse(Map<String, dynamic> data) {
    final userData = _extractUserData(data);
    return _parseUserFromData(userData);
  }

  /// Extrait les données utilisateur depuis la réponse API
  ///
  /// Throws [AuthException] si les données utilisateur sont manquantes ou invalides.
  Map<String, dynamic> _extractUserData(Map<String, dynamic> data) {
    final userData = data['user'];

    if (userData == null) {
      throw _authException('Invalid response format: user missing',
          'error.response.userMissing');
    }
    if (userData is! Map<String, dynamic>) {
      throw _authException(
        'Invalid response format: user is not an object',
        'error.response.userNotObject',
      );
    }

    return userData;
  }

  /// Parse les données utilisateur en objet User
  ///
  /// Throws [AuthException] si le parsing échoue.
  User _parseUserFromData(Map<String, dynamic> userData) {
    try {
      return User.fromJson(userData);
    } catch (e) {
      AppLogger.error('Error while parsing user', e);
      throw _authException(
          'Invalid response format', 'error.response.invalidFormat');
    }
  }
}
