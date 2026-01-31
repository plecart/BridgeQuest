import 'package:google_sign_in/google_sign_in.dart';
import '../../core/config/app_config.dart';
import '../../core/exceptions/app_exceptions.dart';
import '../../core/utils/logger.dart';

/// Service pour l'authentification Google Sign-In
class GoogleSignInService {
  final GoogleSignIn _googleSignIn;

  GoogleSignInService({GoogleSignIn? googleSignIn})
      : _googleSignIn = googleSignIn ??
            GoogleSignIn(
              scopes: ['email', 'profile'],
              // IMPORTANT: Pour Android, serverClientId doit être un Client ID Web
              // Le Client ID Android est utilisé automatiquement par le plugin
              serverClientId: AppConfig.googleSignInWebClientId,
            ) {
    AppLogger.debug(
      'Google Sign-In initialisé avec Client ID Web',
    );
  }

  /// Obtient le token ID Google
  /// 
  /// Retourne le token ID si la connexion réussit, null si l'utilisateur annule.
  /// 
  /// Throws [AuthException] si une erreur survient.
  Future<String?> getToken() async {
    try {
      final account = await _googleSignIn.signIn();
      if (account == null) {
        return null;
      }

      final authentication = await account.authentication;
      final idToken = authentication.idToken;

      if (idToken == null) {
        throw AuthException(
          'Token Google non disponible',
          code: 'error.google.tokenUnavailable',
        );
      }

      return idToken;
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException(
        'Erreur lors de la connexion Google',
        code: 'error.google.signIn',
      );
    }
  }
}
