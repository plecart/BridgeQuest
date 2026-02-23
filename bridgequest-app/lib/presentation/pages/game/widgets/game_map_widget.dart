import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../../data/models/game/game_player_role.dart';
import '../../../../data/models/game/player_position.dart';
import '../../../../i18n/app_localizations.dart';
import 'player_marker_widget.dart';

/// Carte interactive affichant les positions des joueurs.
///
/// Centré sur la position du joueur courant. Les markers sont des
/// widgets Flutter via [flutter_map], permettant des avatars riches.
///
/// Règles de visibilité :
/// - [showRoles] = `true` → le joueur est un Esprit, les rôles sont colorés.
/// - [showRoles] = `false` → le joueur est un Humain, markers neutres.
class GameMapWidget extends StatefulWidget {
  const GameMapWidget({
    super.key,
    required this.positions,
    required this.roles,
    required this.currentPlayerId,
    required this.showRoles,
  });

  final Map<int, PlayerPosition> positions;
  final List<GamePlayerRole> roles;
  final int currentPlayerId;
  final bool showRoles;

  @override
  State<GameMapWidget> createState() => _GameMapWidgetState();
}

class _GameMapWidgetState extends State<GameMapWidget> {
  final MapController _mapController = MapController();
  bool _hasInitialCenter = false;

  static const double _defaultZoom = 16.0;
  static const double _markerWidth = 80.0;
  static const double _markerHeight = 60.0;

  @override
  void didUpdateWidget(GameMapWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    _centerOnFirstPosition();
  }

  @override
  Widget build(BuildContext context) {
    final center = _resolveCenter();
    final l10n = AppLocalizations.of(context)!;

    if (center == null) {
      return Center(
        child: Text(l10n.gameMapLoading),
      );
    }

    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: center,
        initialZoom: _defaultZoom,
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.all,
        ),
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.bridgequest.app',
          maxZoom: 19,
        ),
        MarkerLayer(markers: _buildMarkers(l10n)),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // Centrage carte
  // ---------------------------------------------------------------------------

  LatLng? _resolveCenter() {
    final currentPos = widget.positions[widget.currentPlayerId];
    if (currentPos != null) {
      return LatLng(currentPos.latitude, currentPos.longitude);
    }
    if (widget.positions.isNotEmpty) {
      final first = widget.positions.values.first;
      return LatLng(first.latitude, first.longitude);
    }
    return null;
  }

  void _centerOnFirstPosition() {
    if (_hasInitialCenter) return;
    final center = _resolveCenter();
    if (center == null) return;

    _hasInitialCenter = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _mapController.move(center, _defaultZoom);
    });
  }

  // ---------------------------------------------------------------------------
  // Markers
  // ---------------------------------------------------------------------------

  List<Marker> _buildMarkers(AppLocalizations l10n) {
    return widget.positions.entries.map((entry) {
      final playerId = entry.key;
      final position = entry.value;
      final isCurrentPlayer = playerId == widget.currentPlayerId;
      final role = _findRole(playerId);

      return Marker(
        point: LatLng(position.latitude, position.longitude),
        width: _markerWidth,
        height: _markerHeight,
        child: PlayerMarkerWidget(
          position: position,
          isCurrentPlayer: isCurrentPlayer,
          showRoles: widget.showRoles,
          role: role,
          currentPlayerLabel: isCurrentPlayer ? l10n.gameMapPlayerYou : null,
        ),
      );
    }).toList();
  }

  GamePlayerRole? _findRole(int playerId) {
    for (final r in widget.roles) {
      if (r.playerId == playerId) return r;
    }
    return null;
  }
}
