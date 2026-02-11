import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../i18n/app_localizations.dart';
import '../../../providers/auth_provider.dart';
import '../../../core/utils/error_translator.dart';
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
                ErrorMessage(
                  message: ErrorTranslator.translate(
                      authProvider.errorMessage!, l10n,),
                ),
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
}
