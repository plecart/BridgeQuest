import 'package:dio/dio.dart';
import 'secure_storage_service.dart';
import '../../core/config/api_config.dart';
import '../../core/exceptions/app_exceptions.dart';
import '../../core/utils/logger.dart';

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

  /// Gère les erreurs HTTP dans les intercepteurs
  void _handleError(
    DioException error,
    ErrorInterceptorHandler handler,
  ) {
    // Les erreurs sont gérées dans les méthodes get/post via _handleDioError
    // L'intercepteur laisse passer l'erreur pour traitement ultérieur
    handler.next(error);
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
    return _executeRequest(() => _dio.get(path, queryParameters: queryParameters));
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
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.sendTimeout) {
      return NetworkException(
        'Timeout de connexion',
        code: 'error.api.timeout',
      );
    }

    if (error.type == DioExceptionType.connectionError) {
      return NetworkException(
        'Erreur de connexion réseau',
        code: 'error.network',
      );
    }

    if (error.response != null) {
      return _createApiException(error);
    }

    return NetworkException(
      'Erreur réseau inconnue',
      code: 'error.api.unknown',
    );
  }

  /// Crée une exception API à partir d'une erreur Dio
  ApiException _createApiException(DioException error) {
    final statusCode = error.response!.statusCode;
    final errorData = error.response!.data;
    
    AppLogger.error(
      'Erreur API - Status: $statusCode',
      errorData,
    );
    
    final errorMessage = _extractErrorMessage(errorData);

    return ApiException(
      errorMessage,
      code: 'error.api.generic',
      statusCode: statusCode,
    );
  }

  /// Extrait le message d'erreur de la réponse
  String _extractErrorMessage(dynamic errorData) {
    if (errorData is Map<String, dynamic>) {
      return errorData['error']?.toString() ?? 
             errorData['message']?.toString() ?? 
             errorData['detail']?.toString() ??
             'Erreur API';
    }
    if (errorData is String) {
      return errorData;
    }
    return 'Erreur API';
  }
}
