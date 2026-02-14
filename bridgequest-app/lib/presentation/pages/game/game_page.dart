import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../data/models/game/game_player_role.dart';
import '../../../data/services/game_websocket_service.dart';
import '../../../i18n/app_localizations.dart';
import '../../widgets/error_state_view.dart';
import '../menu/home_page.dart';
import 'game_view_model.dart';

/// Page principale de jeu affichée pendant la phase IN_PROGRESS.
///
/// Affiche le compte à rebours, le rôle du joueur, la liste des joueurs
/// et leurs rôles. Navigue vers ResultsPage quand `game_finished` est reçu.
class GamePage extends StatefulWidget {
  const GamePage({
    super.key,
    required this.gameId,
    required this.gameEndsAt,
    required this.roles,
    required this.currentPlayerId,
  });

  final int gameId;
  final String gameEndsAt;
  final List<GamePlayerRole> roles;
  final int currentPlayerId;

  @override
  State<GamePage> createState() => _GamePageState();
}

class _GamePageState extends State<GamePage> {
  late final GameViewModel _viewModel;

  @override
  void initState() {
    super.initState();
    _viewModel = GameViewModel(
      gameId: widget.gameId,
      gameEndsAt: widget.gameEndsAt,
      roles: widget.roles,
      currentPlayerId: widget.currentPlayerId,
      gameWebSocketService: context.read<GameWebSocketService>(),
    );
    _viewModel.initialize();
  }

  @override
  void dispose() {
    _viewModel.disposeResources();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<GameViewModel>.value(
      value: _viewModel,
      child: _GameContent(
        onNavigateToMenu: _navigateToMenu,
        onNavigateToResults: _navigateToResults,
      ),
    );
  }

  void _navigateToMenu() {
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const HomePage()),
      (route) => false,
    );
  }

  void _navigateToResults(GameNavigateToResults result) {
    if (!mounted) return;
    // TODO(Sprint 3 - Task N): Naviguer vers ResultsPage
    // Pour l'instant, revenir au menu.
    _navigateToMenu();
  }
}

// ---------------------------------------------------------------------------
// Contenu de la page (séparé pour accéder au ViewModel via Consumer)
// ---------------------------------------------------------------------------

class _GameContent extends StatelessWidget {
  const _GameContent({
    required this.onNavigateToMenu,
    required this.onNavigateToResults,
  });

  final VoidCallback onNavigateToMenu;
  final void Function(GameNavigateToResults) onNavigateToResults;

  @override
  Widget build(BuildContext context) {
    return Consumer<GameViewModel>(
      builder: (context, vm, _) {
        _scheduleNavigationIfNeeded(context, vm);
        return PopScope(
          canPop: false,
          child: Scaffold(
            appBar: AppBar(
              title: Text(AppLocalizations.of(context)!.gameTitle),
              automaticallyImplyLeading: false,
            ),
            body: SafeArea(child: _buildBody(context, vm)),
          ),
        );
      },
    );
  }

  // ---------------------------------------------------------------------------
  // Navigation
  // ---------------------------------------------------------------------------

