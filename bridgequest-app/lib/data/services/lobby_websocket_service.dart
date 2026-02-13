import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../core/config/api_config.dart';
import '../../core/utils/logger.dart';
import '../models/game/game_settings.dart';
import '../models/game/lobby_player.dart';

/// Événements reçus du canal WebSocket lobby.
sealed class LobbyEvent {
  const LobbyEvent();
}

/// Connexion établie, contient game_id et le joueur local.
class LobbyConnectedEvent extends LobbyEvent {
  const LobbyConnectedEvent({
    required this.gameId,
    required this.player,
  });
  final int gameId;
  final LobbyPlayer player;
}

/// Un joueur a rejoint la salle.
class LobbyPlayerJoinedEvent extends LobbyEvent {
  const LobbyPlayerJoinedEvent({required this.player});
  final LobbyPlayer player;
}

/// Un joueur a quitté le canal (déconnexion — peut se reconnecter sous 30 s).
class LobbyPlayerLeftEvent extends LobbyEvent {
  const LobbyPlayerLeftEvent({required this.player});
  final LobbyPlayer player;
}

/// Un joueur exclu après 30 s sans reconnexion.
class LobbyPlayerExcludedEvent extends LobbyEvent {
  const LobbyPlayerExcludedEvent({required this.player});
  final LobbyPlayer player;
}

/// Droits admin transférés à un nouveau joueur.
class LobbyAdminTransferredEvent extends LobbyEvent {
  const LobbyAdminTransferredEvent({required this.newAdmin});
  final LobbyPlayer newAdmin;
}

/// Partie supprimée (admin exclu seul).
class LobbyGameDeletedEvent extends LobbyEvent {
  const LobbyGameDeletedEvent({required this.gameId});
  final int gameId;
}

/// Partie lancée (state: DEPLOYMENT).
class LobbyGameStartedEvent extends LobbyEvent {
  const LobbyGameStartedEvent({
    required this.gameId,
    required this.state,
    required this.deploymentEndsAt,
  });
  final int gameId;
  final String state;
  final String deploymentEndsAt;
}

/// Paramètres de la partie modifiés par l'admin.
class LobbySettingsUpdatedEvent extends LobbyEvent {
  const LobbySettingsUpdatedEvent({required this.settings});
  final GameSettings settings;
}

/// Erreur ou fermeture inattendue.
class LobbyErrorEvent extends LobbyEvent {
  const LobbyErrorEvent({required this.message, this.closeCode});
  final String message;
  final int? closeCode;
}

/// Type de message pour signaler une sortie volontaire (exclusion immédiate).
const _leaveMessageType = 'leave';

/// Service de connexion WebSocket au canal lobby.
///
/// Gère la connexion, la réception des événements et la fermeture.
/// Ne gère pas la reconnexion automatique ; le ViewModel peut le faire.
class LobbyWebSocketService {
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;

  /// Indique si le canal est connecté.
  bool get isConnected => _channel != null;

  /// Connecte au canal lobby et démarre l'écoute des événements.
  ///
  /// [gameId] : ID de la partie
  /// [accessToken] : Token JWT pour l'authentification
  /// [onEvent] : Callback appelé à chaque événement reçu
  ///
  /// Ferme une éventuelle connexion existante avant de se connecter.
  void connect({
    required int gameId,
    required String accessToken,
    required void Function(LobbyEvent) onEvent,
  }) {
    disconnect();

    final url = ApiConfig.lobbyWebSocketUrl(gameId, accessToken);
    AppLogger.debug('Lobby WebSocket connecting to game $gameId');

    _channel = WebSocketChannel.connect(Uri.parse(url));
    _subscription = _channel!.stream.listen(
      (data) => _handleMessage(data, onEvent),
      onError: (error) {
        AppLogger.error('Lobby WebSocket error', error);
        onEvent(LobbyErrorEvent(message: error.toString()));
      },
      onDone: _clearConnection,
      cancelOnError: false,
    );
  }

  void _handleMessage(dynamic data, void Function(LobbyEvent) onEvent) {
    if (data is! String) return;
    try {
      final decoded = jsonDecode(data);
      if (decoded is! Map<String, dynamic>) return;
      final type = decoded['type'] as String?;
      if (type == null) return;

      switch (type) {
        case 'connected':
          _emitConnected(decoded, onEvent);
          break;
        case 'player_joined':
          _emitPlayerJoined(decoded, onEvent);
          break;
        case 'player_left':
          _emitPlayerLeft(decoded, onEvent);
          break;
        case 'player_excluded':
          _emitPlayerExcluded(decoded, onEvent);
          break;
        case 'admin_transferred':
          _emitAdminTransferred(decoded, onEvent);
          break;
        case 'game_deleted':
          _emitGameDeleted(decoded, onEvent);
          break;
        case 'game_started':
          _emitGameStarted(decoded, onEvent);
          break;
        case 'settings_updated':
          _emitSettingsUpdated(decoded, onEvent);
          break;
        case 'echo':
          // Ignorer les echo de test
          break;
        default:
          AppLogger.debug('Lobby WebSocket unknown event type: $type');
      }
    } catch (e) {
      AppLogger.error('Lobby WebSocket message parse error', e);
      onEvent(LobbyErrorEvent(message: e.toString()));
    }
  }

