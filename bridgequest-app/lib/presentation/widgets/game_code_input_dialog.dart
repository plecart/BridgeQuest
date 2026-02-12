import 'package:flutter/material.dart';

import '../../core/exceptions/app_exceptions.dart';
import '../../i18n/app_localizations.dart';

String _identity(String value) => value;

/// Dialogue de saisie pour rejoindre une partie via son code.
///
/// Affiche un champ texte avec validation et gestion des erreurs API.
class GameCodeInputDialog<T> extends StatefulWidget {
  const GameCodeInputDialog({
    super.key,
    required this.title,
    required this.label,
    required this.submitLabel,
    required this.submit,
    required this.validate,
    this.transformInput = _identity,
    this.textCapitalization = TextCapitalization.words,
  });

  final String title;
  final String label;
  final String submitLabel;
  final Future<T> Function(String value) submit;
  final String? Function(String value) validate;
  final String Function(String value) transformInput;
  final TextCapitalization textCapitalization;

  /// Affiche le dialogue et retourne le résultat ou null si annulé.
  static Future<T?> show<T>({
    required BuildContext context,
    required String title,
    required String label,
    required String submitLabel,
    required Future<T> Function(String value) submit,
    required String? Function(String value) validate,
    String Function(String value) transformInput = _identity,
    TextCapitalization textCapitalization = TextCapitalization.words,
  }) {
    return showDialog<T?>(
      context: context,
      builder: (ctx) => GameCodeInputDialog<T>(
        title: title,
        label: label,
        submitLabel: submitLabel,
        submit: submit,
        validate: validate,
        transformInput: transformInput,
        textCapitalization: textCapitalization,
      ),
    );
  }

  @override
  State<GameCodeInputDialog<T>> createState() => _GameCodeInputDialogState<T>();
}

class _GameCodeInputDialogState<T> extends State<GameCodeInputDialog<T>> {
  late final TextEditingController _controller;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    final l10n = AppLocalizations.of(context)!;
    final raw = _controller.text.trim();
    final value = widget.transformInput(raw);
    final validationError = widget.validate(value);
    if (validationError != null) {
      setState(() => _errorMessage = validationError);
      return;
    }
    try {
      final result = await widget.submit(value);
      if (!mounted) return;
      Navigator.of(context).pop(result);
    } on GameException catch (e) {
      setState(
        () => _errorMessage = e.serverMessage ?? l10n.errorGeneric,
      );
    } catch (e) {
      setState(() => _errorMessage = l10n.errorGeneric);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return AlertDialog(
      title: Text(widget.title),
      content: TextField(
        controller: _controller,
        decoration: InputDecoration(
          labelText: widget.label,
          errorText: _errorMessage,
        ),
        textCapitalization: widget.textCapitalization,
        onChanged: (_) => setState(() => _errorMessage = null),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(l10n.commonDialogCancel),
        ),
        FilledButton(
          onPressed: _handleSubmit,
          child: Text(widget.submitLabel),
        ),
      ],
    );
  }
}
