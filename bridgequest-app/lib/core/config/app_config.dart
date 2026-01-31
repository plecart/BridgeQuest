import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../exceptions/app_exceptions.dart';

/// Configuration de l'application
class AppConfig {
  AppConfig._();

  /// Nom de l'application
  static const String appName = 'Bridge Quest';

  /// Version de l'application
  static const String appVersion = '1.0.0+1';

  /// Environnement de l'application
  static const String environment = String.fromEnvironment(
    'ENV',
    defaultValue: 'development',
  );

  /// Mode debug
  static const bool isDebug = bool.fromEnvironment('dart.vm.product') == false;

  /// Client ID Web Google Sign-In (pour obtenir l'idToken côté serveur)
  /// 
  /// IMPORTANT: Pour Android, il faut utiliser un Client ID Web comme serverClientId.
  /// Le Client ID Android est utilisé automatiquement par le plugin Google Sign-In.
  /// 
  /// Throws [ConfigurationException] si la variable d'environnement n'est pas définie.
  static String get googleSignInWebClientId {
    final clientId = dotenv.env['GOOGLE_SIGN_IN_WEB_CLIENT_ID'];
    if (clientId == null || clientId.isEmpty) {
      throw ConfigurationException(
        'GOOGLE_SIGN_IN_WEB_CLIENT_ID environment variable is not defined',
        code: 'error.config.googleClientIdMissing',
      );
    }
    return clientId;
  }
}
