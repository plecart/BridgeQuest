import 'package:sign_in_with_apple/sign_in_with_apple.dart';
import '../../core/exceptions/app_exceptions.dart';

/// Codes d'erreur Apple Sign-In (l10n via [ErrorTranslator]).
abstract final class AppleSignInErrorCodes {
  static const String tokenUnavailable = 'error.apple.tokenUnavailable';
  static const String signInCancelled = 'error.apple.signInCancelled';
  static const String signIn = 'error.apple.signIn';
}

/// Service pour l'authentification Apple Sign-In
class AppleSignInService {
  /// Obtient le token ID Apple
  ///
  /// Retourne le token ID si la connexion réussit.
  ///
  /// Throws [AuthException] si une erreur survient ou si l'utilisateur annule.
  /// Les messages passent par le code d'erreur (l10n dans la couche présentation).
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
          AppleSignInErrorCodes.tokenUnavailable,
          code: AppleSignInErrorCodes.tokenUnavailable,
        );
      }

      return identityToken;
    } catch (e) {
      if (e is AuthException) rethrow;
      if (e is SignInWithAppleAuthorizationException) {
        _handleAppleAuthorizationException(e);
      }
      _throwAppleError(AppleSignInErrorCodes.signIn);
    }
  }

  /// Mappe l'exception Apple vers une [AuthException] avec le bon code l10n.
  Never _handleAppleAuthorizationException(
    SignInWithAppleAuthorizationException e,
  ) {
    if (e.code == AuthorizationErrorCode.canceled) {
      _throwAppleError(AppleSignInErrorCodes.signInCancelled);
    }
    _throwAppleError(AppleSignInErrorCodes.signIn);
  }

  Never _throwAppleError(String code) {
    throw AuthException(code, code: code);
  }
}
