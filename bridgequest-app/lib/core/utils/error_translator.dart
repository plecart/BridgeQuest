import '../../i18n/app_localizations.dart';

/// Utilitaire pour traduire les codes d'erreur en messages localisés
///
/// Cette classe centralise la traduction des codes d'erreur pour éviter
/// la duplication de code dans les différentes pages.
class ErrorTranslator {
  ErrorTranslator._();

  /// Traduit un code d'erreur en message localisé
  ///
  /// [errorCode] : Le code d'erreur (ex: 'error.generic', 'error.network')
  /// [l10n] : Les localisations de l'application
  ///
  /// Retourne le message traduit ou le code si aucune traduction n'est trouvée.
  static String translate(String errorCode, AppLocalizations l10n) {
    switch (errorCode) {
      case 'error.generic':
        return l10n.errorGeneric;
      case 'error.network':
        return l10n.errorNetwork;
      case 'error.unexpected':
        return l10n.errorUnexpected;
      case 'error.auth.ssoFailed':
        return l10n.errorAuthSsoFailed;
      case 'error.auth.tokenInvalid':
        return l10n.errorAuthTokenInvalid;
      case 'error.auth.tokensMissing':
        return l10n.errorAuthTokensMissing;
      case 'error.auth.notAuthenticated':
      case 'errorAuthNotAuthenticated':
        return l10n.errorAuthNotAuthenticated;
      case 'lobbyErrorWebSocket':
        return l10n.lobbyErrorWebSocket;
      case 'lobbyStartGameError':
        return l10n.lobbyStartGameError;
      case 'error.response.invalidFormat':
        return l10n.errorResponseInvalidFormat;
      case 'error.response.unstructuredData':
        return l10n.errorResponseUnstructuredData;
      case 'error.response.userMissing':
        return l10n.errorResponseUserMissing;
      case 'error.response.userNotObject':
        return l10n.errorResponseUserNotObject;
      case 'error.google.signIn':
        return l10n.errorGoogleSignIn;
      case 'error.google.tokenUnavailable':
        return l10n.errorGoogleTokenUnavailable;
      case 'error.apple.signIn':
        return l10n.errorAppleSignIn;
      case 'error.apple.tokenUnavailable':
        return l10n.errorAppleTokenUnavailable;
      case 'error.apple.signInCancelled':
        return l10n.errorAppleSignInCancelled;
      case 'error.api.timeout':
        return l10n.errorApiTimeout;
      case 'error.api.unknown':
        return l10n.errorApiUnknown;
      case 'error.api.generic':
        return l10n.errorApiGeneric;
      case 'error.config.googleClientIdMissing':
        return l10n.errorConfigGoogleClientIdMissing;
      default:
        // Si le code n'est pas reconnu, retourner un message générique
        return errorCode.startsWith('error.') ? l10n.errorGeneric : errorCode;
    }
  }
}
