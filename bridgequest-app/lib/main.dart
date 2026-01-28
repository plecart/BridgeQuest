import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:provider/provider.dart';

import 'core/config/app_config.dart';
import 'core/config/api_config.dart';
import 'data/services/api_service.dart';
import 'data/services/secure_storage_service.dart';
import 'data/repositories/auth_repository.dart';
import 'providers/auth_provider.dart';
import 'presentation/pages/auth/login_page.dart';
import 'presentation/theme/app_theme.dart';

void main() {
  runApp(const BridgeQuestApp());
}

class BridgeQuestApp extends StatelessWidget {
  const BridgeQuestApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: _buildProviders(),
      child: MaterialApp(
        title: AppConfig.appName,
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        localizationsDelegates: _buildLocalizationDelegates(),
        supportedLocales: _buildSupportedLocales(),
        home: const LoginPage(),
      ),
    );
  }

  /// Construit la liste des providers
  List<ChangeNotifierProvider> _buildProviders() {
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

  /// Construit la liste des délégations de localisation
  List<LocalizationsDelegate> _buildLocalizationDelegates() {
    return const [
      AppLocalizations.delegate,
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ];
  }

  /// Construit la liste des locales supportées
  List<Locale> _buildSupportedLocales() {
    return const [
      Locale('fr', ''),
      Locale('en', ''),
    ];
  }
}
