import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'i18n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[];

  /// Nom de l'application
  ///
  /// In fr, this message translates to:
  /// **'Bridge Quest'**
  String get appName;

  /// Titre de la page de connexion
  ///
  /// In fr, this message translates to:
  /// **'Connexion'**
  String get authLoginTitle;

  /// Sous-titre de la page de connexion
  ///
  /// In fr, this message translates to:
  /// **'Connectez-vous pour commencer'**
  String get authLoginSubtitle;

  /// Bouton de connexion Google
  ///
  /// In fr, this message translates to:
  /// **'Se connecter avec Google'**
  String get authLoginButtonGoogle;

  /// Bouton de connexion Apple
  ///
  /// In fr, this message translates to:
  /// **'Se connecter avec Apple'**
  String get authLoginButtonApple;

  /// Message d'erreur pour l'échec de l'authentification SSO
  ///
  /// In fr, this message translates to:
  /// **'Échec de l\'authentification SSO'**
  String get errorAuthSsoFailed;

  /// Message d'erreur pour un token invalide
  ///
  /// In fr, this message translates to:
  /// **'Token d\'authentification invalide'**
  String get errorAuthTokenInvalid;

  /// Message d'erreur générique
  ///
  /// In fr, this message translates to:
  /// **'Une erreur est survenue'**
  String get errorGeneric;

  /// Message d'erreur réseau
  ///
  /// In fr, this message translates to:
  /// **'Erreur de connexion réseau'**
  String get errorNetwork;

  /// Message d'erreur inattendue
  ///
  /// In fr, this message translates to:
  /// **'Erreur inattendue'**
  String get errorUnexpected;

  /// Message d'erreur pour un format de réponse invalide
  ///
  /// In fr, this message translates to:
  /// **'Format de réponse invalide'**
  String get errorResponseInvalidFormat;

  /// Message d'erreur pour des données non structurées
  ///
  /// In fr, this message translates to:
  /// **'Format de réponse invalide: données non structurées'**
  String get errorResponseUnstructuredData;

  /// Message d'erreur pour un utilisateur manquant dans la réponse
  ///
  /// In fr, this message translates to:
  /// **'Format de réponse invalide: utilisateur manquant'**
  String get errorResponseUserMissing;

  /// Message d'erreur pour un utilisateur qui n'est pas un objet
  ///
  /// In fr, this message translates to:
  /// **'Format de réponse invalide: utilisateur n\'est pas un objet'**
  String get errorResponseUserNotObject;

  /// Message d'erreur pour la connexion Google
  ///
  /// In fr, this message translates to:
  /// **'Erreur lors de la connexion Google'**
  String get errorGoogleSignIn;

  /// Message d'erreur pour la connexion Apple
  ///
  /// In fr, this message translates to:
  /// **'Erreur lors de la connexion Apple'**
  String get errorAppleSignIn;

  /// Message d'erreur pour un timeout de connexion
  ///
  /// In fr, this message translates to:
  /// **'Timeout de connexion'**
  String get errorApiTimeout;

  /// Message d'erreur pour une erreur réseau inconnue
  ///
  /// In fr, this message translates to:
  /// **'Erreur réseau inconnue'**
  String get errorApiUnknown;

  /// Message d'erreur API générique
  ///
  /// In fr, this message translates to:
  /// **'Erreur API'**
  String get errorApiGeneric;

  /// Message d'erreur quand le token Google n'est pas disponible
  ///
  /// In fr, this message translates to:
  /// **'Token Google non disponible'**
  String get errorGoogleTokenUnavailable;

  /// Message d'erreur quand le token Apple n'est pas disponible
  ///
  /// In fr, this message translates to:
  /// **'Token Apple non disponible'**
  String get errorAppleTokenUnavailable;

  /// Message d'erreur quand l'utilisateur annule la connexion Apple
  ///
  /// In fr, this message translates to:
  /// **'Connexion Apple annulée'**
  String get errorAppleSignInCancelled;

  /// Message d'erreur quand le Client ID Google n'est pas configuré
  ///
  /// In fr, this message translates to:
  /// **'Configuration Google manquante'**
  String get errorConfigGoogleClientIdMissing;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>[].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
