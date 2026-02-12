/// Modèle représentant une partie de Bridge Quest.
class Game {
  final int id;
  final String code;
  final String state;
  final String? createdAt;
  final String? updatedAt;

  Game({
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
  bool get isWaiting => state == 'WAITING';

  /// Indique si la partie est terminée.
  bool get isFinished => state == 'FINISHED';
}
