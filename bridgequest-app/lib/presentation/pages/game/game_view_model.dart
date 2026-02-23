import 'package:flutter/foundation.dart';

import '../../../core/constants/game_constants.dart';
import '../../../core/utils/countdown_controller.dart';
import '../../../core/utils/logger.dart';
import '../../../data/models/game/game_player_role.dart';
import '../../../data/models/game/game_score_entry.dart';
import '../../../data/models/game/player_position.dart';
import '../../../data/repositories/position_repository.dart';
import '../../../data/services/game_websocket_service.dart';
import '../../../data/services/location_service.dart';

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
/// Gère le compte à rebours, l'affichage des rôles, le tracking GPS,
/// les positions temps réel des joueurs, et les règles de visibilité.
///
/// Règles de visibilité carte :
/// - Tout le monde voit tous les joueurs sur la carte.
/// - Seuls les Esprits voient les rôles de chaque joueur.
/// - Les Humains ne voient pas les rôles (tous les markers sont neutres).
class GameViewModel extends ChangeNotifier {
  GameViewModel({
    required int gameId,
    required String gameEndsAt,
    required List<GamePlayerRole> roles,
    required int currentPlayerId,
    required GameWebSocketService gameWebSocketService,
    required LocationService locationService,
    required PositionRepository positionRepository,
  })  : _gameId = gameId,
        _roles = roles,
        _currentPlayerId = currentPlayerId,
        _gameWebSocketService = gameWebSocketService,
        _locationService = locationService,
        _positionRepository = positionRepository,
        _countdown = CountdownController(
          targetTime: DateTime.parse(gameEndsAt).toLocal(),
        );

  final int _gameId;
  final List<GamePlayerRole> _roles;
  final int _currentPlayerId;
  final GameWebSocketService _gameWebSocketService;
  final LocationService _locationService;
  final PositionRepository _positionRepository;
  final CountdownController _countdown;

  final Map<int, PlayerPosition> _positions = {};
  String? _errorKey;
  String? _locationErrorKey;
  GameNavigationResult? _navigationResult;

  // ---------------------------------------------------------------------------
  // Getters
  // ---------------------------------------------------------------------------

  int get gameId => _gameId;
  int get currentPlayerId => _currentPlayerId;
  List<GamePlayerRole> get roles => List.unmodifiable(_roles);
  String? get errorKey => _errorKey;
  String? get locationErrorKey => _locationErrorKey;
  GameNavigationResult? get navigationResult => _navigationResult;
  Duration get remainingTime => _countdown.remainingTime;
  String get countdownText => _countdown.countdownText;

  /// Positions de tous les joueurs, indexées par playerId.
  Map<int, PlayerPosition> get positions => Map.unmodifiable(_positions);

  /// Rôle du joueur courant.
  GamePlayerRole? get currentPlayerRole {
    for (final r in _roles) {
      if (r.playerId == _currentPlayerId) return r;
    }
    return null;
  }

  /// `true` si le joueur courant est un Esprit.
  bool get isCurrentPlayerSpirit =>
      currentPlayerRole?.role == PlayerRole.spirit;

  /// Clé de rôle du joueur courant (`'human'` / `'spirit'` / `'unknown'`).
  String get currentRoleKey {
    final role = currentPlayerRole?.role;
    if (role == PlayerRole.spirit) return 'spirit';
    if (role == PlayerRole.human) return 'human';
    return 'unknown';
  }

  /// Position du joueur courant (pour centrer la carte).
  PlayerPosition? get currentPlayerPosition => _positions[_currentPlayerId];

  // ---------------------------------------------------------------------------
  // Cycle de vie
  // ---------------------------------------------------------------------------

  /// Initialise le ViewModel : charge les positions, reprend le WS,
  /// démarre le countdown et le tracking GPS.
  void initialize() {
    _countdown.onTick = () => notifyListeners();
    _countdown.start();
    _gameWebSocketService.setEventHandler(_handleGameEvent);
    _loadInitialPositions();
    _startLocationTracking();
  }

  /// Libère toutes les ressources.
  void disposeResources() {
    _countdown.stop();
    _locationService.stopTracking();
    _gameWebSocketService.disconnect();
  }

  /// Consomme le résultat de navigation.
  void clearNavigationResult() {
    _navigationResult = null;
    notifyListeners();
  }

  // ---------------------------------------------------------------------------
  // Chargement initial des positions
  // ---------------------------------------------------------------------------

  Future<void> _loadInitialPositions() async {
    try {
      final positionsList = await _positionRepository.getGamePositions(_gameId);
      for (final pos in positionsList) {
        _positions[pos.playerId] = pos;
      }
    } catch (e) {
      AppLogger.error('Failed to load initial positions', e);
    } finally {
      notifyListeners();
    }
  }

  // ---------------------------------------------------------------------------
  // Tracking GPS
  // ---------------------------------------------------------------------------

  Future<void> _startLocationTracking() async {
    final result = await _locationService.ensurePermission();
    if (result != LocationPermissionResult.granted) {
      _locationErrorKey = result == LocationPermissionResult.serviceDisabled
          ? 'errorLocationServiceDisabled'
          : 'errorLocationPermissionDenied';
      notifyListeners();
      return;
    }

    _locationService.startTracking(
      onPositionChanged: _handleLocalPositionChanged,
    );
  }

  void _handleLocalPositionChanged(double latitude, double longitude) {
    _positions[_currentPlayerId] = PlayerPosition(
      playerId: _currentPlayerId,
      userId: currentPlayerRole?.userId ?? 0,
      username: currentPlayerRole?.username ?? '',
      latitude: latitude,
      longitude: longitude,
      recordedAt: DateTime.now(),
    );
    notifyListeners();

    _positionRepository.sendPosition(
      gameId: _gameId,
      latitude: latitude,
      longitude: longitude,
    );
  }

  // ---------------------------------------------------------------------------
  // Gestion des événements WebSocket
  // ---------------------------------------------------------------------------

  void _handleGameEvent(GameEvent event) {
    switch (event) {
      case GameConnectedEvent _:
      case GameRolesAssignedEvent _:
      case GameInProgressEvent _:
        break;
      case GameFinishedEvent e:
        _handleGameFinished(e);
        break;
      case GamePositionUpdatedEvent e:
        _handlePositionUpdated(e);
        break;
      case GameErrorEvent _:
        _setError('gameErrorWebSocket');
        break;
    }
  }

  void _handleGameFinished(GameFinishedEvent event) {
    _countdown.stop();
    _locationService.stopTracking();
    _setNavigationResult(
      GameNavigateToResults(
        gameId: event.gameId,
        scores: event.scores,
      ),
    );
  }

  void _handlePositionUpdated(GamePositionUpdatedEvent event) {
    _positions[event.playerId] = PlayerPosition.fromWebSocketEvent(
      playerId: event.playerId,
      userId: event.userId,
      username: event.username,
      latitude: event.latitude,
      longitude: event.longitude,
      recordedAt: event.recordedAt,
    );
    notifyListeners();
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
