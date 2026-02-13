import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/utils/error_translator.dart';
import '../../../data/models/game/game.dart';
import '../../../data/models/game/lobby_player.dart';
import '../../../data/repositories/game_repository.dart';
import '../../../data/services/lobby_websocket_service.dart';
import '../../../data/services/token_manager.dart';
import '../../../i18n/app_localizations.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/loading_button.dart';
import '../menu/home_page.dart';
import 'lobby_view_model.dart';

/// Page salle d'attente d'une partie.
///
/// Affiche la liste des joueurs connectés en temps réel via WebSocket,
/// le code de la partie, et le bouton de lancement pour l'admin.
class LobbyPage extends StatefulWidget {
  const LobbyPage({super.key, required this.game});

  final Game game;

  @override
  State<LobbyPage> createState() => _LobbyPageState();
}

class _LobbyPageState extends State<LobbyPage> {
  late final LobbyViewModel _viewModel;

  @override
  void initState() {
    super.initState();
    _viewModel = LobbyViewModel(
      game: widget.game,
      gameRepository: context.read<GameRepository>(),
      lobbyWebSocketService: context.read<LobbyWebSocketService>(),
      tokenManager: context.read<TokenManager>(),
    );
    _viewModel.initialize();
  }

  @override
  void dispose() {
    _viewModel.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<LobbyViewModel>.value(
      value: _viewModel,
      child: _LobbyContent(
        onNavigateToMenu: _navigateToMenu,
        onNavigateToGame: _navigateToGame,
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

  void _navigateToGame(int gameId, {required String deploymentEndsAt}) {
    if (!mounted) return;
    // TODO(Sprint 3): Naviguer vers DeploymentPage(gameId, deploymentEndsAt)
    // Pour l'instant, revenir au menu
    _navigateToMenu();
  }
}

class _LobbyContent extends StatelessWidget {
  const _LobbyContent({
    required this.onNavigateToMenu,
    required this.onNavigateToGame,
  });

  final VoidCallback onNavigateToMenu;
  final void Function(int gameId, {required String deploymentEndsAt})
      onNavigateToGame;

  @override
  Widget build(BuildContext context) {
    return Consumer<LobbyViewModel>(
      builder: (context, vm, _) {
        _scheduleNavigationIfNeeded(context, vm);
        return PopScope(
          canPop: false,
          onPopInvokedWithResult: (didPop, _) {
            if (!didPop) _handleBackPressed(context, vm);
          },
          child: Scaffold(
            appBar: AppBar(
              title: Text(vm.game.code),
              leading: IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: () => _handleBackPressed(context, vm),
              ),
            ),
            body: SafeArea(child: _buildBody(context, vm)),
          ),
        );
      },
    );
  }

  Future<void> _handleBackPressed(
    BuildContext context,
    LobbyViewModel vm,
  ) async {
    await vm.leaveAndDisconnect();
    if (!context.mounted) return;
    onNavigateToMenu();
  }

  void _scheduleNavigationIfNeeded(BuildContext context, LobbyViewModel vm) {
    final result = vm.navigationResult;
    if (result == null) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      vm.clearNavigationResult();
      if (!context.mounted) return;
      switch (result) {
        case LobbyNavigateToMenu():
          onNavigateToMenu();
          break;
        case LobbyNavigateToGame e:
          onNavigateToGame(e.gameId, deploymentEndsAt: e.deploymentEndsAt);
          break;
      }
    });
  }

  Widget _buildBody(BuildContext context, LobbyViewModel vm) {
    final l10n = AppLocalizations.of(context)!;
    if (vm.isConnecting) return _buildLoadingState(l10n);
    if (vm.errorKey != null) return _buildErrorState(context, vm, l10n);
    return _buildLobbyContent(context, vm, l10n);
  }

  Widget _buildLoadingState(AppLocalizations l10n) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(l10n.lobbyConnecting),
        ],
      ),
    );
  }

  Widget _buildErrorState(
    BuildContext context,
    LobbyViewModel vm,
    AppLocalizations l10n,
  ) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 48,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              ErrorTranslator.translate(vm.errorKey!, l10n),
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Theme.of(context).colorScheme.error,
              ),
            ),
            const SizedBox(height: 24),
            OutlinedButton(
              onPressed: () => vm.initialize(),
              child: Text(l10n.lobbyRetry),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLobbyContent(
    BuildContext context,
    LobbyViewModel vm,
    AppLocalizations l10n,
  ) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            l10n.lobbyGameCode(vm.game.code),
            style: AppTextStyles.homeTitle,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          Text(
            l10n.lobbyPlayersTitle,
            style: AppTextStyles.homeTitle.copyWith(fontSize: 18),
          ),
          const SizedBox(height: 12),
          _buildPlayerList(context, vm.players),
          if (vm.isAdmin) ...[
            const SizedBox(height: 32),
            LoadingButton(
              label: l10n.lobbyStartGameButton,
              isLoading: vm.isStarting,
              onPressed: () => vm.startGame(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildPlayerList(BuildContext context, List<LobbyPlayer> players) {
    if (players.isEmpty) {
      return Padding(
        padding: const EdgeInsets.all(16),
        child: Text(AppLocalizations.of(context)!.lobbyNoPlayers),
      );
    }
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: players.length,
      itemBuilder: (context, index) =>
          _buildPlayerTile(context, players[index]),
    );
  }

  Widget _buildPlayerTile(BuildContext context, LobbyPlayer player) {
    final l10n = AppLocalizations.of(context)!;
    final initial =
        (player.username.isNotEmpty ? player.username[0] : '?').toUpperCase();
    final displayName = player.username.isNotEmpty
        ? player.username
        : l10n.lobbyPlayerFallbackName(player.playerId);
    return ListTile(
      leading: CircleAvatar(child: Text(initial)),
      title: Text(displayName),
      trailing: player.isAdmin
          ? Icon(
              Icons.admin_panel_settings,
              color: Theme.of(context).colorScheme.tertiary,
            )
          : null,
    );
  }

}
