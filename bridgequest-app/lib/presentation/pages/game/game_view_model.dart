import 'package:flutter/foundation.dart';

import '../../../core/constants/game_constants.dart';
import '../../../core/utils/countdown_controller.dart';
import '../../../data/models/game/game_player_role.dart';
import '../../../data/models/game/game_score_entry.dart';
import '../../../data/services/game_websocket_service.dart';

// ---------------------------------------------------------------------------
// Résultats de navigation
// ---------------------------------------------------------------------------

/// Résultat de la navigation après un événement en phase de jeu.
sealed class GameNavigationResult {
  const GameNavigationResult();
}

/// Partie terminée -> naviguer vers la page des résultats.
class GameNavigateToResults extends GameNavigationResult {
  const GameNavigateToResults({
    required this.gameId,
    required this.scores,
  });
  final int gameId;
  final List<GameScoreEntry> scores;
}

/// Erreur fatale -> retour au menu.
class GameNavigateToMenu extends GameNavigationResult {
  const GameNavigateToMenu();
}

// ---------------------------------------------------------------------------
// ViewModel
// ---------------------------------------------------------------------------

/// ViewModel pour la page de jeu (phase IN_PROGRESS).
///
/// Reprend la connexion WebSocket existante via [setEventHandler],
/// gère le compte à rebours avant la fin de partie, affiche le rôle
/// du joueur courant et la liste des joueurs. Déclenche la navigation
/// vers ResultsPage quand l'événement `game_finished` est reçu.
class GameViewModel extends ChangeNotifier {
  GameViewModel({
    required int gameId,
    required String gameEndsAt,
    required List<GamePlayerRole> roles,
    required int currentPlayerId,
    required GameWebSocketService gameWebSocketService,
  })  : _gameId = gameId,
        _roles = roles,
        _currentPlayerId = currentPlayerId,
        _gameWebSocketService = gameWebSocketService,
        _countdown = CountdownController(
          targetTime: DateTime.parse(gameEndsAt).toLocal(),
        );

  final int _gameId;
  final List<GamePlayerRole> _roles;
  final int _currentPlayerId;
  final GameWebSocketService _gameWebSocketService;
  final CountdownController _countdown;

  String? _errorKey;
  GameNavigationResult? _navigationResult;

  // ---------------------------------------------------------------------------
  // Getters
  // ---------------------------------------------------------------------------

  int get gameId => _gameId;
  List<GamePlayerRole> get roles => List.unmodifiable(_roles);
  String? get errorKey => _errorKey;
  GameNavigationResult? get navigationResult => _navigationResult;
  Duration get remainingTime => _countdown.remainingTime;
  String get countdownText => _countdown.countdownText;

  /// Rôle du joueur courant (recherché par playerId).
  GamePlayerRole? get currentPlayerRole {
    for (final r in _roles) {
      if (r.playerId == _currentPlayerId) return r;
    }
    return null;
  }

  /// Clé de rôle du joueur courant (`'human'` / `'spirit'` / `'unknown'`).
  String get currentRoleKey {
    final role = currentPlayerRole?.role;
    if (role == PlayerRole.spirit) return 'spirit';
    if (role == PlayerRole.human) return 'human';
    return 'unknown';
  }

  // ---------------------------------------------------------------------------
  // Cycle de vie
  // ---------------------------------------------------------------------------

  /// Initialise le ViewModel : reprend la connexion WS et démarre le countdown.
  ///
  /// Utilise [setEventHandler] sur le [GameWebSocketService] existant
  /// (connexion établie durant la phase de déploiement).
  void initialize() {
    _countdown.onTick = () => notifyListeners();
    _countdown.start();
    _gameWebSocketService.setEventHandler(_handleGameEvent);
  }

  /// Libère les ressources (timer) et déconnecte le WebSocket.
  void disposeResources() {
    _countdown.stop();
    _gameWebSocketService.disconnect();
  }

  /// Consomme le résultat de navigation (après que la page ait navigué).
  void clearNavigationResult() {
    _navigationResult = null;
    notifyListeners();
  }

  // ---------------------------------------------------------------------------
  // Gestion des événements WebSocket
  // ---------------------------------------------------------------------------

  void _handleGameEvent(GameEvent event) {
    switch (event) {
      case GameConnectedEvent _:
      case GameRolesAssignedEvent _:
      case GameInProgressEvent _:
        // Déjà traités pendant le déploiement, ignorés ici.
        break;
      case GameFinishedEvent e:
        _handleGameFinished(e);
        break;
      case GamePositionUpdatedEvent _:
        // TODO(Sprint futur): Mettre à jour les positions sur la carte.
        break;
      case GameErrorEvent _:
        _setError('gameErrorWebSocket');
        break;
    }
  }

  void _handleGameFinished(GameFinishedEvent event) {
    _countdown.stop();
    _setNavigationResult(
      GameNavigateToResults(
        gameId: event.gameId,
        scores: event.scores,
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Helpers d'état
  // ---------------------------------------------------------------------------

  void _setError(String key) {
    _errorKey = key;
    notifyListeners();
  }

  void _setNavigationResult(GameNavigationResult result) {
    _navigationResult = result;
    notifyListeners();
  }
}
