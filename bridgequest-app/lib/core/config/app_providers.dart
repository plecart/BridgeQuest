import 'package:provider/provider.dart';
import 'package:provider/single_child_widget.dart';
import '../config/api_config.dart';
import '../../data/services/api_service.dart';
import '../../data/services/game_websocket_service.dart';
import '../../data/services/lobby_websocket_service.dart';
import '../../data/services/token_manager.dart';
import '../../data/repositories/auth_repository.dart';
import '../../data/repositories/game_repository.dart';
import '../../providers/auth_provider.dart';

/// Configuration des providers de l'application
class AppProviders {
  AppProviders._();

  /// Construit la liste des providers nécessaires à l'application
  ///
  /// Les services utilisent l'authentification OAuth2/JWT
  /// avec des tokens stockés de manière sécurisée.
  static List<SingleChildWidget> buildProviders() {
    final tokenManager = TokenManager();
    final apiService = ApiService(
      baseUrl: ApiConfig.baseUrl,
      tokenManager: tokenManager,
    );
    final authRepository = AuthRepository(
      apiService: apiService,
      tokenManager: tokenManager,
    );
    final gameRepository = GameRepository(
      apiService: apiService,
    );
    final lobbyWebSocketService = LobbyWebSocketService();
    final gameWebSocketService = GameWebSocketService();

    return [
      Provider<TokenManager>.value(value: tokenManager),
      Provider<LobbyWebSocketService>.value(value: lobbyWebSocketService),
      Provider<GameWebSocketService>.value(value: gameWebSocketService),
      Provider<ApiService>.value(value: apiService),
      Provider<AuthRepository>.value(value: authRepository),
      Provider<GameRepository>.value(value: gameRepository),
      ChangeNotifierProvider(
        create: (context) => AuthProvider(
          authRepository: context.read<AuthRepository>(),
        ),
      ),
    ];
  }
}
