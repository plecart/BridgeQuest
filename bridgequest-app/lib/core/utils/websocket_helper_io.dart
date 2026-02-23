// Implémentation native (Android, iOS, macOS, Windows, Linux).
// Utilise les headers Authorization pour éviter l'exposition du token dans les logs.

import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// Implémentation pour les plateformes natives (mobile + desktop).
/// Les headers personnalisés sont supportés via IOWebSocketChannel.
WebSocketChannel createWebSocketChannel({
  required String url,
  required String accessToken,
}) {
  return IOWebSocketChannel.connect(
    Uri.parse(url),
    headers: {'Authorization': 'Bearer $accessToken'},
  );
}
