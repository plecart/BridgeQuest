import 'package:dio/dio.dart';
import 'secure_storage_service.dart';
import '../../core/config/api_config.dart';
import '../../core/exceptions/app_exceptions.dart';

/// Service pour les appels API REST
class ApiService {
  final Dio _dio;
  final SecureStorageService _storageService;

  ApiService({
    required String baseUrl,
    required SecureStorageService storageService,
  })  : _storageService = storageService,
        _dio = Dio(
          BaseOptions(
            baseUrl: baseUrl,
            headers: {'Content-Type': 'application/json'},
            connectTimeout: Duration(seconds: ApiConfig.timeoutSeconds),
            receiveTimeout: Duration(seconds: ApiConfig.timeoutSeconds),
          ),
        ) {
    _setupInterceptors();
  }

  /// Configure les intercepteurs HTTP
  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: _addAuthHeader,
        onError: _handleError,
      ),
    );
  }

  /// Ajoute le header d'authentification à la requête
  Future<void> _addAuthHeader(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _storageService.getSessionToken();
    if (token != null) {
      options.headers['Authorization'] = 'Session $token';
    }
    return handler.next(options);
  }

  /// Gère les erreurs HTTP
  void _handleError(
    DioException error,
    ErrorInterceptorHandler handler,
  ) {
    // Les erreurs 401 seront gérées par le AuthProvider
    // via la vérification du token dans les réponses
    return handler.next(error);
  }

  /// Requête GET
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.get(path, queryParameters: queryParameters);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  /// Requête POST
  Future<Response> post(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    try {
      return await _dio.post(path, data: data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  /// Convertit une erreur Dio en exception personnalisée
  AppException _handleDioError(DioException error) {
    if (error.response != null) {
      return _createApiException(error);
    }
    return NetworkException('Erreur de connexion réseau');
  }

  /// Crée une exception API à partir d'une erreur Dio
  ApiException _createApiException(DioException error) {
    final statusCode = error.response!.statusCode;
    final errorData = error.response!.data;
    final errorMessage = _extractErrorMessage(errorData);

    return ApiException(
      errorMessage,
      statusCode: statusCode,
    );
  }

  /// Extrait le message d'erreur de la réponse
  String _extractErrorMessage(dynamic errorData) {
    if (errorData is Map<String, dynamic>) {
      return errorData['error']?.toString() ?? 'Erreur API';
    }
    return 'Erreur API';
  }
}
