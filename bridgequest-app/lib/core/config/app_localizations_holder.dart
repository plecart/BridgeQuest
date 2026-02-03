import '../../i18n/app_localizations.dart';

/// Détient l'instance courante de [AppLocalizations] pour permettre
/// l'accès aux messages l10n en dehors de l'arbre des widgets (ex. logs).
///
/// Doit être initialisé depuis un widget ayant accès à [AppLocalizations.of]
/// (typiquement dans [AuthWrapper] ou à la racine de l'app).
abstract final class AppLocalizationsHolder {
  static AppLocalizations? _current;

  /// Instance courante des localisations (null avant le premier build).
  static AppLocalizations? get current => _current;

  /// Définit l'instance courante. Appelé depuis la couche présentation.
  static void setCurrent(AppLocalizations? l10n) {
    _current = l10n;
  }
}
