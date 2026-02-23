import 'package:flutter/material.dart';

import '../../../../data/models/game/game_player_role.dart';
import '../../../../data/models/game/player_position.dart';

/// Marker d'un joueur sur la carte.
///
/// Affiche un avatar circulaire avec l'initiale du joueur et son nom.
/// Si [showRoles] est `true` (joueur courant = Esprit), affiche aussi
/// le rôle avec un code couleur. Sinon, affichage neutre pour tous.
///
/// Le joueur courant est mis en avant avec une bordure dorée.
class PlayerMarkerWidget extends StatelessWidget {
  const PlayerMarkerWidget({
    super.key,
    required this.position,
    required this.isCurrentPlayer,
    required this.showRoles,
    this.role,
    this.currentPlayerLabel,
  });

  final PlayerPosition position;
  final bool isCurrentPlayer;
  final bool showRoles;
  final GamePlayerRole? role;
  final String? currentPlayerLabel;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final displayName = isCurrentPlayer
        ? (currentPlayerLabel ?? position.username)
        : position.username;
    final initial =
        (displayName.isNotEmpty ? displayName[0] : '?').toUpperCase();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildAvatar(theme, initial),
        const SizedBox(height: 2),
        _buildLabel(theme, displayName),
      ],
    );
  }

  Widget _buildAvatar(ThemeData theme, String initial) {
    final isSpirit = role?.isSpirit ?? false;
    final avatarColor = _resolveAvatarColor(theme, isSpirit);
    final textColor = _resolveTextColor(theme, isSpirit);

    return Container(
      decoration: isCurrentPlayer
          ? BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: Colors.amber, width: 3),
            )
          : null,
      child: CircleAvatar(
        radius: isCurrentPlayer ? 18 : 14,
        backgroundColor: avatarColor,
        child: Text(
          initial,
          style: TextStyle(
            color: textColor,
            fontWeight: FontWeight.bold,
            fontSize: isCurrentPlayer ? 16 : 12,
          ),
        ),
      ),
    );
  }

  Widget _buildLabel(ThemeData theme, String displayName) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface.withValues(alpha: 0.85),
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.15),
            blurRadius: 2,
          ),
        ],
      ),
      child: Text(
        displayName,
        style: theme.textTheme.labelSmall?.copyWith(
          fontWeight: isCurrentPlayer ? FontWeight.bold : FontWeight.normal,
        ),
        overflow: TextOverflow.ellipsis,
      ),
    );
  }

  Color _resolveAvatarColor(ThemeData theme, bool isSpirit) {
    if (!showRoles) return theme.colorScheme.primaryContainer;
    return isSpirit
        ? theme.colorScheme.errorContainer
        : theme.colorScheme.primaryContainer;
  }

  Color _resolveTextColor(ThemeData theme, bool isSpirit) {
    if (!showRoles) return theme.colorScheme.onPrimaryContainer;
    return isSpirit
        ? theme.colorScheme.onErrorContainer
        : theme.colorScheme.onPrimaryContainer;
  }
}
