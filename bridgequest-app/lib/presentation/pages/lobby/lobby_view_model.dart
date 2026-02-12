import 'package:flutter/foundation.dart';

import '../../../data/models/game/game.dart';
import '../../../data/models/game/lobby_player.dart';
import '../../../data/repositories/game_repository.dart';
import '../../../data/services/lobby_websocket_service.dart';
import '../../../data/services/token_manager.dart';

/// Résultat de la navigation après un événement lobby.
sealed class LobbyNavigationResult {
  const LobbyNavigationResult();
}

/// La partie a été lancée → naviguer vers la carte de jeu.
class LobbyNavigateToGame extends LobbyNavigationResult {
  const LobbyNavigateToGame({required this.gameId});
  final int gameId;
}

/// La partie a été supprimée → naviguer vers le menu.
class LobbyNavigateToMenu extends LobbyNavigationResult {
  const LobbyNavigateToMenu();
}

/// ViewModel pour la page salle d'attente (lobby).
///
/// Gère la connexion WebSocket, la liste des joueurs en temps réel,
/// le lancement de la partie (admin) et les événements (game_deleted, game_started).
class LobbyViewModel extends ChangeNotifier {
  LobbyViewModel({
    required Game game,
    required GameRepository gameRepository,
    required LobbyWebSocketService lobbyWebSocketService,
    required TokenManager tokenManager,
  })  : _game = game,
        _gameRepository = gameRepository,
        _lobbyWebSocketService = lobbyWebSocketService,
        _tokenManager = tokenManager;

  final Game _game;
  final GameRepository _gameRepository;
  final LobbyWebSocketService _lobbyWebSocketService;
  final TokenManager _tokenManager;

  List<LobbyPlayer> _players = [];
  bool _isConnecting = true;
  String? _errorKey;
  bool _isStarting = false;
  LobbyNavigationResult? _navigationResult;

  List<LobbyPlayer> get players => List.unmodifiable(_players);
  bool get isConnecting => _isConnecting;
  String? get errorKey => _errorKey;
  bool get isStarting => _isStarting;
  Game get game => _game;
  LobbyNavigationResult? get navigationResult => _navigationResult;

  /// Indique si l'utilisateur local est admin.
  ///
  /// Mis à jour par "connected" et "admin_transferred".
  bool get isAdmin => _currentPlayer?.isAdmin ?? false;

  LobbyPlayer? _currentPlayer;

  /// Connecte au WebSocket et charge la liste des joueurs.
  Future<void> initialize() async {
    _setConnecting(true);
    _clearError();

    try {
      await _loadPlayers();
      await _connectWebSocket();
    } catch (e) {
      _setError('lobbyErrorWebSocket');
    } finally {
      _setConnecting(false);
    }
  }

  Future<void> _loadPlayers() async {
    final list = await _gameRepository.getGamePlayers(_game.id);
    _players = list
        .map(
          (p) => LobbyPlayer(
            playerId: p.id,
            userId: p.user.id,
            username: p.user.username,
            isAdmin: p.isAdmin,
          ),
        )
        .toList();
    notifyListeners();
  }

  Future<void> _connectWebSocket() async {
    final token = await _tokenManager.getAccessToken();
    if (token == null || token.isEmpty) {
      _setError('errorAuthNotAuthenticated');
      return;
    }

    _lobbyWebSocketService.connect(
      gameId: _game.id,
      accessToken: token,
      onEvent: _handleLobbyEvent,
    );
  }

  void _handleLobbyEvent(LobbyEvent event) {
    switch (event) {
      case LobbyConnectedEvent e:
        _currentPlayer = e.player;
        _addOrUpdatePlayer(e.player);
        break;
      case LobbyPlayerJoinedEvent e:
        _addOrUpdatePlayer(e.player);
        break;
      case LobbyPlayerLeftEvent e:
        _removePlayer(e.player.playerId);
        break;
      case LobbyPlayerExcludedEvent e:
        _removePlayer(e.player.playerId);
        break;
      case LobbyAdminTransferredEvent e:
        _handleAdminTransferred(e.newAdmin);
        break;
      case LobbyGameDeletedEvent _:
        _setNavigationResult(const LobbyNavigateToMenu());
        break;
      case LobbyGameStartedEvent e:
        _setNavigationResult(LobbyNavigateToGame(gameId: e.gameId));
        break;
      case LobbyErrorEvent _:
        _setError('lobbyErrorWebSocket');
        break;
    }
  }

  void _addOrUpdatePlayer(LobbyPlayer player) {
    final idx = _players.indexWhere((p) => p.playerId == player.playerId);
    if (idx >= 0) {
      _players = [
        ..._players.sublist(0, idx),
        player,
        ..._players.sublist(idx + 1),
      ];
    } else {
      _players = [..._players, player];
    }
    notifyListeners();
  }

  void _removePlayer(int playerId) {
    _players = _players.where((p) => p.playerId != playerId).toList();
    notifyListeners();
  }

  void _handleAdminTransferred(LobbyPlayer newAdmin) {
    if (_isLocalPlayer(newAdmin) && newAdmin.isAdmin) {
      _currentPlayer = newAdmin;
    }
    _players = _players.map((p) {
      if (p.playerId == newAdmin.playerId) return newAdmin;
      if (p.isAdmin) return p.copyWith(isAdmin: false);
      return p;
    }).toList();
    notifyListeners();
  }

  bool _isLocalPlayer(LobbyPlayer player) =>
      _currentPlayer?.playerId == player.playerId;

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

  void _setNavigationResult(LobbyNavigationResult result) {
    _navigationResult = result;
    notifyListeners();
  }

  /// Lance la partie (admin uniquement).
  Future<void> startGame() async {
    if (!isAdmin) return;
    _isStarting = true;
    _clearError();
    notifyListeners();

    try {
      await _gameRepository.startGame(_game.id);
      _setNavigationResult(LobbyNavigateToGame(gameId: _game.id));
    } catch (e) {
      _setError('lobbyStartGameError');
    } finally {
      _isStarting = false;
      notifyListeners();
    }
  }

  /// Déconnecte du WebSocket (à appeler au démontage de la page).
  void disconnect() {
    _lobbyWebSocketService.disconnect();
  }

  /// Signale une sortie volontaire au serveur puis déconnecte.
  ///
  /// À appeler quand l'utilisateur quitte volontairement (bouton retour).
  /// Le transfert des droits admin se fait immédiatement, sans attendre 30 s.
  Future<void> leaveAndDisconnect() async {
    await _lobbyWebSocketService.leaveAndDisconnect();
  }

  /// Consomme le résultat de navigation (après que la page ait navigué).
  void clearNavigationResult() {
    _navigationResult = null;
    notifyListeners();
  }
}
