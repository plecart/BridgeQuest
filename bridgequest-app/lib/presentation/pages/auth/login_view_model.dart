import '../../../data/services/google_sign_in_service.dart';
import '../../../data/services/apple_sign_in_service.dart';
import '../../../providers/auth_provider.dart';

/// ViewModel pour la page de connexion
class LoginViewModel {
  final AuthProvider _authProvider;
  final GoogleSignInService _googleSignInService;
  final AppleSignInService _appleSignInService;

  LoginViewModel({
    required AuthProvider authProvider,
    GoogleSignInService? googleSignInService,
    AppleSignInService? appleSignInService,
  })  : _authProvider = authProvider,
        _googleSignInService = googleSignInService ?? GoogleSignInService(),
        _appleSignInService = appleSignInService ?? AppleSignInService();

  /// Connexion via Google Sign-In
  Future<void> loginWithGoogle() async {
    try {
      final token = await _googleSignInService.getToken();
      if (token == null) {
        // L'utilisateur a annulé la connexion
        return;
      }

      await _authProvider.loginWithSSO(
        provider: 'google',
        token: token,
      );
    } catch (e) {
      // L'erreur est gérée par le AuthProvider
      rethrow;
    }
  }

  /// Connexion via Apple Sign-In
  Future<void> loginWithApple() async {
    try {
      final token = await _appleSignInService.getToken();

      await _authProvider.loginWithSSO(
        provider: 'apple',
        token: token,
      );
    } catch (e) {
      // L'erreur est gérée par le AuthProvider
      rethrow;
    }
  }
}
