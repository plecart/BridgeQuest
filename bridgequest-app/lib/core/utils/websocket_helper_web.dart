// Implémentation web. Pas d'import dart:io (non disponible sur web).
//
// Limitation navigateur : les WebSockets natifs ne permettent pas d'envoyer
// des headers personnalisés. Le token doit être passé dans la query string,
// ce qui l'expose dans les logs (risque d'usurpation si accès aux logs).
// Mitigations : HTTPS obligatoire, backend redacte ?token=xxx, tokens courts,
// reverse-proxy configuré pour ne pas logger les query strings.
// Détails : CODING_STANDARDS_FLUTTER.md section "Authentification WebSocket sécurisée".

import 'package:web_socket_channel/web_socket_channel.dart';

/// Implémentation pour Flutter Web.
/// Token en query string (limitation navigateurs). Cf. en-tête du fichier et
/// CODING_STANDARDS_FLUTTER.md section « Authentification WebSocket sécurisée ».
WebSocketChannel createWebSocketChannel({
  required String url,
  required String accessToken,
}) {
  final urlWithToken =
      '$url?token=${Uri.encodeQueryComponent(accessToken)}';
  return WebSocketChannel.connect(Uri.parse(urlWithToken));
}
