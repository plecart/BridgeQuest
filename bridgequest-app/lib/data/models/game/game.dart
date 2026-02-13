import '../../../core/constants/game_constants.dart';

/// Modèle représentant une partie de Bridge Quest.
class Game {
  final int id;
  final String code;
  final String state;
  final String? createdAt;
  final String? updatedAt;

  const Game({
    required this.id,
    required this.code,
    required this.state,
    this.createdAt,
    this.updatedAt,
  });

  /// Création depuis JSON (réponse API).
  factory Game.fromJson(Map<String, dynamic> json) {
    return Game(
      id: json['id'] as int,
      code: json['code'] as String,
      state: json['state'] as String,
      createdAt: json['created_at'] as String?,
      updatedAt: json['updated_at'] as String?,
    );
  }

  /// Indique si la partie est en salle d'attente.
  bool get isWaiting => state == GameState.waiting;

  /// Indique si la partie est en déploiement.
  bool get isDeployment => state == GameState.deployment;

  /// Indique si la partie est en cours.
  bool get isInProgress => state == GameState.inProgress;

  /// Indique si la partie est terminée.
  bool get isFinished => state == GameState.finished;
}
