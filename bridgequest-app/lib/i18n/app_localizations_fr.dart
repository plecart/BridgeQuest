// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for French (`fr`).
class AppLocalizationsFr extends AppLocalizations {
  AppLocalizationsFr([String locale = 'fr']) : super(locale);

  @override
  String get appName => 'Bridge Quest';

  @override
  String get authLoginTitle => 'Connexion';

  @override
  String get authLoginSubtitle => 'Connectez-vous pour commencer';

  @override
  String get authLoginButtonGoogle => 'Se connecter avec Google';

  @override
  String get authLoginButtonApple => 'Se connecter avec Apple';

  @override
  String get errorAuthSsoFailed => 'Échec de l\'authentification SSO';

  @override
  String get errorAuthTokenInvalid => 'Token d\'authentification invalide';

  @override
  String get errorGeneric => 'Une erreur est survenue';

  @override
  String get errorNetwork => 'Erreur de connexion réseau';

  @override
  String get errorUnexpected => 'Erreur inattendue';

  @override
  String get errorResponseInvalidFormat => 'Format de réponse invalide';

  @override
  String get errorResponseUnstructuredData =>
      'Format de réponse invalide: données non structurées';

  @override
  String get errorResponseUserMissing =>
      'Format de réponse invalide: utilisateur manquant';

  @override
  String get errorResponseUserNotObject =>
      'Format de réponse invalide: utilisateur n\'est pas un objet';

  @override
  String get errorGoogleSignIn => 'Erreur lors de la connexion Google';

  @override
  String get errorAppleSignIn => 'Erreur lors de la connexion Apple';

  @override
  String get errorApiTimeout => 'Timeout de connexion';

  @override
  String get errorApiUnknown => 'Erreur réseau inconnue';

  @override
  String get errorApiGeneric => 'Erreur API';

  @override
  String get errorGoogleTokenUnavailable => 'Token Google non disponible';

  @override
  String get errorAppleTokenUnavailable => 'Token Apple non disponible';

  @override
  String get errorAppleSignInCancelled => 'Connexion Apple annulée';

  @override
  String get errorConfigGoogleClientIdMissing =>
      'Configuration Google manquante';

  @override
  String get homeTitle => 'Accueil';

  @override
  String get homeLogoutButton => 'Déconnexion';
}
