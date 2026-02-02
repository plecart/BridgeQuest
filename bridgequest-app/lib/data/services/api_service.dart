import 'package:dio/dio.dart';

import '../../core/config/api_config.dart';
import '../../core/config/app_localizations_holder.dart';
import '../../core/exceptions/app_exceptions.dart';
import '../../core/utils/logger.dart';
import 'token_manager.dart';

/// Service pour les appels API REST avec authentification OAuth2/JWT
/// 
/// Ce service gère toutes les requêtes HTTP vers l'API backend en utilisant
/// des tokens JWT pour l'authentification. Les tokens sont automatiquement
/// ajoutés aux headers et rafraîchis si nécessaire.
class ApiService {
  final Dio _dio;
  final TokenManager _tokenManager;
  bool _isRefreshing = false;

  ApiService({
    required String baseUrl,
    TokenManager? tokenManager,
  })  : _tokenManager = tokenManager ?? TokenManager(),
        _dio = Dio(
          BaseOptions(
            baseUrl: baseUrl,
            headers: const {'Content-Type': 'application/json'},
            connectTimeout: Duration(seconds: ApiConfig.timeoutSeconds), // ignore: prefer_const_constructors
            receiveTimeout: Duration(seconds: ApiConfig.timeoutSeconds), // ignore: prefer_const_constructors
            // Duration ne peut pas être const car ApiConfig.timeoutSeconds n'est pas une constante compile-time
          ),
        ) {
    _setupInterceptors();
    _preloadToken();
  }

  /// Précharge le token en mémoire pour éviter les accès bloquants au stockage
  /// 
  /// Cette méthode charge le token de manière asynchrone au démarrage pour
  /// améliorer les performances des requêtes suivantes.
  /// Le Future n'est pas attendu pour ne pas bloquer l'initialisation.
  void _preloadToken() {
    // ignore: unawaited_futures
    // Le Future est intentionnellement non attendu pour ne pas bloquer l'initialisation
    _tokenManager.getAccessToken();
  }

