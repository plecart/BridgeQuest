import 'package:provider/provider.dart';
import 'package:provider/single_child_widget.dart';
import '../config/api_config.dart';
import '../../data/services/api_service.dart';
import '../../data/services/token_manager.dart';
import '../../data/repositories/auth_repository.dart';
import '../../providers/auth_provider.dart';

/// Configuration des providers de l'application
class AppProviders {
  AppProviders._();

  /// Construit la liste des providers nécessaires à l'application
  /// 
  /// Les services utilisent maintenant l'authentification OAuth2/JWT
  /// avec des tokens stockés de manière sécurisée.
  /// Une seule instance de [TokenManager] est partagée entre [ApiService] et
  /// [AuthRepository] pour que le cache en mémoire soit à jour après un login SSO.
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

    return [
      Provider<ApiService>.value(value: apiService),
      Provider<AuthRepository>.value(value: authRepository),
      ChangeNotifierProvider(
        create: (context) => AuthProvider(
          authRepository: context.read<AuthRepository>(),
        ),
      ),
    ];
  }
}
