/// Position d'un joueur sur la carte.
///
/// Combine l'identité du joueur et ses coordonnées GPS.
/// Utilisé par [GameViewModel] pour maintenir l'état des positions
/// et par [GameMapWidget] pour afficher les markers.
class PlayerPosition {
  final int playerId;
  final int userId;
  final String username;
  final double latitude;
  final double longitude;
  final DateTime recordedAt;

  const PlayerPosition({
    required this.playerId,
    required this.userId,
    required this.username,
    required this.latitude,
    required this.longitude,
    required this.recordedAt,
  });

  /// Création depuis le payload WebSocket `position_updated`.
  factory PlayerPosition.fromWebSocketEvent({
    required int playerId,
    required int userId,
    required String username,
    required String latitude,
    required String longitude,
    required String recordedAt,
  }) {
    return PlayerPosition(
      playerId: playerId,
      userId: userId,
      username: username,
      latitude: double.parse(latitude),
      longitude: double.parse(longitude),
      recordedAt: DateTime.parse(recordedAt).toLocal(),
    );
  }

  /// Création depuis le JSON de l'API `GET /api/games/{id}/positions/`.
  factory PlayerPosition.fromJson(Map<String, dynamic> json) {
    final userJson = json['user'] as Map<String, dynamic>?;
    return PlayerPosition(
      playerId: json['player_id'] as int,
      userId: userJson?['id'] as int? ?? 0,
      username: userJson?['username'] as String? ?? '',
      latitude: double.parse(json['latitude'] as String),
      longitude: double.parse(json['longitude'] as String),
      recordedAt: DateTime.parse(json['recorded_at'] as String).toLocal(),
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PlayerPosition &&
          runtimeType == other.runtimeType &&
          playerId == other.playerId;

  @override
  int get hashCode => playerId.hashCode;
}
