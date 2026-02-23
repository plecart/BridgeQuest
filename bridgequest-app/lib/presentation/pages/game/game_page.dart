import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../data/models/game/game_player_role.dart';
import '../../../data/repositories/position_repository.dart';
import '../../../data/services/game_websocket_service.dart';
import '../../../data/services/location_service.dart';
import '../../../i18n/app_localizations.dart';
import '../../widgets/error_state_view.dart';
import '../menu/home_page.dart';
import '../results/results_page.dart';
import 'game_view_model.dart';
import 'widgets/game_map_widget.dart';

/// Page principale de jeu affichée pendant la phase IN_PROGRESS.
///
/// Layout : carte plein écran avec overlays pour le countdown,
/// le rôle du joueur et les alertes GPS.
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
      locationService: context.read<LocationService>(),
      positionRepository: context.read<PositionRepository>(),
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
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => ResultsPage(
          gameId: result.gameId,
          scores: result.scores,
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Contenu de la page
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
            body: SafeArea(child: _buildBody(context, vm)),
          ),
        );
      },
    );
  }

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

  Widget _buildBody(BuildContext context, GameViewModel vm) {
    final l10n = AppLocalizations.of(context)!;
    if (vm.errorKey != null) {
      return ErrorStateView(
        errorKey: vm.errorKey!,
        retryLabel: l10n.gameRetry,
        onRetry: () => vm.initialize(),
      );
    }
    return _buildMapLayout(context, vm, l10n);
  }

  Widget _buildMapLayout(
    BuildContext context,
    GameViewModel vm,
    AppLocalizations l10n,
  ) {
    return Stack(
      children: [
        GameMapWidget(
          positions: vm.positions,
          roles: vm.roles,
          currentPlayerId: vm.currentPlayerId,
          showRoles: vm.isCurrentPlayerSpirit,
        ),
        _buildTopOverlay(context, vm, l10n),
        if (vm.locationErrorKey != null)
          _buildLocationWarning(context, vm.locationErrorKey!, l10n),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // Overlay supérieur : countdown + rôle
  // ---------------------------------------------------------------------------

  Widget _buildTopOverlay(
    BuildContext context,
    GameViewModel vm,
    AppLocalizations l10n,
  ) {
    final theme = Theme.of(context);
    final isSpirit = vm.isCurrentPlayerSpirit;

    return Positioned(
      top: 12,
      left: 12,
      right: 12,
      child: Row(
        children: [
          _buildCountdownChip(theme, vm),
          const SizedBox(width: 8),
          _buildRoleChip(theme, vm, l10n, isSpirit),
        ],
      ),
    );
  }

  Widget _buildCountdownChip(ThemeData theme, GameViewModel vm) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.15),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.timer, size: 18, color: theme.colorScheme.primary),
          const SizedBox(width: 6),
          Text(
            vm.countdownText,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.primary,
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRoleChip(
    ThemeData theme,
    GameViewModel vm,
    AppLocalizations l10n,
    bool isSpirit,
  ) {
    final roleName = isSpirit ? l10n.gameRoleSpirit : l10n.gameRoleHuman;
    final bgColor = isSpirit
        ? theme.colorScheme.errorContainer
        : theme.colorScheme.primaryContainer;
    final textColor = isSpirit
        ? theme.colorScheme.onErrorContainer
        : theme.colorScheme.onPrimaryContainer;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: bgColor.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.15),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isSpirit ? Icons.visibility_off : Icons.person,
            size: 18,
            color: textColor,
          ),
          const SizedBox(width: 6),
          Text(
            roleName,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: textColor,
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Avertissement GPS
  // ---------------------------------------------------------------------------

  Widget _buildLocationWarning(
    BuildContext context,
    String errorKey,
    AppLocalizations l10n,
  ) {
    final theme = Theme.of(context);
    final message = _translateLocationError(errorKey, l10n);

    return Positioned(
      bottom: 16,
      left: 16,
      right: 16,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: theme.colorScheme.errorContainer.withValues(alpha: 0.95),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.15),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Icon(
              Icons.location_off,
              color: theme.colorScheme.onErrorContainer,
              size: 20,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                message,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onErrorContainer,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _translateLocationError(String key, AppLocalizations l10n) {
    return switch (key) {
      'errorLocationPermissionDenied' => l10n.errorLocationPermissionDenied,
      'errorLocationServiceDisabled' => l10n.errorLocationServiceDisabled,
      'errorLocationUnavailable' => l10n.errorLocationUnavailable,
      _ => l10n.errorLocationUnavailable,
    };
  }
}
