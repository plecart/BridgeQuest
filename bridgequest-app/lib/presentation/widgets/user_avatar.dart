import 'package:flutter/material.dart';
import '../../data/models/user.dart';
import '../../core/utils/user_helpers.dart';
import '../theme/app_text_styles.dart';

/// Widget réutilisable pour afficher l'avatar d'un utilisateur.
///
/// Affiche l'image de profil si disponible, sinon affiche les initiales
/// dans un cercle coloré. Gère automatiquement les erreurs de chargement
/// d'image en basculant sur l'avatar par défaut.
class UserAvatar extends StatefulWidget {
  /// L'utilisateur dont on affiche l'avatar.
  final User user;

  /// Le rayon de l'avatar (défaut: 30).
  final double radius;

  /// La couleur de fond pour l'avatar par défaut.
  final Color? backgroundColor;

  /// Couleur de fond par défaut si non spécifiée.
  static const Color defaultBackgroundColor = Colors.blue;

  /// Ratio du rayon pour calculer la taille de police des initiales.
  static const double _initialsTextRatio = 0.5;

  const UserAvatar({
    super.key,
    required this.user,
    this.radius = 30,
    this.backgroundColor,
  });

  @override
  State<UserAvatar> createState() => _UserAvatarState();
}

class _UserAvatarState extends State<UserAvatar> {
  bool _hasImageError = false;

  @override
  void didUpdateWidget(UserAvatar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (_avatarChanged(oldWidget)) {
      _resetImageError();
    }
  }

  bool _avatarChanged(UserAvatar oldWidget) {
    return oldWidget.user.avatar != widget.user.avatar;
  }

  void _resetImageError() {
    _hasImageError = false;
  }

  @override
  Widget build(BuildContext context) {
    if (_shouldShowNetworkAvatar()) {
      return _buildNetworkAvatar();
    }
    return _buildDefaultAvatar();
  }

  bool _shouldShowNetworkAvatar() {
    return UserHelpers.hasAvatar(widget.user) && !_hasImageError;
  }

  Color get _effectiveBackgroundColor {
    return widget.backgroundColor ?? UserAvatar.defaultBackgroundColor;
  }

  Widget _buildNetworkAvatar() {
    return CircleAvatar(
      radius: widget.radius,
      backgroundImage: NetworkImage(widget.user.avatar!),
      backgroundColor: _effectiveBackgroundColor,
      onBackgroundImageError: (_, __) => _handleImageError(),
    );
  }

  void _handleImageError() {
    setState(() {
      _hasImageError = true;
    });
  }

  Widget _buildDefaultAvatar() {
    return CircleAvatar(
      radius: widget.radius,
      backgroundColor: _effectiveBackgroundColor,
      child: Text(
        UserHelpers.getInitials(widget.user),
        style: AppTextStyles.avatarInitials.copyWith(
          fontSize: widget.radius * UserAvatar._initialsTextRatio,
        ),
      ),
    );
  }
}
