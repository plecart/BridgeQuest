import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../core/config/api_config.dart';
import '../../core/utils/logger.dart';
import '../models/game/game_player_role.dart';
import '../models/game/game_score_entry.dart';

// ---------------------------------------------------------------------------
// Événements reçus du canal WebSocket game.
// ---------------------------------------------------------------------------

/// Événements reçus du canal WebSocket game (DEPLOYMENT, IN_PROGRESS).
sealed class GameEvent {
  const GameEvent();
}

/// Connexion établie, contient game_id et le joueur local.
class GameConnectedEvent extends GameEvent {
  const GameConnectedEvent({
    required this.gameId,
    required this.playerId,
    required this.userId,
    required this.username,
  });
  final int gameId;
  final int playerId;
  final int userId;
  final String username;
}

/// Rôles attribués à chaque joueur (fin du déploiement).
class GameRolesAssignedEvent extends GameEvent {
  const GameRolesAssignedEvent({required this.players});
  final List<GamePlayerRole> players;
}

/// Partie passée en phase IN_PROGRESS, contient le countdown.
class GameInProgressEvent extends GameEvent {
  const GameInProgressEvent({
    required this.gameId,
    required this.gameEndsAt,
  });
  final int gameId;
  final String gameEndsAt;
}

/// Partie terminée, contient les scores finaux triés par classement.
class GameFinishedEvent extends GameEvent {
  const GameFinishedEvent({
    required this.gameId,
    required this.scores,
  });
  final int gameId;
  final List<GameScoreEntry> scores;
}

/// Mise à jour de position d'un joueur.
class GamePositionUpdatedEvent extends GameEvent {
  const GamePositionUpdatedEvent({
    required this.playerId,
    required this.userId,
    required this.username,
    required this.latitude,
    required this.longitude,
    required this.recordedAt,
  });
  final int playerId;
  final int userId;
  final String username;
  final String latitude;
  final String longitude;
  final String recordedAt;
}

/// Erreur ou fermeture inattendue.
class GameErrorEvent extends GameEvent {
  const GameErrorEvent({required this.message, this.closeCode});
  final String message;
  final int? closeCode;
}

// ---------------------------------------------------------------------------
// Service WebSocket pour la partie en cours.
// ---------------------------------------------------------------------------

/// Service de connexion WebSocket au canal game.
///
/// Gère la connexion, la réception des événements et la fermeture.
/// Utilisé pendant les phases DEPLOYMENT et IN_PROGRESS.
///
/// Le callback [_onEvent] peut être remplacé sans reconnexion via
/// [setEventHandler], permettant la transition DeploymentPage -> GamePage
/// sur la même connexion WebSocket.
class GameWebSocketService {
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  void Function(GameEvent)? _onEvent;

  /// Indique si le canal est connecté.
  bool get isConnected => _channel != null;

  /// Connecte au canal game et démarre l'écoute des événements.
  ///
  /// [gameId] : ID de la partie.
  /// [accessToken] : Token JWT pour l'authentification.
  /// [onEvent] : Callback appelé à chaque événement reçu.
  ///
  /// Ferme une éventuelle connexion existante avant de se connecter.
  void connect({
    required int gameId,
    required String accessToken,
    required void Function(GameEvent) onEvent,
  }) {
    disconnect();
    _onEvent = onEvent;

    final url = ApiConfig.gameWebSocketUrl(gameId, accessToken);
    AppLogger.debug('Game WebSocket connecting to game $gameId');

    _channel = WebSocketChannel.connect(Uri.parse(url));
    _subscription = _channel!.stream.listen(
      _handleMessage,
      onError: _handleError,
      onDone: _clearConnection,
      cancelOnError: false,
    );
  }

  /// Remplace le handler d'événements sans reconnecter.
  ///
  /// Utilisé lors de la transition DeploymentPage -> GamePage pour que
  /// le nouveau ViewModel reçoive les événements sur la connexion existante.
  void setEventHandler(void Function(GameEvent) onEvent) {
    _onEvent = onEvent;
  }

  /// Ferme la connexion WebSocket.
  void disconnect() {
    _channel?.sink.close();
    _clearConnection();
  }

