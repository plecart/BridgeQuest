import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Service pour le stockage sécurisé des données sensibles
class SecureStorageService {
  final FlutterSecureStorage _storage;

  SecureStorageService()
      : _storage = const FlutterSecureStorage(
          aOptions: AndroidOptions(
            encryptedSharedPreferences: true,
          ),
          iOptions: IOSOptions(
            accessibility: KeychainAccessibility.first_unlock_this_device,
          ),
        );

  /// Sauvegarde le token de session
  Future<void> saveSessionToken(String token) async {
    await _storage.write(key: 'session_token', value: token);
  }

  /// Récupère le token de session
  Future<String?> getSessionToken() async {
    return await _storage.read(key: 'session_token');
  }

  /// Supprime le token de session
  Future<void> deleteSessionToken() async {
    await _storage.delete(key: 'session_token');
  }
}
