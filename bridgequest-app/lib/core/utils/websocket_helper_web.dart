// Implémentation web. Pas d'import dart:io (non disponible sur web).
//
// SÉCURITÉ — Token en query string :
// Les WebSockets natifs des navigateurs ne permettent pas d'envoyer des headers
// personnalisés (ex. Authorization). Le token JWT doit donc être passé en query
// string (?token=xxx), ce qui l'expose dans les logs serveur/proxy et l'historique.
// Toute personne ayant accès à ces traces peut rejouer le token et usurper la session.
//
// Mitigations OBLIGATOIRES :
// - HTTPS en production (chiffrement bout en bout)
// - Backend : AccessLogMiddleware redacte ?token=xxx → ?token=***
// - Reverse-proxy (nginx, etc.) : ne jamais logger les query strings contenant token=
// - Tokens à courte durée (ex. 15 min) pour limiter la fenêtre d'usurpation
//
// Alternative future : backend accepterait le token dans un message initial (requiert
// des modifications serveur). Détails : CODING_STANDARDS_FLUTTER.md « Authentification WebSocket ».

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
