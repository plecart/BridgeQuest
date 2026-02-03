import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../i18n/app_localizations.dart';
import '../../../providers/auth_provider.dart';
import '../../../data/models/user.dart';
import '../../../core/utils/user_helpers.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/user_avatar.dart';

/// Page d'accueil affichant le profil de l'utilisateur
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.user;

    if (user == null) {
      // Ne devrait jamais arriver si la navigation conditionnelle fonctionne
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.homeTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => _handleLogout(context, authProvider),
            tooltip: l10n.homeLogoutButton,
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              UserAvatar(user: user, radius: 60),
              const SizedBox(height: 24),
              _buildUserName(user),
              const SizedBox(height: 8),
              _buildUserEmail(context, user),
            ],
          ),
        ),
      ),
    );
  }

  /// Construit le nom de l'utilisateur
  Widget _buildUserName(User user) {
    final displayName = UserHelpers.getDisplayName(user);
    return Text(
      displayName,
      style: AppTextStyles.homeTitle,
      textAlign: TextAlign.center,
    );
  }

  /// Construit l'email de l'utilisateur
  Widget _buildUserEmail(BuildContext context, User user) {
    return Text(
      user.email,
      style: AppTextStyles.homeEmail(context),
      textAlign: TextAlign.center,
    );
  }

  /// Gère la déconnexion
  Future<void> _handleLogout(
    BuildContext context,
    AuthProvider authProvider,
  ) async {
    try {
      await authProvider.logout();
    } catch (e) {
      // L'erreur est gérée par le provider
      // La navigation sera gérée par le widget de navigation conditionnelle
    }
  }
}
