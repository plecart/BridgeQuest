import 'dart:async';

import 'package:geolocator/geolocator.dart';

import '../../core/utils/logger.dart';

/// Résultat de la vérification des permissions de localisation.
enum LocationPermissionResult {
  granted,
  serviceDisabled,
  permissionDenied,
}

/// Service de géolocalisation encapsulant [Geolocator].
///
/// Gère les permissions et le streaming continu de positions.
/// Cycle de vie explicite : [startTracking] / [stopTracking].
class LocationService {
  StreamSubscription<Position>? _positionSubscription;
  void Function(double latitude, double longitude)? _onPositionChanged;

  /// Distance minimale (en mètres) pour déclencher une mise à jour.
  static const int _distanceFilterMeters = 5;

  bool get isTracking => _positionSubscription != null;

  /// Vérifie et demande les permissions de localisation.
  ///
  /// Retourne un [LocationPermissionResult] indiquant le résultat précis.
  /// Ne lance pas d'exception : le ViewModel décide de l'action à mener.
  Future<LocationPermissionResult> ensurePermission() async {
    if (!await Geolocator.isLocationServiceEnabled()) {
      AppLogger.warning('Location services are disabled');
      return LocationPermissionResult.serviceDisabled;
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }

    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      AppLogger.warning('Location permission denied: $permission');
      return LocationPermissionResult.permissionDenied;
    }

    return LocationPermissionResult.granted;
  }

  /// Démarre le tracking continu de la position.
  ///
  /// [onPositionChanged] est appelé à chaque nouvelle position avec
  /// (latitude, longitude). Ignore les mises à jour sans mouvement
  /// significatif grâce au [_distanceFilterMeters].
  void startTracking({
    required void Function(double latitude, double longitude) onPositionChanged,
  }) {
    stopTracking();
    _onPositionChanged = onPositionChanged;

    AppLogger.debug('Starting location tracking');

    const settings = LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: _distanceFilterMeters,
    );

    _positionSubscription = Geolocator.getPositionStream(
      locationSettings: settings,
    ).listen(
      _handlePositionUpdate,
      onError: _handleError,
    );
  }

  /// Arrête le tracking de position.
  void stopTracking() {
    _positionSubscription?.cancel();
    _positionSubscription = null;
    _onPositionChanged = null;
    AppLogger.debug('Location tracking stopped');
  }

  void _handlePositionUpdate(Position position) {
    _onPositionChanged?.call(position.latitude, position.longitude);
  }

  void _handleError(dynamic error) {
    AppLogger.error('Location stream error', error);
  }
}
