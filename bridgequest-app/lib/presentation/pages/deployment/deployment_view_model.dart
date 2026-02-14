import 'package:flutter/foundation.dart';

import '../../../core/utils/countdown_controller.dart';
import '../../../data/models/game/game_player_role.dart';
import '../../../data/services/game_websocket_service.dart';
import '../../../data/services/token_manager.dart';

// ---------------------------------------------------------------------------
// Résultats de navigation
// ---------------------------------------------------------------------------

/// Résultat de la navigation après un événement en phase déploiement.
sealed class DeploymentNavigationResult {
  const DeploymentNavigationResult();
}

/// Fin du déploiement -> naviguer vers la page de jeu.
class DeploymentNavigateToGame extends DeploymentNavigationResult {
  const DeploymentNavigateToGame({
    required this.gameId,
    required this.gameEndsAt,
    required this.roles,
    required this.currentPlayerId,
  });
  final int gameId;
  final String gameEndsAt;
  final List<GamePlayerRole> roles;
  final int currentPlayerId;
}

/// Erreur fatale -> retour au menu.
class DeploymentNavigateToMenu extends DeploymentNavigationResult {
  const DeploymentNavigateToMenu();
}

// ---------------------------------------------------------------------------
// ViewModel
// ---------------------------------------------------------------------------

/// ViewModel pour la page de déploiement.
///
/// Connecte au canal WebSocket game, gère le compte à rebours avant
/// l'attribution des rôles, et déclenche la navigation vers GamePage
/// quand l'événement `game_in_progress` est reçu.
class DeploymentViewModel extends ChangeNotifier {
  DeploymentViewModel({
    required int gameId,
    required String deploymentEndsAt,
    required GameWebSocketService gameWebSocketService,
    required TokenManager tokenManager,
  })  : _gameId = gameId,
        _gameWebSocketService = gameWebSocketService,
        _tokenManager = tokenManager,
        _countdown = CountdownController(
          targetTime: DateTime.parse(deploymentEndsAt).toLocal(),
        );

  final int _gameId;
  final GameWebSocketService _gameWebSocketService;
  final TokenManager _tokenManager;
  final CountdownController _countdown;

  bool _isConnecting = true;
  String? _errorKey;
  List<GamePlayerRole>? _roles;
  int? _connectedPlayerId;
  DeploymentNavigationResult? _navigationResult;

  // ---------------------------------------------------------------------------
  // Getters
  // ---------------------------------------------------------------------------

  int get gameId => _gameId;
  bool get isConnecting => _isConnecting;
  String? get errorKey => _errorKey;
  Duration get remainingTime => _countdown.remainingTime;
  List<GamePlayerRole>? get roles => _roles;
  DeploymentNavigationResult? get navigationResult => _navigationResult;

  /// Minutes et secondes formatées du compte à rebours.
  String get countdownText => _countdown.countdownText;

  // ---------------------------------------------------------------------------
  // Cycle de vie
  // ---------------------------------------------------------------------------

  /// Initialise la connexion WebSocket et démarre le compte à rebours.
  Future<void> initialize() async {
    _setConnecting(true);
    _clearError();
    _countdown.onTick = () => notifyListeners();
    _countdown.start();

    try {
      await _connectWebSocket();
    } catch (e) {
      _setError('deploymentErrorWebSocket');
    } finally {
      _setConnecting(false);
    }
  }

  /// Libère les ressources (timer). Ne déconnecte **pas** le WebSocket
  /// si la navigation va vers GamePage (même connexion réutilisée).
  void disposeResources({bool keepConnection = false}) {
    _countdown.stop();
    if (!keepConnection) {
      _gameWebSocketService.disconnect();
    }
  }

  /// Consomme le résultat de navigation (après que la page ait navigué).
  void clearNavigationResult() {
    _navigationResult = null;
    notifyListeners();
  }

  // ---------------------------------------------------------------------------
  // Connexion WebSocket
  // ---------------------------------------------------------------------------

  Future<void> _connectWebSocket() async {
    final token = await _tokenManager.getAccessToken();
    if (token == null || token.isEmpty) {
      _setError('errorAuthNotAuthenticated');
      return;
    }

    _gameWebSocketService.connect(
      gameId: _gameId,
      accessToken: token,
      onEvent: _handleGameEvent,
    );
  }

  // ---------------------------------------------------------------------------
  // Gestion des événements WebSocket
  // ---------------------------------------------------------------------------

  void _handleGameEvent(GameEvent event) {
    switch (event) {
      case GameConnectedEvent e:
        _connectedPlayerId = e.playerId;
        break;
      case GameRolesAssignedEvent e:
        _handleRolesAssigned(e.players);
        break;
      case GameInProgressEvent e:
        _handleGameInProgress(e);
        break;
      case GameFinishedEvent _:
      case GamePositionUpdatedEvent _:
        // Ignoré pendant le déploiement.
        break;
      case GameErrorEvent _:
        _setError('deploymentErrorWebSocket');
        break;
    }
  }

  void _handleRolesAssigned(List<GamePlayerRole> players) {
    _roles = players;
    notifyListeners();
  }

  void _handleGameInProgress(GameInProgressEvent event) {
    _countdown.stop();
    _setNavigationResult(
      DeploymentNavigateToGame(
        gameId: event.gameId,
        gameEndsAt: event.gameEndsAt,
        roles: _roles ?? [],
        currentPlayerId: _connectedPlayerId ?? 0,
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Helpers d'état
  // ---------------------------------------------------------------------------

  void _setConnecting(bool value) {
    _isConnecting = value;
    notifyListeners();
  }

  void _setError(String key) {
    _errorKey = key;
    notifyListeners();
  }

  void _clearError() {
    _errorKey = null;
    notifyListeners();
  }

  void _setNavigationResult(DeploymentNavigationResult result) {
    _navigationResult = result;
    notifyListeners();
  }
}
