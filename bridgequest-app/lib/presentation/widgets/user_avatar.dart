import 'package:flutter/material.dart';
import '../../data/models/user.dart';
import '../../core/utils/user_helpers.dart';
import '../theme/app_text_styles.dart';

/// Widget réutilisable pour afficher l'avatar d'un utilisateur
/// 
/// Affiche l'image de profil si disponible, sinon affiche les initiales
/// dans un cercle coloré.
class UserAvatar extends StatelessWidget {
  /// L'utilisateur dont on affiche l'avatar
  final User user;
  
  /// Le rayon de l'avatar
  final double radius;
  
  /// La couleur de fond pour l'avatar par défaut
  final Color? backgroundColor;

  const UserAvatar({
    super.key,
    required this.user,
    this.radius = 30,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    if (UserHelpers.hasAvatar(user)) {
      return _buildNetworkAvatar();
    }
    return _buildDefaultAvatar();
  }

  /// Construit l'avatar avec l'image réseau
  Widget _buildNetworkAvatar() {
    return CircleAvatar(
      radius: radius,
      backgroundImage: NetworkImage(user.avatar!),
      onBackgroundImageError: (_, __) {
        // En cas d'erreur, l'avatar par défaut sera affiché
      },
      child: _buildDefaultAvatar(),
    );
  }

  /// Construit l'avatar par défaut avec les initiales
  Widget _buildDefaultAvatar() {
    final initials = UserHelpers.getInitials(user);
    return CircleAvatar(
      radius: radius,
      backgroundColor: backgroundColor ?? Colors.blue,
      child: Text(
        initials,
        style: AppTextStyles.avatarInitials.copyWith(
          fontSize: radius * 0.5,
        ),
      ),
    );
  }
}
