import '../../data/models/user.dart';

/// Utilitaires pour la manipulation des données utilisateur
class UserHelpers {
  UserHelpers._();

  /// Obtient les initiales de l'utilisateur
  ///
  /// Retourne les initiales basées sur le prénom/nom ou le username.
  /// Retourne '?' si aucune information n'est disponible.
  static String getInitials(User user) {
    if (user.firstName != null && user.firstName!.isNotEmpty) {
      final firstInitial = user.firstName![0].toUpperCase();
      if (user.lastName != null && user.lastName!.isNotEmpty) {
        return '$firstInitial${user.lastName![0].toUpperCase()}';
      }
      return firstInitial;
    }
    if (user.username.isNotEmpty) {
      return user.username[0].toUpperCase();
    }
    return '?';
  }

  /// Obtient le nom d'affichage de l'utilisateur
  ///
  /// Priorité : Prénom + Nom > Prénom > Username
  static String getDisplayName(User user) {
    if (user.firstName != null && user.lastName != null) {
      if (user.firstName!.isNotEmpty && user.lastName!.isNotEmpty) {
        return '${user.firstName} ${user.lastName}';
      }
    }
    if (user.firstName != null && user.firstName!.isNotEmpty) {
      return user.firstName!;
    }
    return user.username;
  }

  /// Vérifie si l'utilisateur a un avatar valide
  static bool hasAvatar(User user) {
    return user.avatar != null && user.avatar!.isNotEmpty;
  }
}
