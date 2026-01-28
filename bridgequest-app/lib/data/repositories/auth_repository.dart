import '../services/api_service.dart';
import '../services/secure_storage_service.dart';
import '../models/user.dart';
import '../../core/config/api_config.dart';
import '../../core/exceptions/app_exceptions.dart';

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
  Future<User> loginWithSSO({
    required String provider,
    required String token,
  }) async {
    try {
      final response = await _apiService.post(
        ApiConfig.authSSOLogin,
        data: {
          'provider': provider,
          'token': token,
        },
      );

      final user = _parseUserFromResponse(response.data);
      await _saveSessionToken(response.data);

      return user;
    } on ApiException catch (e) {
      throw AuthException(e.message);
    } catch (e) {
      if (e is AppException) rethrow;
      throw AuthException('Erreur inattendue: ${e.toString()}');
    }
  }

  /// Récupère l'utilisateur actuel
  Future<User> getCurrentUser() async {
    try {
      final response = await _apiService.get(ApiConfig.authMe);
      return User.fromJson(response.data as Map<String, dynamic>);
    } on ApiException catch (e) {
      throw AuthException(e.message);
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

  /// Parse l'utilisateur depuis la réponse API
  User _parseUserFromResponse(Map<String, dynamic> data) {
    return User.fromJson(data['user'] as Map<String, dynamic>);
  }

  /// Sauvegarde le token de session
  Future<void> _saveSessionToken(Map<String, dynamic> data) async {
    final sessionToken = data['session_token'] as String;
    await _storageService.saveSessionToken(sessionToken);
  }
}
