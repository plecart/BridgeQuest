import '../../core/config/api_config.dart';
import '../../core/exceptions/app_exceptions.dart';
import '../../core/utils/logger.dart';
import '../models/game/player_position.dart';
import '../services/api_service.dart';

/// Repository pour la gestion des positions GPS.
///
/// Envoie la position du joueur au backend et récupère les positions
/// initiales de tous les joueurs d'une partie.
class PositionRepository {
  static const _codeGeneric = 'error.generic';
  static const _codeSendFailed = 'errorLocationSendFailed';

  final ApiService _apiService;

  PositionRepository({required ApiService apiService})
      : _apiService = apiService;

  /// Envoie la position courante au backend.
  ///
  /// Silencieux en cas d'échec : logge l'erreur sans la propager.
  /// Le tracking GPS continue indépendamment des erreurs d'envoi.
  Future<void> sendPosition({
    required int gameId,
    required double latitude,
    required double longitude,
  }) async {
    try {
      await _apiService.post(
        ApiConfig.locationUpdate,
        data: {
          'game_id': gameId,
          'latitude': latitude.toString(),
          'longitude': longitude.toString(),
        },
      );
    } on ApiException catch (e) {
      AppLogger.error('Failed to send position', e);
    } catch (e) {
      AppLogger.error('Unexpected error sending position', e);
    }
  }

  /// Récupère les dernières positions de tous les joueurs d'une partie.
  ///
  /// Utilisé au chargement initial de la carte pour afficher les positions
  /// existantes avant de recevoir les mises à jour WebSocket.
  Future<List<PlayerPosition>> getGamePositions(int gameId) async {
    try {
      final response = await _apiService.get(ApiConfig.gamePositions(gameId));
      return _parsePositionsList(response.data);
    } on ApiException catch (e) {
      AppLogger.error('API error fetching positions', e);
      throw GameException(
        'API error fetching positions',
        code: e.code ?? _codeGeneric,
        serverMessage: e.serverMessage,
      );
    } catch (e) {
      if (e is AppException) rethrow;
      AppLogger.error('Unexpected error fetching positions', e);
      throw GameException(
        'Unexpected error fetching positions',
        code: _codeSendFailed,
      );
    }
  }

  List<PlayerPosition> _parsePositionsList(dynamic data) {
    if (data is! List) return [];
    return data
        .whereType<Map<String, dynamic>>()
        .map(PlayerPosition.fromJson)
        .toList();
  }
}
