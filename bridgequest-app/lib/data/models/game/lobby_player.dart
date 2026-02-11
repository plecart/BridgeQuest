/// Modèle minimal d'un joueur pour les événements WebSocket du lobby.
///
/// Correspond au payload des événements connected, player_joined, player_left,
/// player_excluded, admin_transferred.
class LobbyPlayer {
  const LobbyPlayer({
    required this.playerId,
    required this.userId,
    required this.username,
    this.isAdmin = false,
  });

  final int playerId;
  final int userId;
  final String username;
  final bool isAdmin;

  /// Création depuis le payload JSON des événements WebSocket lobby.
  factory LobbyPlayer.fromJson(Map<String, dynamic> json) {
    return LobbyPlayer(
      playerId: json['player_id'] as int,
      userId: json['user_id'] as int,
      username: json['username'] as String? ?? '',
      isAdmin: json['is_admin'] as bool? ?? false,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is LobbyPlayer &&
          runtimeType == other.runtimeType &&
          playerId == other.playerId;

  @override
  int get hashCode => playerId.hashCode;
}
