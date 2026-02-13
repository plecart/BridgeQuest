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
            ),
            _buildField(
              context,
              label: l10n.lobbySettingsDeploymentDuration,
              value: settings.deploymentDuration,
              jsonKey: 'deployment_duration',
            ),
            _buildField(
              context,
              label: l10n.lobbySettingsSpiritPercentage,
              value: settings.spiritPercentage,
              jsonKey: 'spirit_percentage',
            ),
            _buildField(
              context,
              label: l10n.lobbySettingsPointsPerMinute,
              value: settings.pointsPerMinute,
              jsonKey: 'points_per_minute',
            ),
            _buildField(
              context,
              label: l10n.lobbySettingsConversionPercentage,
              value: settings.conversionPointsPercentage,
              jsonKey: 'conversion_points_percentage',
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
  }) {
    if (isAdmin) {
      return _SettingsEditableField(
        label: label,
        value: value,
        enabled: !isUpdating,
        onSubmitted: (newValue) => onSettingChanged?.call(jsonKey, newValue),
      );
    }
    return _SettingsReadOnlyField(label: label, value: value);
  }
}

/// Champ éditable pour l'admin (TextFormField avec validation).
class _SettingsEditableField extends StatefulWidget {
  const _SettingsEditableField({
    required this.label,
    required this.value,
    required this.enabled,
    required this.onSubmitted,
  });

  final String label;
  final int value;
  final bool enabled;
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
      // Restaure la valeur précédente si le champ est vidé.
      _controller.text = widget.value.toString();
      return;
    }
    final parsed = int.tryParse(text);
    if (parsed == null || parsed < 0) {
      _controller.text = widget.value.toString();
      return;
    }
    if (parsed != widget.value) {
      widget.onSubmitted(parsed);
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
