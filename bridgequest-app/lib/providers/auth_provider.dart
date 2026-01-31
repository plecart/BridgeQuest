import 'package:flutter/foundation.dart';
import '../data/repositories/auth_repository.dart';
import '../data/models/user.dart';
import '../core/exceptions/app_exceptions.dart';

/// Provider pour l'authentification
class AuthProvider extends ChangeNotifier {
  final AuthRepository _authRepository;

  User? _user;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _errorMessage;

  User? get user => _user;
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  AuthProvider({required AuthRepository authRepository})
      : _authRepository = authRepository;

  /// Connexion via SSO
  Future<void> loginWithSSO({
    required String provider,
    required String token,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      _user = await _authRepository.loginWithSSO(
        provider: provider,
        token: token,
      );
      _isAuthenticated = true;
      notifyListeners();
    } catch (e) {
      _setErrorFromException(e);
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  /// Déconnexion
  Future<void> logout() async {
    _setLoading(true);
    try {
      await _authRepository.logout();
      _resetAuthState();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  /// Vérifie si l'utilisateur est déjà connecté
  Future<void> checkAuthStatus() async {
    _setLoading(true);
    try {
      _user = await _authRepository.getCurrentUser();
      _isAuthenticated = true;
      notifyListeners();
    } catch (e) {
      _resetAuthState();
    } finally {
      _setLoading(false);
    }
  }

  /// Réinitialise l'état d'authentification
  void _resetAuthState() {
    _user = null;
    _isAuthenticated = false;
    _errorMessage = null;
  }

  /// Met à jour l'état de chargement
  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  /// Définit un message d'erreur à partir d'une exception
  /// 
  /// Stocke le code de traduction (pas le message traduit) pour permettre
  /// la traduction dans la couche de présentation selon la locale.
  void _setErrorFromException(dynamic exception) {
    if (exception is AppException) {
      // Stocker le code de traduction si disponible, sinon le message
      _errorMessage = exception.code ?? exception.message;
    } else {
      _errorMessage = 'error.generic';
    }
    notifyListeners();
  }

  /// Efface le message d'erreur
  void _clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
