import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/exceptions/app_exceptions.dart';
import '../../../data/models/game/game.dart';
import '../../../data/models/user.dart';
import '../../../data/repositories/game_repository.dart';
import '../../../i18n/app_localizations.dart';
import '../../../providers/auth_provider.dart';
import '../../../core/utils/user_helpers.dart';
import '../../pages/lobby/lobby_page.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/game_code_input_dialog.dart';
import '../../widgets/user_avatar.dart';

/// Page d'accueil affichant le profil de l'utilisateur et les actions
/// Créer / Rejoindre une partie.
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.user;

    if (user == null) {
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
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              UserAvatar(user: user, radius: 60),
              const SizedBox(height: 24),
              _buildUserName(user),
              const SizedBox(height: 8),
              _buildUserEmail(context, user),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: () => _createGameAndNavigate(context),
                icon: const Icon(Icons.add),
                label: Text(l10n.homeCreateGameButton),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () => _showJoinGameDialog(context),
                icon: const Icon(Icons.login),
                label: Text(l10n.homeJoinGameButton),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _createGameAndNavigate(BuildContext context) async {
    final l10n = AppLocalizations.of(context)!;
    try {
      final game = await context.read<GameRepository>().createGame();
      if (!context.mounted) return;
      _navigateToLobby(context, game);
    } on AppException catch (e) {
      if (!context.mounted) return;
      _showErrorSnackBar(context, e.serverMessage ?? l10n.errorGeneric);
    } catch (_) {
      if (!context.mounted) return;
      _showErrorSnackBar(context, l10n.errorGeneric);
    }
  }

  void _showErrorSnackBar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Theme.of(context).colorScheme.error,
      ),
    );
  }

  Future<void> _showJoinGameDialog(BuildContext context) async {
    final l10n = AppLocalizations.of(context)!;
    final game = await GameCodeInputDialog.show<Game>(
      context: context,
      title: l10n.homeJoinGameButton,
      label: l10n.homeGameCodeLabel,
      submitLabel: l10n.homeJoinGameSubmit,
      submit: (value) => context.read<GameRepository>().joinGame(code: value),
      validate: (value) => value.isEmpty ? l10n.errorGameInvalidCode : null,
      transformInput: (v) => v.toUpperCase(),
      textCapitalization: TextCapitalization.characters,
    );
    if (context.mounted && game != null) {
      _navigateToLobby(context, game);
    }
  }

  void _navigateToLobby(BuildContext context, Game game) {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => LobbyPage(game: game)),
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

  /// Gère la déconnexion.
  Future<void> _handleLogout(
    BuildContext context,
    AuthProvider authProvider,
  ) async {
    try {
      await authProvider.logout();
    } catch (_) {
      // Erreur gérée par le provider ; navigation conditionnelle gère la sortie.
    }
  }
}
