import 'package:provider/provider.dart';
import 'package:provider/single_child_widget.dart';
import '../config/api_config.dart';
import '../../data/services/api_service.dart';
import '../../data/services/secure_storage_service.dart';
import '../../data/repositories/auth_repository.dart';
import '../../providers/auth_provider.dart';

/// Configuration des providers de l'application
class AppProviders {
  AppProviders._();

  /// Construit la liste des providers nécessaires à l'application
  static List<SingleChildWidget> buildProviders() {
    final secureStorageService = SecureStorageService();
    final apiService = ApiService(
      baseUrl: ApiConfig.baseUrl,
      storageService: secureStorageService,
    );
    final authRepository = AuthRepository(
      apiService: apiService,
      storageService: secureStorageService,
    );

    return [
      Provider<ApiService>.value(value: apiService),
      Provider<SecureStorageService>.value(value: secureStorageService),
      Provider<AuthRepository>.value(value: authRepository),
      ChangeNotifierProvider(
        create: (context) => AuthProvider(
          authRepository: context.read<AuthRepository>(),
        ),
      ),
    ];
  }
}
