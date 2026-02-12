import 'dart:async';

import 'package:dio/dio.dart';
import '../../core/config/api_config.dart';
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
  Future<bool>? _refreshFuture;

  ApiService({
    required String baseUrl,
    TokenManager? tokenManager,
  })  : _tokenManager = tokenManager ?? TokenManager(),
        _dio = Dio(
          BaseOptions(
            baseUrl: baseUrl,
            headers: const {'Content-Type': 'application/json'},
            connectTimeout: const Duration(
              seconds: ApiConfig.timeoutSeconds,
            ), // ignore: prefer_const_constructors
            receiveTimeout: const Duration(
              seconds: ApiConfig.timeoutSeconds,
            ), // ignore: prefer_const_constructors
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
          if (_shouldRetryAfterRefresh(error)) {
            final retried = await _retryRequestAfterRefresh(error, handler);
            if (retried) return;
          }
          handler.next(error);
        },
      ),
    );
  }

  /// Indique si l'erreur doit déclencher un retry après refresh du token.
  ///
  /// Retourne true uniquement pour un 401 sur une requête autre que l'endpoint
  /// de refresh (évite le cycle 401 → refresh → 401 sur la route de refresh).
  bool _shouldRetryAfterRefresh(DioException error) {
    return _isUnauthorizedError(error) && !_isRefreshRequest(error);
  }

  /// Vérifie si l'erreur est une erreur d'authentification (401)
  bool _isUnauthorizedError(DioException error) {
    return error.response?.statusCode == 401;
  }

  /// Vérifie si la requête en erreur cible l'endpoint de refresh.
  ///
  /// Ne pas retry sur cette route évite un cycle infini : un 401 sur le refresh
  /// repasserait par l'intercepteur et rappellerait le refresh.
  bool _isRefreshRequest(DioException error) {
    return error.requestOptions.path == ApiConfig.authTokenRefresh;
  }

  /// Réessaie une requête après avoir rafraîchi le token.
  ///
  /// Retourne true si l'erreur a été traitée (retry effectué ou échec propagé),
  /// false si le refresh a échoué et qu'on n'a pas retry.
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
      _rejectWithRetryError(opts, e, handler);
      return true;
    }
  }

  /// Propage l'erreur du retry (500/404/etc.) plutôt que le 401 d'origine.
  void _rejectWithRetryError(
    RequestOptions opts,
    dynamic error,
    ErrorInterceptorHandler handler,
  ) {
    final retryError = error is DioException
        ? error
        : DioException(requestOptions: opts, error: error);
    handler.reject(retryError);
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
  /// Si plusieurs requêtes reçoivent un 401 simultanément, elles partagent le même
  /// refresh et attendent toutes sa complétion (évite les refresh en parallèle et
  /// les échecs inutiles quand une requête arrive pendant un refresh en cours).
  Future<bool> _refreshTokenIfNeeded() async {
    if (_refreshFuture != null) {
      return _refreshFuture!;
    }

    final completer = Completer<bool>();
    _refreshFuture = completer.future;

    try {
      final result = await _performTokenRefresh();
      completer.complete(result);
      return result;
    } catch (e) {
      completer.complete(false);
      return false;
    } finally {
      _refreshFuture = null;
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
      return _createNetworkException('Connection timeout', 'error.api.timeout');
    }
    if (_isConnectionError(error)) {
      return _createNetworkException(
        'Network connection error',
        'error.network',
      );
    }
    if (error.response != null) {
      return _createApiException(error);
    }
    return _createNetworkException(
      'Unknown network error',
      'error.api.unknown',
    );
  }

  bool _isTimeoutError(DioException error) =>
      error.type == DioExceptionType.connectionTimeout ||
      error.type == DioExceptionType.receiveTimeout ||
      error.type == DioExceptionType.sendTimeout;

  bool _isConnectionError(DioException error) =>
      error.type == DioExceptionType.connectionError;

  NetworkException _createNetworkException(String message, String code) =>
      NetworkException(message, code: code);

  /// Crée une exception API à partir d'une erreur Dio
  ///
  /// Le [message] est technique (anglais) pour les logs. Le [code] sert à l'affichage localisé.
  /// Les erreurs 401/403 (authentification) ne sont pas loggées car elles peuvent être
  /// des cas normaux (ex: vérification de l'état d'authentification au démarrage).
  ApiException _createApiException(DioException error) {
    final statusCode = error.response!.statusCode!;
    final errorData = error.response!.data;
    final serverMessage = _extractServerErrorMessage(errorData);

    _logApiErrorIfNeeded(statusCode, errorData);

    return ApiException(
      'API error: $statusCode',
      code: 'error.api.generic',
      statusCode: statusCode,
      serverMessage: serverMessage,
    );
  }

  /// Extrait le message d'erreur du body de réponse API (format {"error": "..."}).
  String? _extractServerErrorMessage(dynamic data) {
    if (data is Map && data.containsKey('error')) {
      final error = data['error'];
      if (error is String && error.isNotEmpty) return error;
    }
    return null;
  }

  /// Log une erreur API si nécessaire
  ///
  /// Les erreurs 401/403 (authentification) ne sont pas loggées car ce sont des cas normaux
  /// lors de la vérification de l'état d'authentification.
  void _logApiErrorIfNeeded(int statusCode, dynamic errorData) {
    if (statusCode != 401 && statusCode != 403) {
      AppLogger.error(
        'API error - Status: $statusCode',
        errorData,
      );
    }
  }
}
