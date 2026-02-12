import '../user.dart';

/// Modèle représentant un joueur dans une partie.
class GamePlayer {
  final int id;
  final User user;
  final bool isAdmin;
  final String role;
  final int score;
  final String? joinedAt;

  const GamePlayer({
    required this.id,
    required this.user,
    required this.isAdmin,
    required this.role,
    required this.score,
    this.joinedAt,
  });

  /// Création depuis JSON (réponse API).
  factory GamePlayer.fromJson(Map<String, dynamic> json) {
    return GamePlayer(
      id: json['id'] as int,
      user: User.fromJson(json['user'] as Map<String, dynamic>),
      isAdmin: json['is_admin'] as bool,
      role: json['role'] as String,
      score: json['score'] as int,
      joinedAt: json['joined_at'] as String?,
    );
  }
}
