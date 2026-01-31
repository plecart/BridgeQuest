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

  bool _isLoggingIn = false;

  /// Connexion via Google Sign-In
  /// 
  /// Retourne null si l'utilisateur annule la connexion.
  /// Throws [AuthException] si une erreur survient.
  Future<void> loginWithGoogle() async {
    await _loginWithSSO(
      provider: 'google',
      getToken: () => _googleSignInService.getToken(),
    );
  }

  /// Connexion via Apple Sign-In
  /// 
  /// Throws [AuthException] si une erreur survient.
  Future<void> loginWithApple() async {
    await _loginWithSSO(
      provider: 'apple',
      getToken: () => _appleSignInService.getToken(),
    );
  }

  /// Logique commune de connexion SSO
  /// 
  /// [provider] : Le fournisseur SSO ('google' ou 'apple')
  /// [getToken] : Fonction pour obtenir le token du fournisseur
  Future<void> _loginWithSSO({
    required String provider,
    required Future<String?> Function() getToken,
  }) async {
    if (_isLoggingIn) {
      return;
    }

    _isLoggingIn = true;
    try {
      final token = await getToken();
      if (token == null) {
        return;
      }

      await _authProvider.loginWithSSO(
        provider: provider,
        token: token,
      );
    } finally {
      _isLoggingIn = false;
    }
  }
}
