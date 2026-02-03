import 'package:flutter/material.dart';

/// Styles de texte réutilisables dans l'application
class AppTextStyles {
  AppTextStyles._();

  /// Style pour le titre principal de la page d'accueil
  static const TextStyle homeTitle = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
  );

  /// Style pour l'email de l'utilisateur
  static TextStyle homeEmail(BuildContext context) {
    return TextStyle(
      fontSize: 16,
      color: Colors.grey[600],
    );
  }

  /// Style pour les initiales de l'avatar
  static const TextStyle avatarInitials = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.bold,
    color: Colors.white,
  );
}
