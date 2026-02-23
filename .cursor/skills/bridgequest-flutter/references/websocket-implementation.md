# Bridge Quest — Implémentation WebSocket (Flutter)

## Authentification Sécurisée

**`core/utils/websocket_helper.dart`** — fichier principal avec imports conditionnels :

```dart
import 'websocket_helper_io.dart'
    if (dart.library.html) 'websocket_helper_web.dart' as impl;

WebSocketChannel createWebSocketChannel({...}) => impl.createWebSocketChannel(...);
```

**Mobile + Desktop** (`websocket_helper_io.dart`) :
```dart
import 'package:web_socket_channel/io.dart';
return IOWebSocketChannel.connect(
  Uri.parse(url),
  headers: {'Authorization': 'Bearer $accessToken'},
);
```

**Web** (`websocket_helper_web.dart`) :
```dart
final urlWithToken = '$url?token=${Uri.encodeQueryComponent(accessToken)}';
return WebSocketChannel.connect(Uri.parse(urlWithToken));
```

**Rappel** : `dart:io` n'est PAS disponible sur Flutter Web — ne jamais l'importer dans un fichier compilé pour le web.

## Lobby WebSocket Service

`data/services/lobby_websocket_service.dart` :
- Connexion via `createWebSocketChannel`
- Dispatch des événements via callback
- Événements : `connected`, `player_joined`, `player_left`, `player_excluded`, `admin_transferred`, `game_deleted`, `game_started`, `settings_updated`

## Game WebSocket Service

`data/services/game_websocket_service.dart` :
- Connexion via `createWebSocketChannel` + `ApiConfig.gameWebSocketUrl`
- Handler stocké en champ (`_onEvent`), changeable via `setEventHandler(onEvent)` sans reconnecter
- **Pas de reconnexion automatique** — `ErrorStateView` + retry manuel
- Sealed class `GameEvent` avec sous-classes :
  - `GameConnectedEvent`
  - `GameRolesAssignedEvent`
  - `GameInProgressEvent`
  - `GameFinishedEvent`
  - `GamePositionUpdatedEvent`
  - `GameErrorEvent`

## Codes de Fermeture

- `4001` : non authentifié
- `4002` : non dans la partie
- `4003` : mauvais canal ou phase

## Mitigations Sécurité (Web)

Tokens dans l'URL exposés dans logs, historique navigateur, headers Referer.

Mitigations :
1. HTTPS obligatoire en production
2. Backend redacte tokens dans les logs (`AccessLogMiddleware`)
3. Tokens à courte durée de vie (15 min)
4. Préférer sessions Django pour le web si possible
5. Configurer nginx pour ne pas logger les query strings `token=`

## Récupération d'État

Si le client a manqué `game_started` :
1. `GET /api/games/{id}/` pour vérifier `state`
2. Si WAITING → connecter au lobby
3. Si DEPLOYMENT/IN_PROGRESS → connecter au game
