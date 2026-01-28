import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import '../../../providers/auth_provider.dart';
import '../../widgets/loading_button.dart';
import '../../widgets/error_message.dart';
import '../../../data/services/google_sign_in_service.dart';
import '../../../data/services/apple_sign_in_service.dart';
import 'login_view_model.dart';

/// Page de connexion SSO
class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final authProvider = context.watch<AuthProvider>();
    final viewModel = _createViewModel(authProvider);

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
              _buildLoginButtons(context, l10n, viewModel, authProvider),
              if (authProvider.isLoading) _buildLoadingIndicator(),
              if (authProvider.errorMessage != null)
                ErrorMessage(message: authProvider.errorMessage!),
            ],
          ),
        ),
      ),
    );
  }

  /// Crée le ViewModel avec les services injectés
  LoginViewModel _createViewModel(AuthProvider authProvider) {
    return LoginViewModel(
      authProvider: authProvider,
      googleSignInService: GoogleSignInService(),
      appleSignInService: AppleSignInService(),
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
    LoginViewModel viewModel,
    AuthProvider authProvider,
  ) {
    return Column(
      children: [
        LoadingButton(
          label: l10n.authLoginButtonGoogle,
          icon: Icons.login,
          isLoading: authProvider.isLoading,
          onPressed: () => viewModel.loginWithGoogle(),
        ),
        if (Theme.of(context).platform == TargetPlatform.iOS) ...[
          const SizedBox(height: 16),
          LoadingButton(
            label: l10n.authLoginButtonApple,
            icon: Icons.apple,
            isLoading: authProvider.isLoading,
            onPressed: () => viewModel.loginWithApple(),
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
