// ignore_for_file: avoid_print
// Utilisation de print acceptée dans ce fichier car AppLogger est un logger de debug
// qui doit fonctionner sans dépendances externes de logging.

import '../config/app_config.dart';

/// Logger simple pour l'application
/// 
/// Utilise print en mode debug, silencieux en production.
/// 
/// Note: L'utilisation de `print` est acceptée ici car ce logger doit fonctionner
/// sans dépendances externes et est uniquement utilisé en mode debug.
class AppLogger {
  AppLogger._();

  /// Log un message de debug (uniquement en mode debug)
  static void debug(String message) {
    if (AppConfig.isDebug) {
      print('[DEBUG] $message');
    }
  }

  /// Log un message d'information
  static void info(String message) {
    if (AppConfig.isDebug) {
      print('[INFO] $message');
    }
  }

  /// Log un message d'erreur
  /// 
  /// Les erreurs sont toujours loggées, même en production.
  static void error(String message, [Object? error, StackTrace? stackTrace]) {
    print('[ERROR] $message');
    if (error != null) {
      print('[ERROR] Exception: $error');
    }
    if (stackTrace != null) {
      print('[ERROR] StackTrace: $stackTrace');
    }
  }

  /// Log un message d'avertissement
  static void warning(String message) {
    if (AppConfig.isDebug) {
      print('[WARNING] $message');
    }
  }
}
