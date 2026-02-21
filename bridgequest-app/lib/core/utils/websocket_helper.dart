// Imports conditionnels : IO (mobile + desktop) par défaut, Web en fallback.
// Évite l'import dart:io sur web qui ferait échouer la compilation.

import 'websocket_helper_io.dart'
    if (dart.library.html) 'websocket_helper_web.dart' as impl;

import 'package:web_socket_channel/web_socket_channel.dart';

/// Crée une connexion WebSocket avec authentification.
///
/// **Mobile et desktop** : header `Authorization: Bearer <token>` (évite l'exposition
/// dans les logs).
///
/// **Web** : query string `?token=xxx` (limitation navigateurs). Les tokens en URL
/// sont exposés (logs, historique). Voir CODING_STANDARDS_FLUTTER.md pour risques
/// et mitigations.
WebSocketChannel createWebSocketChannel({
  required String url,
  required String accessToken,
}) {
  return impl.createWebSocketChannel(
    url: url,
    accessToken: accessToken,
  );
}
