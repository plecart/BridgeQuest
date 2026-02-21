import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../data/models/game/game_settings.dart';
import '../../../../i18n/app_localizations.dart';

/// Carte affichant les paramètres de la partie dans le lobby.
///
/// - **Admin** : champs éditables (TextFormField) avec validation.
/// - **Non-admin** : affichage en lecture seule.
class LobbySettingsCard extends StatelessWidget {
  const LobbySettingsCard({
    super.key,
    required this.settings,
    required this.isAdmin,
    required this.isUpdating,
    this.onSettingChanged,
  });

  final GameSettings settings;
  final bool isAdmin;
  final bool isUpdating;

  /// Callback appelé quand l'admin modifie un champ.
  ///
  /// Paramètres : clé JSON (`game_duration`, etc.) et nouvelle valeur.
  final void Function(String key, int value)? onSettingChanged;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.lobbySettingsTitle,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            _buildField(
              context,
              label: l10n.lobbySettingsGameDuration,
              value: settings.gameDuration,
              jsonKey: 'game_duration',
              fieldType: _SettingsFieldType.duration,
            ),
            _buildField(
              context,
              label: l10n.lobbySettingsDeploymentDuration,
              value: settings.deploymentDuration,
              jsonKey: 'deployment_duration',
              fieldType: _SettingsFieldType.duration,
            ),
            _buildField(
              context,
              label: l10n.lobbySettingsSpiritPercentage,
              value: settings.spiritPercentage,
              jsonKey: 'spirit_percentage',
              fieldType: _SettingsFieldType.percentage,
            ),
            _buildField(
              context,
              label: l10n.lobbySettingsPointsPerMinute,
              value: settings.pointsPerMinute,
              jsonKey: 'points_per_minute',
              fieldType: _SettingsFieldType.pointsPerMinute,
            ),
            _buildField(
              context,
              label: l10n.lobbySettingsConversionPercentage,
              value: settings.conversionPointsPercentage,
              jsonKey: 'conversion_points_percentage',
              fieldType: _SettingsFieldType.percentage,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildField(
    BuildContext context, {
    required String label,
    required int value,
    required String jsonKey,
    required _SettingsFieldType fieldType,
  }) {
    if (isAdmin) {
      return _SettingsEditableField(
        label: label,
        value: value,
        enabled: !isUpdating,
        fieldType: fieldType,
        onSubmitted: (newValue) => onSettingChanged?.call(jsonKey, newValue),
      );
    }
    return _SettingsReadOnlyField(label: label, value: value);
  }
}

/// Type de champ pour appliquer la validation appropriée.
enum _SettingsFieldType {
  /// Durées (game_duration, deployment_duration) : minimum 1.
  duration,
  /// Points par minute : minimum 1.
  pointsPerMinute,
  /// Pourcentages (spirit_percentage, conversion_points_percentage) : 0-100.
  percentage,
}

/// Champ éditable pour l'admin (TextFormField avec validation).
class _SettingsEditableField extends StatefulWidget {
  const _SettingsEditableField({
    required this.label,
    required this.value,
    required this.enabled,
    required this.fieldType,
    required this.onSubmitted,
  });

  final String label;
  final int value;
  final bool enabled;
  final _SettingsFieldType fieldType;
  final void Function(int value) onSubmitted;

  @override
  State<_SettingsEditableField> createState() => _SettingsEditableFieldState();
}

class _SettingsEditableFieldState extends State<_SettingsEditableField> {
  late final TextEditingController _controller;
  bool _hasFocus = false;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.value.toString());
  }

  @override
  void didUpdateWidget(covariant _SettingsEditableField oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Synchronise le controller quand la valeur change via WS.
    if (oldWidget.value != widget.value && !_hasFocus) {
      _controller.text = widget.value.toString();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Focus(
        onFocusChange: (focused) {
          _hasFocus = focused;
          if (!focused) _submitIfChanged();
        },
        child: TextFormField(
          controller: _controller,
          enabled: widget.enabled,
          keyboardType: TextInputType.number,
          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
          decoration: InputDecoration(
            labelText: widget.label,
            border: const OutlineInputBorder(),
            isDense: true,
          ),
          onFieldSubmitted: (_) => _submitIfChanged(),
        ),
      ),
    );
  }

  void _submitIfChanged() {
    final text = _controller.text.trim();
    if (text.isEmpty) {
      _restorePreviousValue();
      return;
    }

    final parsed = int.tryParse(text);
    if (parsed == null || !_isValidValue(parsed)) {
      _restorePreviousValue();
      return;
    }

    if (parsed != widget.value) {
      widget.onSubmitted(parsed);
    }
  }

  /// Restaure la valeur précédente dans le champ.
  void _restorePreviousValue() {
    _controller.text = widget.value.toString();
  }

  /// Valide une valeur selon le type de champ pour correspondre aux contraintes backend.
  ///
  /// Retourne true si la valeur est valide selon les règles métier :
  /// - Durées (duration) : minimum 1
  /// - Points par minute (pointsPerMinute) : minimum 1
  /// - Pourcentages (percentage) : 0-100
  bool _isValidValue(int value) {
    switch (widget.fieldType) {
      case _SettingsFieldType.duration:
        return value >= 1;
      case _SettingsFieldType.pointsPerMinute:
        return value >= 1;
      case _SettingsFieldType.percentage:
        return value >= 0 && value <= 100;
    }
  }
}

/// Champ en lecture seule pour les non-admin.
class _SettingsReadOnlyField extends StatelessWidget {
  const _SettingsReadOnlyField({
    required this.label,
    required this.value,
  });

  final String label;
  final int value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
          Text(
            value.toString(),
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
        ],
      ),
    );
  }
}
