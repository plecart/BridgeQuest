import 'dart:io' show Platform;

import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// Crée une connexion WebSocket avec authentification sécurisée.
///
/// Sur mobile (Android/iOS), utilise le header `Authorization: Bearer <token>`
/// pour éviter l'exposition du token dans les logs. Sur web, utilise le query
/// string comme fallback car les navigateurs ne permettent pas les headers
/// personnalisés pour les WebSockets.
///
/// **⚠️ RISQUE DE SÉCURITÉ SUR WEB :**
/// Les tokens JWT dans l'URL sont exposés dans :
/// - Les logs de serveur/reverse-proxy
/// - Les outils de monitoring
/// - L'historique du navigateur
/// - Les headers Referer lors de navigation vers d'autres sites
///
/// **MITIGATIONS :**
/// - Utiliser HTTPS en production (les tokens sont moins exposés avec HTTPS)
/// - Configurer le serveur pour ne pas logger les query strings contenant `token=`
/// - Utiliser des tokens à courte durée de vie (access tokens)
/// - Envisager l'utilisation de sessions Django (cookies) pour le web au lieu de JWT
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
    // ⚠️ LIMITATION WEB : Les navigateurs ne permettent pas d'envoyer des headers
    // personnalisés lors de la connexion WebSocket. Le token doit être passé
    // dans la query string, ce qui l'expose dans les logs.
    //
    // Le backend accepte les deux méthodes (header en priorité, query string
    // en fallback) pour la compatibilité. Sur mobile, toujours utiliser les
    // headers pour éviter l'exposition.
    final urlWithToken = '$url?token=${Uri.encodeQueryComponent(accessToken)}';
    return WebSocketChannel.connect(Uri.parse(urlWithToken));
  }
}