  LobbyPlayer? _parsePlayer(Map<String, dynamic> decoded, String key) {
    final json = decoded[key] as Map<String, dynamic>?;
    return json != null ? LobbyPlayer.fromJson(json) : null;
  }

  void _emitConnected(
    Map<String, dynamic> decoded,
    void Function(LobbyEvent) onEvent,
  ) {
    final gameId = decoded['game_id'] as int?;
    final player = _parsePlayer(decoded, 'player');
    if (gameId == null || player == null) return;
    onEvent(LobbyConnectedEvent(gameId: gameId, player: player));
  }

  void _emitPlayerJoined(
    Map<String, dynamic> decoded,
    void Function(LobbyEvent) onEvent,
  ) {
    final player = _parsePlayer(decoded, 'player');
    if (player == null) return;
    onEvent(LobbyPlayerJoinedEvent(player: player));
  }

  void _emitPlayerLeft(
    Map<String, dynamic> decoded,
    void Function(LobbyEvent) onEvent,
  ) {
    final player = _parsePlayer(decoded, 'player');
    if (player == null) return;
    onEvent(LobbyPlayerLeftEvent(player: player));
  }

  void _emitPlayerExcluded(
    Map<String, dynamic> decoded,
    void Function(LobbyEvent) onEvent,
  ) {
    final player = _parsePlayer(decoded, 'player');
    if (player == null) return;
    onEvent(LobbyPlayerExcludedEvent(player: player));
  }

  void _emitAdminTransferred(
    Map<String, dynamic> decoded,
    void Function(LobbyEvent) onEvent,
  ) {
    final newAdmin = _parsePlayer(decoded, 'new_admin');
    if (newAdmin == null) return;
    onEvent(LobbyAdminTransferredEvent(newAdmin: newAdmin));
  }

  void _emitGameDeleted(
    Map<String, dynamic> decoded,
    void Function(LobbyEvent) onEvent,
  ) {
    final gameId = decoded['game_id'] as int?;
    if (gameId == null) return;
    onEvent(LobbyGameDeletedEvent(gameId: gameId));
  }

  void _emitGameStarted(
    Map<String, dynamic> decoded,
    void Function(LobbyEvent) onEvent,
  ) {
    final gameId = decoded['game_id'] as int?;
    final state = decoded['state'] as String?;
    final deploymentEndsAt = decoded['deployment_ends_at'] as String?;
    if (gameId == null || state == null || deploymentEndsAt == null) return;
    onEvent(
      LobbyGameStartedEvent(
        gameId: gameId,
        state: state,
        deploymentEndsAt: deploymentEndsAt,
      ),
    );
  }

  void _emitSettingsUpdated(
    Map<String, dynamic> decoded,
    void Function(LobbyEvent) onEvent,
  ) {
    final settingsJson = decoded['settings'] as Map<String, dynamic>?;
    if (settingsJson == null) return;
    onEvent(
      LobbySettingsUpdatedEvent(
        settings: GameSettings.fromJson(settingsJson),
      ),
    );
  }

  /// Ferme la connexion WebSocket.
  void disconnect() {
    _channel?.sink.close();
    _clearConnection();
  }

  /// Envoie le message de sortie volontaire puis ferme la connexion.
  ///
  /// À appeler quand l'utilisateur quitte volontairement (retour, déconnexion).
  /// Permet au serveur d'exclure immédiatement sans attendre les 30 s.
  ///
  /// L'appel à [sink.close] est attendu pour garantir que le message soit
  /// transmis avant la fermeture (flush implicite).
  Future<void> leaveAndDisconnect() async {
    if (_channel == null) {
      _clearConnection();
      return;
    }
    try {
      _channel!.sink.add(jsonEncode({'type': _leaveMessageType}));
      await _channel!.sink.close();
    } catch (_) {
      // Ignorer si la connexion est déjà fermée
    } finally {
      _clearConnection();
    }
  }

  void _clearConnection() {
    _subscription?.cancel();
    _subscription = null;
    _channel = null;
  }
}
