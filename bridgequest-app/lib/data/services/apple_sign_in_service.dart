import 'package:sign_in_with_apple/sign_in_with_apple.dart';
import '../../core/exceptions/app_exceptions.dart';

/// Service pour l'authentification Apple Sign-In
class AppleSignInService {
  /// Obtient le token ID Apple
  /// 
  /// Retourne le token ID si la connexion réussit.
  /// 
  /// Throws [AuthException] si une erreur survient ou si l'utilisateur annule.
  Future<String> getToken() async {
    try {
      final credential = await SignInWithApple.getAppleIDCredential(
        scopes: [
          AppleIDAuthorizationScopes.email,
          AppleIDAuthorizationScopes.fullName,
        ],
      );

      final identityToken = credential.identityToken;

      if (identityToken == null) {
        throw AuthException(
          'Apple token unavailable',
          code: 'error.apple.tokenUnavailable',
        );
      }

      return identityToken;
    } catch (e) {
      if (e is AuthException) rethrow;
      if (e is SignInWithAppleAuthorizationException) {
        throw AuthException(
          'Apple Sign-In cancelled by user',
          code: 'error.apple.signInCancelled',
        );
      }
      throw AuthException(
        'Apple Sign-In error',
        code: 'error.apple.signIn',
      );
    }
  }
}
