import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../data/services/game_websocket_service.dart';
import '../../../data/services/token_manager.dart';
import '../../../i18n/app_localizations.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/connecting_indicator.dart';
import '../../widgets/error_state_view.dart';
import '../menu/home_page.dart';
import 'deployment_view_model.dart';

/// Page de déploiement affichée pendant la phase DEPLOYMENT.
///
/// Affiche un compte à rebours, un message d'instruction, et navigue
/// vers la page de jeu quand l'événement `game_in_progress` est reçu.
class DeploymentPage extends StatefulWidget {
  const DeploymentPage({
    super.key,
    required this.gameId,
    required this.deploymentEndsAt,
  });

  final int gameId;
  final String deploymentEndsAt;

  @override
  State<DeploymentPage> createState() => _DeploymentPageState();
}

class _DeploymentPageState extends State<DeploymentPage> {
  late final DeploymentViewModel _viewModel;
  bool _navigatedForward = false;

  @override
  void initState() {
    super.initState();
    _viewModel = DeploymentViewModel(
      gameId: widget.gameId,
      deploymentEndsAt: widget.deploymentEndsAt,
      gameWebSocketService: context.read<GameWebSocketService>(),
      tokenManager: context.read<TokenManager>(),
    );
    _viewModel.initialize();
  }

  @override
  void dispose() {
    // Garder la connexion WS si on navigue vers GamePage.
    _viewModel.disposeResources(keepConnection: _navigatedForward);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<DeploymentViewModel>.value(
      value: _viewModel,
      child: _DeploymentContent(
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

  void _navigateToGame(DeploymentNavigateToGame result) {
    if (!mounted) return;
    _navigatedForward = true;
    // TODO(Sprint 3 - Task M): Naviguer vers GamePage
    // Pour l'instant, revenir au menu.
    _navigateToMenu();
  }
}

// ---------------------------------------------------------------------------
// Contenu de la page (séparé pour accéder au ViewModel via Consumer)
// ---------------------------------------------------------------------------

class _DeploymentContent extends StatelessWidget {
  const _DeploymentContent({
    required this.onNavigateToMenu,
    required this.onNavigateToGame,
  });

  final VoidCallback onNavigateToMenu;
  final void Function(DeploymentNavigateToGame) onNavigateToGame;

  @override
  Widget build(BuildContext context) {
    return Consumer<DeploymentViewModel>(
      builder: (context, vm, _) {
        _scheduleNavigationIfNeeded(context, vm);
        return Scaffold(
          appBar: AppBar(
            title: Text(AppLocalizations.of(context)!.deploymentTitle),
            automaticallyImplyLeading: false,
          ),
          body: SafeArea(child: _buildBody(context, vm)),
        );
      },
    );
  }

  // ---------------------------------------------------------------------------
  // Navigation
  // ---------------------------------------------------------------------------

  void _scheduleNavigationIfNeeded(
    BuildContext context,
    DeploymentViewModel vm,
  ) {
    final result = vm.navigationResult;
    if (result == null) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      vm.clearNavigationResult();
      if (!context.mounted) return;
      switch (result) {
        case DeploymentNavigateToMenu():
          onNavigateToMenu();
          break;
        case DeploymentNavigateToGame e:
          onNavigateToGame(e);
          break;
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Corps de la page
  // ---------------------------------------------------------------------------

  Widget _buildBody(BuildContext context, DeploymentViewModel vm) {
    final l10n = AppLocalizations.of(context)!;
    if (vm.isConnecting) {
      return ConnectingIndicator(message: l10n.deploymentConnecting);
    }
    if (vm.errorKey != null) {
      return ErrorStateView(
        errorKey: vm.errorKey!,
        retryLabel: l10n.deploymentRetry,
        onRetry: () => vm.initialize(),
      );
    }
    return _buildCountdownContent(context, vm, l10n);
  }

  Widget _buildCountdownContent(
    BuildContext context,
    DeploymentViewModel vm,
    AppLocalizations l10n,
  ) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.explore,
              size: 64,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(height: 24),
            Text(
              l10n.deploymentSubtitle,
              style: AppTextStyles.homeTitle.copyWith(fontSize: 20),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            Text(
              l10n.deploymentCountdown,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 8),
            _buildCountdownTimer(context, vm),
            if (vm.roles != null) ...[
              const SizedBox(height: 24),
              _buildRolesAssignedBanner(context, l10n),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildCountdownTimer(BuildContext context, DeploymentViewModel vm) {
    return Text(
      vm.countdownText,
      style: Theme.of(context).textTheme.displayMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: Theme.of(context).colorScheme.primary,
            fontFeatures: const [FontFeature.tabularFigures()],
          ),
    );
  }

  Widget _buildRolesAssignedBanner(
    BuildContext context,
    AppLocalizations l10n,
  ) {
    return Card(
      color: Theme.of(context).colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.check_circle,
              color: Theme.of(context).colorScheme.onPrimaryContainer,
            ),
            const SizedBox(width: 8),
            Text(
              l10n.deploymentRolesAssigned,
              style: TextStyle(
                color: Theme.of(context).colorScheme.onPrimaryContainer,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
