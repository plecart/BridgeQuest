import 'dart:io' show Platform;

import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// Crée une connexion WebSocket avec authentification sécurisée.
///
/// Sur mobile (Android/iOS), utilise le header `Authorization: Bearer <token>`
/// pour éviter l'exposition du token dans les logs. Sur web, utilise le query
/// string comme fallback car les navigateurs ne permettent pas les headers
/// personnalisés.
///
/// Args:
///   url: URL WebSocket (sans token dans l'URL).
///   accessToken: Token JWT pour l'authentification.
///
/// Returns:
///   WebSocketChannel configuré avec l'authentification appropriée.
WebSocketChannel createWebSocketChannel({
  required String url,
  required String accessToken,
}) {
  if (Platform.isAndroid || Platform.isIOS) {
    // Sur mobile : utiliser headers pour éviter l'exposition dans les logs
    return IOWebSocketChannel.connect(
      Uri.parse(url),
      headers: {'Authorization': 'Bearer $accessToken'},
    );
  } else {
    // Fallback pour web : query string (limitation du navigateur)
    final urlWithToken = '$url?token=${Uri.encodeQueryComponent(accessToken)}';
    return WebSocketChannel.connect(Uri.parse(urlWithToken));
  }
}
