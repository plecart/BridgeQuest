import '../services/api_service.dart';
import '../services/secure_storage_service.dart';
import '../models/user.dart';
import '../../core/config/api_config.dart';
import '../../core/exceptions/app_exceptions.dart';
import '../../core/utils/logger.dart';

/// Repository pour l'authentification
class AuthRepository {
  final ApiService _apiService;
  final SecureStorageService _storageService;

  AuthRepository({
    required ApiService apiService,
    required SecureStorageService storageService,
  })  : _apiService = apiService,
        _storageService = storageService;

  /// Authentifie un utilisateur via SSO
  /// 
  /// [provider] : Le fournisseur SSO ('google' ou 'apple')
  /// [token] : Le token ID obtenu du fournisseur SSO
  /// 
  /// Retourne l'utilisateur authentifié.
  /// 
  /// Throws [AuthException] si l'authentification échoue.
  Future<User> loginWithSSO({
    required String provider,
    required String token,
  }) async {
    try {
      AppLogger.debug('Tentative de connexion SSO avec provider: $provider');
      
      final response = await _apiService.post(
        ApiConfig.authSSOLogin,
        data: {
          'provider': provider,
          'token': token,
        },
      );

      final responseData = _normalizeResponseData(response.data);
      final user = _parseUserFromResponse(responseData);
      await _saveSessionTokenIfPresent(responseData);

      AppLogger.debug('Utilisateur authentifié: ${user.email}');
      return user;
    } on ApiException catch (e) {
      AppLogger.error('Erreur API lors de la connexion SSO', e);
      throw AuthException(e.message, code: e.code ?? 'error.generic');
    } catch (e) {
      if (e is AppException) rethrow;
      AppLogger.error('Erreur inattendue lors de la connexion SSO', e);
      throw AuthException('Erreur inattendue', code: 'error.unexpected');
    }
  }

  /// Récupère l'utilisateur actuel
  /// 
  /// Throws [AuthException] si l'utilisateur n'est pas authentifié ou si une erreur survient.
  Future<User> getCurrentUser() async {
    try {
      final response = await _apiService.get(ApiConfig.authMe);
      final responseData = _normalizeResponseData(response.data);
      return User.fromJson(responseData);
    } on ApiException catch (e) {
      AppLogger.error('Erreur API lors de la récupération de l\'utilisateur', e);
      throw AuthException(e.message, code: e.code ?? 'error.generic');
    } catch (e) {
      if (e is AppException) rethrow;
      AppLogger.error('Erreur inattendue lors de la récupération de l\'utilisateur', e);
      throw AuthException('Erreur inattendue', code: 'error.unexpected');
    }
  }

  /// Déconnecte l'utilisateur
  /// 
  /// Supprime le token même si l'appel API échoue.
  Future<void> logout() async {
    try {
      await _apiService.post(ApiConfig.authLogout);
    } catch (e) {
      // Ignorer les erreurs lors de la déconnexion
      // Le token sera supprimé dans tous les cas
    } finally {
      await _storageService.deleteSessionToken();
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
    throw AuthException(
      'Format de réponse invalide: données non structurées',
      code: 'error.response.unstructuredData',
    );
  }

  /// Parse l'utilisateur depuis la réponse API
  /// 
  /// Throws [AuthException] si le format de réponse est invalide.
  User _parseUserFromResponse(Map<String, dynamic> data) {
    final userData = data['user'];
    
    if (userData == null) {
      throw AuthException(
        'Format de réponse invalide: utilisateur manquant',
        code: 'error.response.userMissing',
      );
    }
    
    if (userData is! Map<String, dynamic>) {
      throw AuthException(
        'Format de réponse invalide: utilisateur n\'est pas un objet',
        code: 'error.response.userNotObject',
      );
    }
    
    try {
      return User.fromJson(userData);
    } catch (e) {
      AppLogger.error('Erreur lors du parsing de l\'utilisateur', e);
      throw AuthException(
        'Format de réponse invalide',
        code: 'error.response.invalidFormat',
      );
    }
  }

  /// Sauvegarde le token de session depuis la réponse API (si présent)
  /// 
  /// Note: Le serveur Django utilise les sessions avec cookies par défaut.
  /// Les cookies sont gérés automatiquement par Dio pour les requêtes suivantes.
  Future<void> _saveSessionTokenIfPresent(Map<String, dynamic> data) async {
    final sessionToken = data['session_token'];
    if (sessionToken != null && sessionToken is String) {
      await _storageService.saveSessionToken(sessionToken);
      AppLogger.debug('Token de session sauvegardé');
    }
  }
}
