import 'dart:io';
import '../utils/logger.dart';

/// Configuration de l'API
class ApiConfig {
  ApiConfig._();

  /// URL de base de l'API backend
  ///
  /// Sur Android, utilise 10.0.2.2 au lieu de localhost pour accéder à la machine hôte.
  /// Cette adresse IP spéciale permet à l'émulateur Android d'accéder à localhost de la machine hôte.
  static String get baseUrl {
    // envUrl ne peut pas être const car String.fromEnvironment n'est pas évalué à la compilation
    const envUrl = String.fromEnvironment(
      // ignore: prefer_const_declarations
      'API_BASE_URL',
      defaultValue: '',
    );

    if (envUrl.isNotEmpty) {
      AppLogger.debug('API Base URL (env): $envUrl');
      return envUrl;
    }

    // Pour Android, utiliser 10.0.2.2 au lieu de localhost
    if (Platform.isAndroid) {
      const url = 'http://10.0.2.2:8000';
      AppLogger.debug('API Base URL (Android): $url');
      return url;
    }

    // Pour iOS/autres plateformes, utiliser localhost
    const url = 'http://localhost:8000';
    AppLogger.debug('API Base URL (default): $url');
    return url;
  }

  /// Timeout pour les requêtes HTTP (en secondes)
  static const int timeoutSeconds = 30;

  /// Endpoints de l'API
  static const String authSSOLogin = '/api/auth/sso/login/';
  static const String authTokenRefresh = '/api/auth/token/refresh/';
  static const String authMe = '/api/auth/me/';
  static const String authLogout = '/api/auth/logout/';

  /// Endpoints des parties
  static const String gamesCreate = '/api/games/';
  static const String gamesJoin = '/api/games/join/';

  /// Path pour détail, joueurs et paramètres d'une partie
  static String gameDetail(int id) => '/api/games/$id/';
  static String gamePlayers(int id) => '/api/games/$id/players/';
  static String gameStart(int id) => '/api/games/$id/start/';
  static String gameSettings(int id) => '/api/games/$id/settings/';

  // ---------------------------------------------------------------------------
  // WebSocket URLs
  // ---------------------------------------------------------------------------

  /// Construit l'URL WebSocket de base à partir de [baseUrl].
  ///
  /// Remplace le schéma HTTP par le schéma WS correspondant.
  static String get _wsBaseUrl {
    return baseUrl
        .replaceFirst('http://', 'ws://')
        .replaceFirst('https://', 'wss://');
  }

  /// URL WebSocket pour la salle d'attente (lobby).
  ///
  /// [gameId] : ID de la partie.
  /// [token] : Token JWT pour l'authentification (passé en query ?token=xxx).
  static String lobbyWebSocketUrl(int gameId, String token) {
    return '$_wsBaseUrl/ws/lobby/$gameId/?token=${Uri.encodeQueryComponent(token)}';
  }

  /// URL WebSocket pour la partie en cours (game).
  ///
  /// [gameId] : ID de la partie.
  /// [token] : Token JWT pour l'authentification (passé en query ?token=xxx).
  static String gameWebSocketUrl(int gameId, String token) {
    return '$_wsBaseUrl/ws/game/$gameId/?token=${Uri.encodeQueryComponent(token)}';
  }
}