  /// Configure les intercepteurs HTTP pour l'authentification JWT
  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          await _addAuthTokenIfNeeded(options);
          handler.next(options);
        },
        onError: (error, handler) async {
          if (_isUnauthorizedError(error)) {
            final retried = await _retryRequestAfterRefresh(error, handler);
            if (retried) return;
          }
          handler.next(error);
        },
      ),
    );
  }

  /// Vérifie si l'erreur est une erreur d'authentification (401)
  bool _isUnauthorizedError(DioException error) {
    return error.response?.statusCode == 401;
  }

  /// Réessaie une requête après avoir rafraîchi le token (auth JWT Bearer, pas de cookies).
  /// 
  /// Retourne true si la requête a été réessayée avec succès, false sinon.
  Future<bool> _retryRequestAfterRefresh(
    DioException error,
    ErrorInterceptorHandler handler,
  ) async {
    final refreshed = await _refreshTokenIfNeeded();
    if (!refreshed) return false;

    final opts = error.requestOptions;
    await _addAuthTokenIfNeeded(opts);
    
    try {
      final response = await _dio.fetch(opts);
      handler.resolve(response);
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Ajoute le token d'authentification au header si disponible
  Future<void> _addAuthTokenIfNeeded(RequestOptions options) async {
    final accessToken = await _tokenManager.getAccessToken();
    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
  }

  /// Rafraîchit le token d'accès si nécessaire
  /// 
  /// Retourne true si le token a été rafraîchi avec succès, false sinon.
  /// Évite les refresh multiples simultanés en utilisant un flag de verrouillage.
  Future<bool> _refreshTokenIfNeeded() async {
    if (_isRefreshing) {
      return false;
    }

    _isRefreshing = true;

    try {
      return await _performTokenRefresh();
    } finally {
      _isRefreshing = false;
    }
  }

  /// Effectue le rafraîchissement du token d'accès
  /// 
  /// Retourne true si le refresh réussit, false sinon.
  /// En cas d'erreur, supprime les tokens pour forcer une nouvelle authentification.
  Future<bool> _performTokenRefresh() async {
    final refreshToken = await _tokenManager.getRefreshToken();
    if (refreshToken == null) {
      return false;
    }

    try {
      final response = await _dio.post(
        ApiConfig.authTokenRefresh,
        data: {'refresh': refreshToken},
      );

      final newAccessToken = response.data['access'] as String?;
      if (newAccessToken != null) {
        await _tokenManager.updateAccessToken(newAccessToken);
        return true;
      }

      return false;
    } catch (e) {
      // En cas d'erreur, supprimer les tokens (déconnexion forcée)
      await _tokenManager.clearTokens();
      return false;
    }
  }

  /// Requête GET
  /// 
  /// [path] : Chemin de l'endpoint (relatif à baseUrl)
  /// [queryParameters] : Paramètres de requête optionnels
  /// 
  /// Throws [AppException] si une erreur survient.
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    return _executeRequest(
      () => _dio.get(path, queryParameters: queryParameters),
    );
  }

  /// Requête POST
  /// 
  /// [path] : Chemin de l'endpoint (relatif à baseUrl)
  /// [data] : Données à envoyer dans le body
  /// 
  /// Throws [AppException] si une erreur survient.
  Future<Response> post(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    return _executeRequest(() => _dio.post(path, data: data));
  }

  /// Requête PUT
  /// 
  /// [path] : Chemin de l'endpoint (relatif à baseUrl)
  /// [data] : Données à envoyer dans le body
  /// 
  /// Throws [AppException] si une erreur survient.
  Future<Response> put(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    return _executeRequest(() => _dio.put(path, data: data));
  }

  /// Requête DELETE
  /// 
  /// [path] : Chemin de l'endpoint (relatif à baseUrl)
  /// 
  /// Throws [AppException] si une erreur survient.
  Future<Response> delete(String path) async {
    return _executeRequest(() => _dio.delete(path));
  }

  /// Requête PATCH
  /// 
  /// [path] : Chemin de l'endpoint (relatif à baseUrl)
  /// [data] : Données à envoyer dans le body
  /// 
  /// Throws [AppException] si une erreur survient.
  Future<Response> patch(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    return _executeRequest(() => _dio.patch(path, data: data));
  }

  /// Exécute une requête HTTP et gère les erreurs
  Future<Response> _executeRequest(Future<Response> Function() request) async {
    try {
      return await request();
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  /// Convertit une erreur Dio en exception personnalisée
  AppException _handleDioError(DioException error) {
    if (_isTimeoutError(error)) {
      return _createTimeoutException();
    }

    if (_isConnectionError(error)) {
      return _createConnectionException();
    }

    if (error.response != null) {
      return _createApiException(error);
    }

    return _createUnknownNetworkException();
  }

  /// Vérifie si l'erreur est un timeout
  bool _isTimeoutError(DioException error) {
    return error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.sendTimeout;
  }

  /// Vérifie si l'erreur est une erreur de connexion
  bool _isConnectionError(DioException error) {
    return error.type == DioExceptionType.connectionError;
  }

  /// Crée une exception réseau avec un code l10n (message = code pour [ErrorTranslator])
  NetworkException _createNetworkException(String code) {
    return NetworkException(code, code: code);
  }

  /// Crée une exception de timeout
  NetworkException _createTimeoutException() =>
      _createNetworkException('error.api.timeout');

  /// Crée une exception de connexion
  NetworkException _createConnectionException() =>
      _createNetworkException('error.network');

  /// Crée une exception réseau inconnue
  NetworkException _createUnknownNetworkException() =>
      _createNetworkException('error.api.unknown');

  /// Crée une exception API à partir d'une erreur Dio
  /// 
  /// Les erreurs 401/403 (authentification) ne sont pas loggées car elles peuvent être
  /// des cas normaux (ex: vérification de l'état d'authentification au démarrage).
  ApiException _createApiException(DioException error) {
    final statusCode = error.response!.statusCode!;
    final errorData = error.response!.data;
    
    _logApiErrorIfNeeded(statusCode, errorData);
    final errorMessage = _extractErrorMessage(errorData);

    return ApiException(
      errorMessage,
      code: 'error.api.generic',
      statusCode: statusCode,
    );
  }

  /// Log une erreur API si nécessaire
  /// 
  /// Les erreurs 401/403 (authentification) ne sont pas loggées car ce sont des cas normaux
  /// lors de la vérification de l'état d'authentification.
  void _logApiErrorIfNeeded(int statusCode, dynamic errorData) {
    if (statusCode != 401 && statusCode != 403) {
      final l10n = AppLocalizationsHolder.current;
      AppLogger.error(
        l10n?.logErrorApiStatus(statusCode) ?? 'logErrorApiStatus($statusCode)',
        errorData,
      );
    }
  }

  /// Extrait le message d'erreur de la réponse
  /// 
  /// Les réponses d'erreur Django peuvent avoir différents formats :
  /// - Map avec 'error', 'message' ou 'detail'
  /// - String directe
  /// Cette méthode normalise tous ces formats en un message unique.
  String _extractErrorMessage(dynamic errorData) {
    if (errorData is Map<String, dynamic>) {
      return _extractErrorMessageFromMap(errorData);
    }
    if (errorData is String) {
      return errorData;
    }
    return 'error.api.generic';
  }

  /// Extrait le message d'erreur depuis une Map
  ///
  /// Cherche dans l'ordre : 'error', 'message', 'detail'. Sinon retourne le code l10n.
  String _extractErrorMessageFromMap(Map<String, dynamic> errorData) {
    return errorData['error']?.toString() ??
        errorData['message']?.toString() ??
        errorData['detail']?.toString() ??
        'error.api.generic';
  }
}
