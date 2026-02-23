import '../../../core/constants/game_constants.dart';

/// Rôle attribué à un joueur (payload de l'événement `roles_assigned`).
///
/// Correspond au JSON envoyé par le backend dans l'événement WebSocket
/// `roles_assigned` à la fin de la phase de déploiement.
class GamePlayerRole {
  final int playerId;
  final int userId;
  final String username;
  final String role;

  const GamePlayerRole({
    required this.playerId,
    required this.userId,
    required this.username,
    required this.role,
  });

  /// Création depuis JSON (payload WebSocket).
  factory GamePlayerRole.fromJson(Map<String, dynamic> json) {
    return GamePlayerRole(
      playerId: json['player_id'] as int,
      userId: json['user_id'] as int,
      username: json['username'] as String? ?? '',
      role: json['role'] as String,
    );
  }

  /// Indique si le joueur est un Esprit.
  bool get isSpirit => role == PlayerRole.spirit;

  /// Indique si le joueur est un Humain.
  bool get isHuman => role == PlayerRole.human;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is GamePlayerRole &&
          runtimeType == other.runtimeType &&
          playerId == other.playerId;

  @override
  int get hashCode => playerId.hashCode;
}
