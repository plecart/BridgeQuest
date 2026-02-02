import 'dart:io';

import 'app_localizations_holder.dart';
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
    final envUrl = const String.fromEnvironment( // ignore: prefer_const_declarations
      'API_BASE_URL',
      defaultValue: '',
    );
    
    if (envUrl.isNotEmpty) {
      final l10n = AppLocalizationsHolder.current;
      AppLogger.debug(l10n?.logDebugApiUrlEnv(envUrl) ?? 'logDebugApiUrlEnv($envUrl)');
      return envUrl;
    }

    if (Platform.isAndroid) {
      const url = 'http://10.0.2.2:8000';
      final l10n = AppLocalizationsHolder.current;
      AppLogger.debug(l10n?.logDebugApiUrlAndroid(url) ?? 'logDebugApiUrlAndroid($url)');
      return url;
    }

    const url = 'http://localhost:8000';
    final l10n = AppLocalizationsHolder.current;
    AppLogger.debug(l10n?.logDebugApiUrlDefault(url) ?? 'logDebugApiUrlDefault($url)');
    return url;
  }

  /// Timeout pour les requêtes HTTP (en secondes)
  static const int timeoutSeconds = 30;

  /// Endpoints de l'API
  static const String authSSOLogin = '/api/auth/sso/login/';
  static const String authTokenRefresh = '/api/auth/token/refresh/';
  static const String authMe = '/api/auth/me/';
  static const String authLogout = '/api/auth/logout/';
}
