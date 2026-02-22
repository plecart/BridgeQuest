// Implémentation web. Pas d'import dart:io (non disponible sur web).
//
// SÉCURITÉ — Token en query string :
// Les navigateurs ne permettent pas d'envoyer des headers personnalisés sur WebSocket.
// Le token JWT doit être passé en query string (?token=xxx), ce qui l'expose dans
// les logs. Mitigations : HTTPS, AccessLogMiddleware (utils/middleware.py), tokens
// courts. Détails : CODING_STANDARDS_FLUTTER.md « Authentification WebSocket sécurisée ».

import 'package:web_socket_channel/web_socket_channel.dart';

/// Connexion WebSocket pour Flutter Web (token en query string).
WebSocketChannel createWebSocketChannel({
  required String url,
  required String accessToken,
}) {
  final urlWithToken = '$url?token=${Uri.encodeQueryComponent(accessToken)}';
  return WebSocketChannel.connect(Uri.parse(urlWithToken));
}
