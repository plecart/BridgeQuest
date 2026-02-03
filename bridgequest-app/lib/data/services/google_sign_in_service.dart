import 'package:google_sign_in/google_sign_in.dart';
import '../../core/config/app_config.dart';
import '../../core/exceptions/app_exceptions.dart';

/// Codes d'erreur Google Sign-In (l10n via [ErrorTranslator]).
abstract final class GoogleSignInErrorCodes {
  static const String tokenUnavailable = 'error.google.tokenUnavailable';
  static const String signIn = 'error.google.signIn';
}

/// Service pour l'authentification Google Sign-In
///
/// L'initialisation de GoogleSignIn est lazy pour éviter de bloquer le thread principal
/// au démarrage de l'application.
class GoogleSignInService {
  GoogleSignIn? _googleSignIn;

  GoogleSignInService({GoogleSignIn? googleSignIn}) : _googleSignIn = googleSignIn;

  /// Retourne l'instance GoogleSignIn, en la créant si nécessaire
  ///
  /// L'initialisation est lazy pour améliorer les performances au démarrage.
  GoogleSignIn get _googleSignInInstance {
    _googleSignIn ??= GoogleSignIn(
      scopes: ['email', 'profile'],
      serverClientId: AppConfig.googleSignInWebClientId,
    );
    return _googleSignIn!;
  }

  /// Obtient le token ID Google
  ///
  /// Retourne le token ID si la connexion réussit, null si l'utilisateur annule.
  ///
  /// Throws [AuthException] si une erreur survient.
  /// Les messages passent par le code d'erreur (l10n dans la couche présentation).
  Future<String?> getToken() async {
    try {
      final account = await _googleSignInInstance.signIn();
      if (account == null) return null;

      final authentication = await account.authentication;
      final idToken = authentication.idToken;

      if (idToken == null) {
        throw AuthException(
          GoogleSignInErrorCodes.tokenUnavailable,
          code: GoogleSignInErrorCodes.tokenUnavailable,
        );
      }

      return idToken;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException(
        GoogleSignInErrorCodes.signIn,
        code: GoogleSignInErrorCodes.signIn,
      );
    }
  }
}
