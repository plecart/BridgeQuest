import 'dart:async';

import 'package:flutter/foundation.dart';

/// Contrôleur de compte à rebours réutilisable.
///
/// Gère un timer périodique (1 seconde) qui calcule le temps restant
/// jusqu'à une date cible. Appelle [onTick] à chaque mise à jour
/// pour permettre au ViewModel de notifier ses listeners.
///
/// Utilisé par [DeploymentViewModel] et [GameViewModel] pour éviter
/// la duplication de la logique de countdown.
class CountdownController {
  CountdownController({
    required DateTime targetTime,
    this.onTick,
  }) : _targetTime = targetTime;

  final DateTime _targetTime;

  /// Callback appelé à chaque mise à jour du temps restant.
  ///
  /// Typiquement, le ViewModel y connecte son [ChangeNotifier.notifyListeners].
  VoidCallback? onTick;

  Timer? _timer;
  Duration _remainingTime = Duration.zero;

  /// Temps restant avant la date cible.
  Duration get remainingTime => _remainingTime;

  /// Minutes et secondes formatées du compte à rebours (ex: `02:35`).
  String get countdownText {
    final minutes = _remainingTime.inMinutes;
    final seconds = _remainingTime.inSeconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:'
        '${seconds.toString().padLeft(2, '0')}';
  }

  /// Démarre le compte à rebours (calcul immédiat + tick toutes les secondes).
  void start() {
    _updateRemainingTime();
    _timer?.cancel();
    _timer = Timer.periodic(
      const Duration(seconds: 1),
      (_) => _updateRemainingTime(),
    );
  }

  /// Arrête le timer sans remettre le temps à zéro.
  void stop() {
    _timer?.cancel();
    _timer = null;
  }

  void _updateRemainingTime() {
    final now = DateTime.now();
    final remaining = _targetTime.difference(now);
    _remainingTime = remaining.isNegative ? Duration.zero : remaining;
    onTick?.call();
  }
}
