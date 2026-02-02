import '../services/api_service.dart';
import '../services/token_manager.dart';
import '../models/user.dart';
import '../../core/config/api_config.dart';
import '../../core/config/app_localizations_holder.dart';
import '../../core/exceptions/app_exceptions.dart';
import '../../core/utils/logger.dart';

/// Repository pour l'authentification OAuth2/JWT
class AuthRepository {
  static const _errorCodeNotAuthenticated = 'error.auth.notAuthenticated';
  static const _errorCodeGeneric = 'error.generic';

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
    final l10n = AppLocalizationsHolder.current;
    AppLogger.debug(l10n?.logDebugSsoAttempt(provider) ?? 'logDebugSsoAttempt');

    return _executeApiCall(
      () => _performSSOLogin(provider, token),
      l10n?.logContextSsoLogin ?? 'logContextSsoLogin',
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
    final l10n = AppLocalizationsHolder.current;
    AppLogger.debug(l10n?.logDebugUserAuthenticated(user.email) ?? 'logDebugUserAuthenticated');
    return user;
  }

  /// Sauvegarde les tokens JWT depuis la réponse API
  /// 
  /// [responseData] : Les données de réponse contenant les tokens
  /// 
  /// Throws [AuthException] si les tokens sont manquants.
  Future<void> _saveTokensFromResponse(Map<String, dynamic> responseData) async {
    final accessToken = responseData['access'] as String?;
    final refreshToken = responseData['refresh'] as String?;
    
    if (accessToken == null || refreshToken == null) {
      throw _authError('error.auth.tokensMissing');
    }
    
    await _tokenManager.saveTokens(
      accessToken: accessToken,
      refreshToken: refreshToken,
    );
  }

  /// Récupère l'utilisateur actuel
  ///
  /// Throws [AuthException] si l'utilisateur n'est pas authentifié ou si une erreur survient.
  /// Les erreurs 401/403 (non authentifié) sont gérées silencieusement (cas normal au démarrage).
  Future<User> getCurrentUser() async {
    try {
      final response = await _apiService.get(ApiConfig.authMe);
      final responseData = _normalizeResponseData(response.data);
      return _parseUserFromFlatResponse(responseData);
    } on ApiException catch (e) {
      return _handleApiExceptionForCurrentUser(e);
    } catch (e) {
      return _handleUnexpectedErrorForCurrentUser(e);
    }
  }

  /// Gère les exceptions API lors de la récupération de l'utilisateur.
  ///
  /// 401/403 : code dérivé de [ApiException.statusCode] (ApiService met toujours [ApiException.code] à une valeur générique).
  Never _handleApiExceptionForCurrentUser(ApiException e) {
    if (_isAuthenticationError(e)) {
      throw _authError(_errorCodeNotAuthenticated);
    }
    AppLogger.error(
      AppLocalizationsHolder.current?.logErrorApiUserFetch ?? 'logErrorApiUserFetch',
      e,
    );
    throw _authError(e.code ?? _errorCodeGeneric);
  }

  /// Gère les erreurs inattendues lors de la récupération de l'utilisateur
  Never _handleUnexpectedErrorForCurrentUser(dynamic e) {
    if (e is AuthException) throw e;
    AppLogger.error(
      AppLocalizationsHolder.current?.logErrorUnexpectedUserFetch ?? 'logErrorUnexpectedUserFetch',
      e,
    );
    throw _authError('error.unexpected');
  }

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
      final l10n = AppLocalizationsHolder.current;
      AppLogger.debug(l10n?.logDebugLogoutError(e.toString()) ?? 'logDebugLogoutError');
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
  Future<T> _executeApiCall<T>(
    Future<T> Function() operation,
    String errorContext,
  ) async {
    try {
      return await operation();
    } on ApiException catch (e) {
      final l10n = AppLocalizationsHolder.current;
      AppLogger.error(
        l10n?.logErrorApiContext(errorContext) ?? 'logErrorApiContext',
        e,
      );
      throw _authError(e.code ?? _errorCodeGeneric);
    } catch (e) {
      if (e is AppException) rethrow;
      final l10n = AppLocalizationsHolder.current;
      AppLogger.error(
        l10n?.logErrorUnexpectedContext(errorContext) ?? 'logErrorUnexpectedContext',
        e,
      );
      throw _authError('error.unexpected');
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
    throw _authError('error.response.unstructuredData');
  }

  /// Lance une [AuthException] avec un code l10n (message = code pour affichage via [ErrorTranslator]).
  Never _authError(String code) {
    throw AuthException(code, code: code);
  }

  /// Parse l'utilisateur depuis une réponse API au format plat (ex. endpoint current user).
  User _parseUserFromFlatResponse(Map<String, dynamic> data) {
    return _parseUserFromData(data);
  }

  /// Parse l'utilisateur depuis une réponse API encapsulée (ex. login : { "user": {...} }).
  User _parseUserFromResponse(Map<String, dynamic> data) {
    return _parseUserFromData(_extractUserData(data));
  }

  /// Extrait les données utilisateur depuis la réponse API
  /// 
  /// Throws [AuthException] si les données utilisateur sont manquantes ou invalides.
  Map<String, dynamic> _extractUserData(Map<String, dynamic> data) {
    final userData = data['user'];
    
    if (userData == null) {
      throw _authError('error.response.userMissing');
    }
    if (userData is! Map<String, dynamic>) {
      throw _authError('error.response.userNotObject');
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
      AppLogger.error(
        AppLocalizationsHolder.current?.logErrorUserParse ?? 'logErrorUserParse',
        e,
      );
      throw _authError('error.response.invalidFormat');
    }
  }

}
