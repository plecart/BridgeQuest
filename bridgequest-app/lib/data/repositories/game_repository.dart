import '../../core/config/api_config.dart';
import '../../core/exceptions/app_exceptions.dart';
import '../../core/utils/logger.dart';
import '../models/game/game.dart';
import '../models/game/player.dart';
import '../services/api_service.dart';

/// Repository pour la gestion des parties.
class GameRepository {
  static const _codeGeneric = 'error.generic';
  static const _codeInvalidFormat = 'error.response.invalidFormat';

  final ApiService _apiService;

  GameRepository({required ApiService apiService}) : _apiService = apiService;

  /// Crée une nouvelle partie.
  ///
  /// L'utilisateur authentifié devient administrateur.
  /// Throws [GameException] si la création échoue.
  Future<Game> createGame() async {
    return _executeApiCall(
      () => _requestGame(
        () => _apiService.post(
          ApiConfig.gamesCreate,
          data: <String, dynamic>{},
        ),
      ),
      'create game',
    );
  }

  /// Rejoint une partie via son code.
  ///
  /// Throws [GameException] si le code est invalide ou si l'utilisateur
  /// est déjà dans la partie.
  Future<Game> joinGame({required String code}) async {
    return _executeApiCall(
      () => _requestGame(
        () => _apiService.post(
          ApiConfig.gamesJoin,
          data: {'code': code.trim().toUpperCase()},
        ),
      ),
      'join game',
    );
  }

  /// Récupère les détails d'une partie.
  ///
  /// Throws [GameException] si la partie n'existe pas.
  Future<Game> getGame(int gameId) async {
    return _executeApiCall(
      () => _requestGame(() => _apiService.get(ApiConfig.gameDetail(gameId))),
      'get game',
    );
  }

  /// Récupère la liste des joueurs d'une partie.
  ///
  /// Throws [GameException] si la partie n'existe pas.
  Future<List<GamePlayer>> getGamePlayers(int gameId) async {
    return _executeApiCall(
      () =>
          _requestPlayers(() => _apiService.get(ApiConfig.gamePlayers(gameId))),
      'get game players',
    );
  }

  /// Lance la partie (admin uniquement).
  ///
  /// Throws [GameException] si l'utilisateur n'est pas admin ou si la partie
  /// est déjà commencée.
  Future<Game> startGame(int gameId) async {
    return _executeApiCall(
      () => _requestGame(
        () => _apiService.post(ApiConfig.gameStart(gameId)),
      ),
      'start game',
    );
  }

  /// Effectue une requête API et parse la réponse en [Game].
  Future<Game> _requestGame(Future<dynamic> Function() request) async {
    final response = await request();
    final data = _normalizeResponseData(response.data);
    return _parseGame(data);
  }

  /// Effectue une requête API et parse la réponse en liste de [GamePlayer].
  ///
  /// L'API retourne un tableau JSON, contrairement aux autres endpoints
  /// qui retournent un objet.
  Future<List<GamePlayer>> _requestPlayers(
    Future<dynamic> Function() request,
  ) async {
    final response = await request();
    return _parsePlayersList(response.data);
  }

  /// Exécute un appel API avec gestion d'erreur standardisée.
  Future<T> _executeApiCall<T>(
    Future<T> Function() operation,
    String errorContext,
  ) async {
    try {
      return await operation();
    } on ApiException catch (e) {
      _handleApiException(e, errorContext);
    } catch (e) {
      if (e is AppException) rethrow;
      AppLogger.error('Unexpected error during $errorContext', e);
      throw GameException(
        'Unexpected error during $errorContext',
        code: _codeGeneric,
      );
    }
  }

  /// Gère les exceptions API et les convertit en [GameException].
  ///
  /// Si l'API renvoie un message (serverMessage), il est prioritaire
  /// pour l'affichage car déjà traduit par le backend.
  /// Gère les exceptions API et les convertit en [GameException].
  ///
  /// Si l'API renvoie un message (serverMessage), il est prioritaire
  /// pour l'affichage car déjà traduit par le backend.
  Never _handleApiException(ApiException e, String errorContext) {
    AppLogger.error('API error during $errorContext', e);
    throw GameException(
      'API error during $errorContext',
      code: e.code ?? _codeGeneric,
      serverMessage: e.serverMessage,
    );
  }

  /// Normalise les données de réponse en [Map].
  Map<String, dynamic> _normalizeResponseData(dynamic data) {
    if (data is Map<String, dynamic>) return data;
    if (data is Map) return Map<String, dynamic>.from(data);
    throw GameException('Invalid response format', code: _codeInvalidFormat);
  }

  /// Parse une partie depuis les données JSON.
  Game _parseGame(Map<String, dynamic> data) {
    try {
      return Game.fromJson(data);
    } catch (e) {
      AppLogger.error('Error parsing game', e);
      throw GameException(
        'Invalid game response format',
        code: _codeInvalidFormat,
      );
    }
  }

  /// Parse la liste des joueurs depuis les données JSON.
  List<GamePlayer> _parsePlayersList(dynamic data) {
    if (data is! List) {
      throw GameException(
        'Invalid players response format',
        code: _codeInvalidFormat,
      );
    }
    return data
        .map((e) => GamePlayer.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
