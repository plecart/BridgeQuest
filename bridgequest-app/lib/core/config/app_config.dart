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
}
