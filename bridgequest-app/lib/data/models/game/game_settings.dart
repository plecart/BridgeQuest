/// Paramètres de configuration d'une partie de Bridge Quest.
///
/// Correspond au JSON retourné par GET/PATCH /api/games/{id}/settings/.
/// Tous les champs sont configurables par l'admin en salle d'attente.
class GameSettings {
  final int gameDuration;
  final int deploymentDuration;
  final int spiritPercentage;
  final int pointsPerMinute;
  final int conversionPointsPercentage;

  const GameSettings({
    required this.gameDuration,
    required this.deploymentDuration,
    required this.spiritPercentage,
    required this.pointsPerMinute,
    required this.conversionPointsPercentage,
  });

  /// Création depuis JSON (réponse API).
  factory GameSettings.fromJson(Map<String, dynamic> json) {
    return GameSettings(
      gameDuration: json['game_duration'] as int,
      deploymentDuration: json['deployment_duration'] as int,
      spiritPercentage: json['spirit_percentage'] as int,
      pointsPerMinute: json['points_per_minute'] as int,
      conversionPointsPercentage: json['conversion_points_percentage'] as int,
    );
  }

  /// Conversion en JSON (requête PATCH).
  Map<String, dynamic> toJson() {
    return {
      'game_duration': gameDuration,
      'deployment_duration': deploymentDuration,
      'spirit_percentage': spiritPercentage,
      'points_per_minute': pointsPerMinute,
      'conversion_points_percentage': conversionPointsPercentage,
    };
  }

  /// Copie avec modifications partielles (immutabilité).
  GameSettings copyWith({
    int? gameDuration,
    int? deploymentDuration,
    int? spiritPercentage,
    int? pointsPerMinute,
    int? conversionPointsPercentage,
  }) {
    return GameSettings(
      gameDuration: gameDuration ?? this.gameDuration,
      deploymentDuration: deploymentDuration ?? this.deploymentDuration,
      spiritPercentage: spiritPercentage ?? this.spiritPercentage,
      pointsPerMinute: pointsPerMinute ?? this.pointsPerMinute,
      conversionPointsPercentage:
          conversionPointsPercentage ?? this.conversionPointsPercentage,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is GameSettings &&
          runtimeType == other.runtimeType &&
          gameDuration == other.gameDuration &&
          deploymentDuration == other.deploymentDuration &&
          spiritPercentage == other.spiritPercentage &&
          pointsPerMinute == other.pointsPerMinute &&
          conversionPointsPercentage == other.conversionPointsPercentage;

  @override
  int get hashCode => Object.hash(
        gameDuration,
        deploymentDuration,
        spiritPercentage,
        pointsPerMinute,
        conversionPointsPercentage,
      );
}
