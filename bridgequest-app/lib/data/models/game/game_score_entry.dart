import '../../../core/constants/game_constants.dart';

/// Entrée de score d'un joueur (payload de l'événement `game_finished`).
///
/// Correspond au JSON envoyé par le backend dans l'événement WebSocket
/// `game_finished`. La liste est triée par score décroissant (classement).
class GameScoreEntry {
  final int playerId;
  final int userId;
  final String username;
  final String role;
  final int score;

  const GameScoreEntry({
    required this.playerId,
    required this.userId,
    required this.username,
    required this.role,
    required this.score,
  });

  /// Création depuis JSON (payload WebSocket).
  factory GameScoreEntry.fromJson(Map<String, dynamic> json) {
    return GameScoreEntry(
      playerId: json['player_id'] as int,
      userId: json['user_id'] as int,
      username: json['username'] as String? ?? '',
      role: json['role'] as String,
      score: json['score'] as int,
    );
  }

  /// Indique si le joueur est un Esprit.
  bool get isSpirit => role == PlayerRole.spirit;

  /// Indique si le joueur est un Humain.
  bool get isHuman => role == PlayerRole.human;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is GameScoreEntry &&
          runtimeType == other.runtimeType &&
          playerId == other.playerId;

  @override
  int get hashCode => playerId.hashCode;
}