  void _scheduleNavigationIfNeeded(BuildContext context, GameViewModel vm) {
    final result = vm.navigationResult;
    if (result == null) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      vm.clearNavigationResult();
      if (!context.mounted) return;
      switch (result) {
        case GameNavigateToMenu():
          onNavigateToMenu();
          break;
        case GameNavigateToResults e:
          onNavigateToResults(e);
          break;
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Corps de la page
  // ---------------------------------------------------------------------------

  Widget _buildBody(BuildContext context, GameViewModel vm) {
    final l10n = AppLocalizations.of(context)!;
    if (vm.errorKey != null) {
      return ErrorStateView(
        errorKey: vm.errorKey!,
        retryLabel: l10n.gameRetry,
        onRetry: () => vm.initialize(),
      );
    }
    return _buildGameContent(context, vm, l10n);
  }

  Widget _buildGameContent(
    BuildContext context,
    GameViewModel vm,
    AppLocalizations l10n,
  ) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildCountdownSection(context, vm, l10n),
          const SizedBox(height: 24),
          _buildRoleCard(context, vm, l10n),
          const SizedBox(height: 24),
          _buildPlayersSection(context, vm, l10n),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Section : Compte à rebours
  // ---------------------------------------------------------------------------

  Widget _buildCountdownSection(
    BuildContext context,
    GameViewModel vm,
    AppLocalizations l10n,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
        child: Column(
          children: [
            Text(
              l10n.gameCountdownLabel,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 8),
            Text(
              vm.countdownText,
              style: Theme.of(context).textTheme.displayMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Theme.of(context).colorScheme.primary,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
            ),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Section : Rôle du joueur
  // ---------------------------------------------------------------------------

  Widget _buildRoleCard(
    BuildContext context,
    GameViewModel vm,
    AppLocalizations l10n,
  ) {
    final role = vm.currentPlayerRole;
    final isSpirit = role?.isSpirit ?? false;

    return Card(
      color: isSpirit
          ? Theme.of(context).colorScheme.errorContainer
          : Theme.of(context).colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text(
              l10n.gameYourRole,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: isSpirit
                        ? Theme.of(context).colorScheme.onErrorContainer
                        : Theme.of(context).colorScheme.onPrimaryContainer,
                  ),
            ),
            const SizedBox(height: 8),
            Icon(
              isSpirit ? Icons.visibility_off : Icons.person,
              size: 48,
              color: isSpirit
                  ? Theme.of(context).colorScheme.onErrorContainer
                  : Theme.of(context).colorScheme.onPrimaryContainer,
            ),
            const SizedBox(height: 8),
            Text(
              _localizedRoleName(vm.currentRoleKey, l10n),
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: isSpirit
                        ? Theme.of(context).colorScheme.onErrorContainer
                        : Theme.of(context).colorScheme.onPrimaryContainer,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  /// Traduit la clé de rôle en nom localisé.
  String _localizedRoleName(String roleKey, AppLocalizations l10n) {
    switch (roleKey) {
      case 'human':
        return l10n.gameRoleHuman;
      case 'spirit':
        return l10n.gameRoleSpirit;
      default:
        return l10n.gameRoleUnknown;
    }
  }

  // ---------------------------------------------------------------------------
  // Section : Liste des joueurs
  // ---------------------------------------------------------------------------

  Widget _buildPlayersSection(
    BuildContext context,
    GameViewModel vm,
    AppLocalizations l10n,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.gamePlayersTitle(vm.roles.length),
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 12),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: vm.roles.length,
          itemBuilder: (context, index) =>
              _buildPlayerTile(context, vm.roles[index], vm, l10n),
        ),
      ],
    );
  }

  Widget _buildPlayerTile(
    BuildContext context,
    GamePlayerRole player,
    GameViewModel vm,
    AppLocalizations l10n,
  ) {
    final isCurrentPlayer = player.playerId == vm.currentPlayerRole?.playerId;
    final initial =
        (player.username.isNotEmpty ? player.username[0] : '?').toUpperCase();
    final displayName = player.username.isNotEmpty
        ? player.username
        : l10n.lobbyPlayerFallbackName(player.playerId);

    return ListTile(
      leading: CircleAvatar(
        backgroundColor: player.isSpirit
            ? Theme.of(context).colorScheme.errorContainer
            : Theme.of(context).colorScheme.primaryContainer,
        child: Text(
          initial,
          style: TextStyle(
            color: player.isSpirit
                ? Theme.of(context).colorScheme.onErrorContainer
                : Theme.of(context).colorScheme.onPrimaryContainer,
          ),
        ),
      ),
      title: Text(
        displayName,
        style: isCurrentPlayer
            ? const TextStyle(fontWeight: FontWeight.bold)
            : null,
      ),
      trailing: Chip(
        label: Text(
          _localizedRoleName(
            player.isSpirit ? 'spirit' : 'human',
            l10n,
          ),
        ),
        backgroundColor: player.isSpirit
            ? Theme.of(context).colorScheme.errorContainer
            : Theme.of(context).colorScheme.primaryContainer,
        side: BorderSide.none,
      ),
    );
  }
}
