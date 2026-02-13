/// Constantes liées au cycle de vie d'une partie.
///
/// Centralise les valeurs d'état et de rôle pour éviter les magic strings.
/// Les valeurs correspondent aux enums Django du backend.
abstract final class GameState {
  static const waiting = 'WAITING';
  static const deployment = 'DEPLOYMENT';
  static const inProgress = 'IN_PROGRESS';
  static const finished = 'FINISHED';
}

/// Constantes pour les rôles de joueur.
abstract final class PlayerRole {
  static const human = 'HUMAN';
  static const spirit = 'SPIRIT';
}