  // ---------------------------------------------------------------------------
  // Dispatch des messages
  // ---------------------------------------------------------------------------

  void _handleError(dynamic error) {
    AppLogger.error('Game WebSocket error', error);
    _onEvent?.call(GameErrorEvent(message: error.toString()));
  }

  void _handleMessage(dynamic data) {
    if (data is! String || _onEvent == null) return;
    try {
      final decoded = jsonDecode(data);
      if (decoded is! Map<String, dynamic>) return;
      final type = decoded['type'] as String?;
      if (type == null) return;

      switch (type) {
        case 'connected':
          _emitConnected(decoded);
          break;
        case 'roles_assigned':
          _emitRolesAssigned(decoded);
          break;
        case 'game_in_progress':
          _emitGameInProgress(decoded);
          break;
        case 'game_finished':
          _emitGameFinished(decoded);
          break;
        case 'position_updated':
          _emitPositionUpdated(decoded);
          break;
        case 'echo':
          // Ignorer les echo de test
          break;
        default:
          AppLogger.debug('Game WebSocket unknown event type: $type');
      }
    } catch (e) {
      AppLogger.error('Game WebSocket message parse error', e);
      _onEvent?.call(GameErrorEvent(message: e.toString()));
    }
  }

  // ---------------------------------------------------------------------------
  // Parsing et émission des événements
  // ---------------------------------------------------------------------------

  void _emitConnected(Map<String, dynamic> decoded) {
    final gameId = decoded['game_id'] as int?;
    final playerJson = decoded['player'] as Map<String, dynamic>?;
    if (gameId == null || playerJson == null) return;

    final playerId = playerJson['player_id'] as int?;
    final userId = playerJson['user_id'] as int?;
    final username = playerJson['username'] as String? ?? '';
    if (playerId == null || userId == null) return;

    _onEvent!(
      GameConnectedEvent(
        gameId: gameId,
        playerId: playerId,
        userId: userId,
        username: username,
      ),
    );
  }

  void _emitRolesAssigned(Map<String, dynamic> decoded) {
    final playersJson = decoded['players'] as List?;
    if (playersJson == null) return;

    final players = playersJson
        .whereType<Map<String, dynamic>>()
        .map(GamePlayerRole.fromJson)
        .toList();

    _onEvent!(GameRolesAssignedEvent(players: players));
  }

  void _emitGameInProgress(Map<String, dynamic> decoded) {
    final gameId = decoded['game_id'] as int?;
    final gameEndsAt = decoded['game_ends_at'] as String?;
    if (gameId == null || gameEndsAt == null) return;

    _onEvent!(
      GameInProgressEvent(gameId: gameId, gameEndsAt: gameEndsAt),
    );
  }

  void _emitGameFinished(Map<String, dynamic> decoded) {
    final gameId = decoded['game_id'] as int?;
    final scoresJson = decoded['scores'] as List?;
    if (gameId == null || scoresJson == null) return;

    final scores = scoresJson
        .whereType<Map<String, dynamic>>()
        .map(GameScoreEntry.fromJson)
        .toList();

    _onEvent!(GameFinishedEvent(gameId: gameId, scores: scores));
  }

  void _emitPositionUpdated(Map<String, dynamic> decoded) {
    final playerId = decoded['player_id'] as int?;
    final userJson = decoded['user'] as Map<String, dynamic>?;
    final latitude = decoded['latitude'] as String?;
    final longitude = decoded['longitude'] as String?;
    final recordedAt = decoded['recorded_at'] as String?;
    if (playerId == null ||
        userJson == null ||
        latitude == null ||
        longitude == null ||
        recordedAt == null) {
      return;
    }

    _onEvent!(
      GamePositionUpdatedEvent(
        playerId: playerId,
        userId: userJson['id'] as int? ?? 0,
        username: userJson['username'] as String? ?? '',
        latitude: latitude,
        longitude: longitude,
        recordedAt: recordedAt,
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Gestion de la connexion
  // ---------------------------------------------------------------------------

  void _clearConnection() {
    _subscription?.cancel();
    _subscription = null;
    _channel = null;
    _onEvent = null;
  }
}
