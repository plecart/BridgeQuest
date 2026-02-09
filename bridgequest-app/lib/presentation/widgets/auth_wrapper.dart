import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../pages/auth/login_page.dart';
import '../pages/menu/home_page.dart';

/// Widget qui gère la navigation conditionnelle selon l'état d'authentification
/// 
/// Affiche la page de connexion si l'utilisateur n'est pas authentifié,
/// sinon affiche la page d'accueil.
class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isInitializing = true;

  @override
  void initState() {
    super.initState();
    _initializeAuth();
  }

  /// Initialise l'authentification après le premier frame
  /// 
  /// Utilise [addPostFrameCallback] avec un délai pour éviter de bloquer
  /// le thread principal au démarrage et permettre au premier frame de s'afficher.
  void _initializeAuth() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      // Délai supplémentaire pour permettre au premier frame de s'afficher
      // et éviter de bloquer le thread principal
      Future.delayed(const Duration(milliseconds: 100), () {
        if (mounted) {
          _checkAuthStatus();
        }
      });
    });
  }

  /// Vérifie l'état d'authentification au démarrage
  Future<void> _checkAuthStatus() async {
    if (!mounted) return;

    final authProvider = context.read<AuthProvider>();
    try {
      await authProvider.checkAuthStatus();
    } catch (e) {
      // En cas d'erreur, l'utilisateur sera redirigé vers la page de connexion
      // L'erreur est silencieuse car c'est attendu si l'utilisateur n'est pas connecté
    } finally {
      if (mounted) {
        setState(() {
          _isInitializing = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isInitializing) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Consumer<AuthProvider>(
      builder: (context, authProvider, _) {
        if (authProvider.isAuthenticated) {
          return const HomePage();
        }
        return const LoginPage();
      },
    );
  }
}
