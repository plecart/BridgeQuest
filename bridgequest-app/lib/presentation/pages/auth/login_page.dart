import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../i18n/app_localizations.dart';
import '../../../providers/auth_provider.dart';
import '../../widgets/loading_button.dart';
import '../../widgets/error_message.dart';
import '../../../data/services/google_sign_in_service.dart';
import '../../../data/services/apple_sign_in_service.dart';
import 'login_view_model.dart';

/// Page de connexion SSO
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  late final LoginViewModel _viewModel;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!mounted) return;
    // Initialise le ViewModel une seule fois avec les dépendances
    if (!_isViewModelInitialized) {
      final authProvider = context.read<AuthProvider>();
      _viewModel = LoginViewModel(
        authProvider: authProvider,
        googleSignInService: GoogleSignInService(),
        appleSignInService: AppleSignInService(),
      );
      _isViewModelInitialized = true;
    }
  }

  bool _isViewModelInitialized = false;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildHeader(context, l10n),
              const SizedBox(height: 48),
              _buildLoginButtons(context, l10n, authProvider),
              if (authProvider.isLoading) _buildLoadingIndicator(),
              if (authProvider.errorMessage != null)
                ErrorMessage(message: _translateErrorCode(authProvider.errorMessage!, l10n)),
            ],
          ),
        ),
      ),
    );
  }

  /// Construit l'en-tête de la page
  Widget _buildHeader(BuildContext context, AppLocalizations l10n) {
    return Column(
      children: [
        Text(
          l10n.authLoginTitle,
          style: Theme.of(context).textTheme.headlineLarge,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        Text(
          l10n.authLoginSubtitle,
          style: Theme.of(context).textTheme.bodyLarge,
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  /// Construit les boutons de connexion
  Widget _buildLoginButtons(
    BuildContext context,
    AppLocalizations l10n,
    AuthProvider authProvider,
  ) {
    return Column(
      children: [
        LoadingButton(
          label: l10n.authLoginButtonGoogle,
          icon: Icons.login,
          isLoading: authProvider.isLoading,
          onPressed: () => _viewModel.loginWithGoogle(),
        ),
        if (Theme.of(context).platform == TargetPlatform.iOS) ...[
          const SizedBox(height: 16),
          LoadingButton(
            label: l10n.authLoginButtonApple,
            icon: Icons.apple,
            isLoading: authProvider.isLoading,
            onPressed: () => _viewModel.loginWithApple(),
          ),
        ],
      ],
    );
  }

  /// Construit l'indicateur de chargement
  Widget _buildLoadingIndicator() {
    return const Padding(
      padding: EdgeInsets.only(top: 24),
      child: CircularProgressIndicator(),
    );
  }

  /// Traduit un code d'erreur en message localisé
  /// 
  /// [errorCode] : Le code d'erreur (ex: 'error.generic', 'error.network')
  /// [l10n] : Les localisations de l'application
  /// 
  /// Retourne le message traduit ou le code si aucune traduction n'est trouvée.
  String _translateErrorCode(String errorCode, AppLocalizations l10n) {
    // Mapper les codes d'erreur aux clés de traduction ARB (camelCase)
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
