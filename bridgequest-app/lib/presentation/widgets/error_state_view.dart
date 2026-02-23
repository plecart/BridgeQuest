import 'package:flutter/material.dart';

import '../../core/utils/error_translator.dart';
import '../../i18n/app_localizations.dart';

/// Vue d'erreur centrée avec icône, message traduit et bouton de réessai.
///
/// Utilisée dans les pages connectées (lobby, déploiement, game) quand
/// une erreur réseau ou WebSocket empêche le fonctionnement normal.
class ErrorStateView extends StatelessWidget {
  const ErrorStateView({
    super.key,
    required this.errorKey,
    required this.retryLabel,
    required this.onRetry,
  });

  /// Clé d'erreur passée à [ErrorTranslator.translate].
  final String errorKey;

  /// Libellé du bouton de réessai (déjà localisé).
  final String retryLabel;

  /// Callback appelé quand l'utilisateur appuie sur le bouton.
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 48,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              ErrorTranslator.translate(errorKey, l10n),
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Theme.of(context).colorScheme.error,
              ),
            ),
            const SizedBox(height: 24),
            OutlinedButton(
              onPressed: onRetry,
              child: Text(retryLabel),
            ),
          ],
        ),
      ),
    );
  }
}
