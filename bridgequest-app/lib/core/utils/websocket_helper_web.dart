// Implémentation web. Pas d'import dart:io (non disponible sur web).
//
// Limitation navigateur : les WebSockets natifs ne permettent pas d'envoyer
// des headers personnalisés. Le token doit être passé dans la query string,
// ce qui l'expose dans les logs (risque d'usurpation si accès aux logs).
// Mitigations et recommandations détaillées dans websocket_helper.dart.

import 'package:web_socket_channel/web_socket_channel.dart';

/// Implémentation pour Flutter Web.
/// Le token est passé en query string (limitation des navigateurs).
WebSocketChannel createWebSocketChannel({
  required String url,
  required String accessToken,
}) {
  final urlWithToken =
      '$url?token=${Uri.encodeQueryComponent(accessToken)}';
  return WebSocketChannel.connect(Uri.parse(urlWithToken));
}
