import 'package:flutter/material.dart';

/// Indicateur de connexion centré avec un message.
///
/// Utilisé pendant le chargement initial (lobby, déploiement, game).
class ConnectingIndicator extends StatelessWidget {
  const ConnectingIndicator({super.key, required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(message),
        ],
      ),
    );
  }
}
