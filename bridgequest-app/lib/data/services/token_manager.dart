import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Gestionnaire des tokens JWT pour l'authentification OAuth2
/// 
/// Ce gestionnaire stocke et récupère les tokens d'accès et de rafraîchissement
/// de manière sécurisée en utilisant flutter_secure_storage.
/// 
/// Les tokens sont stockés dans le Keychain (iOS) ou Keystore (Android),
/// offrant une sécurité maximale pour les données sensibles.
/// 
/// Le token d'accès est mis en cache en mémoire pour éviter les accès répétés
/// au stockage sécurisé, améliorant les performances.
class TokenManager {
  static const String _accessTokenKey = 'jwt_access_token';
  static const String _refreshTokenKey = 'jwt_refresh_token';
  
  final FlutterSecureStorage _storage;
  
  // Cache en mémoire pour éviter les accès répétés au stockage sécurisé
  String? _cachedAccessToken;
  bool _cacheInitialized = false;

  TokenManager({
    FlutterSecureStorage? storage,
  }) : _storage = storage ?? const FlutterSecureStorage(
          aOptions: AndroidOptions(
            encryptedSharedPreferences: true,
          ),
          iOptions: IOSOptions(
            accessibility: KeychainAccessibility.first_unlock_this_device,
          ),
        );

  /// Retourne le token d'accès actuel
  /// 
  /// Utilise un cache en mémoire pour éviter les accès répétés au stockage sécurisé.
  /// Retourne null si aucun token n'est stocké.
  Future<String?> getAccessToken() async {
    // Retourner le cache si déjà initialisé (même si null)
    if (_cacheInitialized) {
      return _cachedAccessToken;
    }
    
    // Charger depuis le stockage sécurisé une seule fois
    _cachedAccessToken = await _storage.read(key: _accessTokenKey);
    _cacheInitialized = true;
    return _cachedAccessToken;
  }

  /// Retourne le token de rafraîchissement actuel
  /// 
  /// Retourne null si aucun token n'est stocké.
  Future<String?> getRefreshToken() async {
    return await _storage.read(key: _refreshTokenKey);
  }

  /// Sauvegarde les tokens d'accès et de rafraîchissement
  /// 
  /// [accessToken] : Le token d'accès JWT
  /// [refreshToken] : Le token de rafraîchissement JWT
  /// 
  /// Le cache est mis à jour immédiatement pour améliorer les performances,
  /// puis les tokens sont sauvegardés de manière asynchrone dans le stockage sécurisé.
  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    _updateCache(accessToken);
    await _persistTokens(accessToken, refreshToken);
  }

  /// Met à jour le cache en mémoire avec le nouveau token
  void _updateCache(String accessToken) {
    _cachedAccessToken = accessToken;
    _cacheInitialized = true;
  }

  /// Sauvegarde les tokens dans le stockage sécurisé
  Future<void> _persistTokens(String accessToken, String refreshToken) async {
    await Future.wait([
      _storage.write(key: _accessTokenKey, value: accessToken),
      _storage.write(key: _refreshTokenKey, value: refreshToken),
    ]);
  }

  /// Met à jour uniquement le token d'accès
  /// 
  /// Utilisé lors du refresh token lorsque seul le access_token change.
  /// Le cache est mis à jour immédiatement pour améliorer les performances.
  Future<void> updateAccessToken(String accessToken) async {
    _updateCache(accessToken);
    await _storage.write(key: _accessTokenKey, value: accessToken);
  }

  /// Supprime tous les tokens stockés
  /// 
  /// Utilisé lors de la déconnexion pour nettoyer les tokens.
  /// Le cache est vidé immédiatement, puis les tokens sont supprimés du stockage.
  Future<void> clearTokens() async {
    _clearCache();
    await _deleteTokensFromStorage();
  }

  /// Vide le cache en mémoire
  /// 
  /// Utilisé lors de la déconnexion pour marquer le cache comme vide.
  void _clearCache() {
    _cachedAccessToken = null;
    _cacheInitialized = true;
  }

  /// Supprime les tokens du stockage sécurisé
  /// 
  /// Supprime les deux tokens (access et refresh) de manière parallèle.
  Future<void> _deleteTokensFromStorage() async {
    await Future.wait([
      _storage.delete(key: _accessTokenKey),
      _storage.delete(key: _refreshTokenKey),
    ]);
  }
  
  /// Invalide le cache en mémoire
  /// 
  /// Force le rechargement depuis le stockage sécurisé lors du prochain appel.
  /// Diffère de [_clearCache] car elle marque le cache comme non initialisé,
  /// permettant un rechargement depuis le stockage.
  void invalidateCache() {
    _cacheInitialized = false;
    _cachedAccessToken = null;
  }

  /// Vérifie si un token d'accès est disponible
  /// 
  /// Retourne true si un token d'accès est stocké, false sinon.
  Future<bool> hasAccessToken() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }
}
