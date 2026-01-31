import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import '../../i18n/app_localizations.dart';

/// Configuration de la localisation de l'application
class AppLocalization {
  AppLocalization._();

  /// Construit la liste des délégations de localisation
  static List<LocalizationsDelegate> buildDelegates() {
    return const [
      AppLocalizations.delegate,
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ];
  }

  /// Construit la liste des locales supportées
  static List<Locale> buildSupportedLocales() {
    return const [
      Locale('fr', ''),
    ];
  }
}
