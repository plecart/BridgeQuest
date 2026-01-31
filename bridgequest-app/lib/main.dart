import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'core/config/app_config.dart';
import 'core/config/app_providers.dart';
import 'core/config/app_localization.dart';
import 'presentation/pages/auth/login_page.dart';
import 'presentation/theme/app_theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Charger les variables d'environnement
  await dotenv.load(fileName: '.env');
  
  runApp(const BridgeQuestApp());
}

/// Application principale Bridge Quest
class BridgeQuestApp extends StatelessWidget {
  const BridgeQuestApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: AppProviders.buildProviders(),
      child: MaterialApp(
        title: AppConfig.appName,
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        localizationsDelegates: AppLocalization.buildDelegates(),
        supportedLocales: AppLocalization.buildSupportedLocales(),
        home: const LoginPage(),
      ),
    );
  }
}
