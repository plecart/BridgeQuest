---
name: bridgequest-flutter
description: Standards spécifiques au client Flutter de Bridge Quest. Structure projet MVP (core/data/presentation), WebSocket deux canaux (lobby + game) avec JWT auth, navigation Lobby→Deployment→Game→Results, gestion erreurs API avec serverMessage prioritaire, modèles spécifiques (LobbyPlayer, GameSettings, GamePlayerRole, GameScoreEntry), widgets réutilisables (ConnectingIndicator, ErrorStateView). Utiliser pour tout développement sur bridgequest-app.
---

# Bridge Quest — Standards Flutter

Ce skill complète `flutter-coding-standards` (standards généraux) avec les conventions spécifiques au projet Bridge Quest.

## Structure Projet (MVP par couche)

```
lib/
├── core/
│   ├── config/               # app_config, api_config
│   ├── constants/
│   │   └── game_constants.dart  # GameState, PlayerRole
│   ├── utils/
│   │   ├── logger.dart
│   │   ├── error_translator.dart     # Codes erreur → i18n
│   │   ├── countdown_controller.dart # Timer réutilisable
│   │   └── websocket_helper.dart     # Imports conditionnels
│   └── exceptions/app_exceptions.dart
├── data/
│   ├── models/game/          # LobbyPlayer, GameSettings, GamePlayerRole, GameScoreEntry
│   ├── repositories/         # auth, game, position
│   └── services/             # api, lobby_ws, game_ws, location, google_sign_in
├── presentation/
│   ├── pages/
│   │   ├── auth/login_page + login_view_model
│   │   ├── menu/main_menu_page + view_model
│   │   ├── lobby/lobby_page + view_model + widgets/
│   │   ├── deployment/deployment_page + view_model
│   │   ├── game/game_page + game_view_model
│   │   └── results/results_page (StatelessWidget, pas de VM)
│   ├── widgets/              # ConnectingIndicator, ErrorStateView
│   └── theme/
├── i18n/                     # Fichiers ARB (fr, en)
└── providers/                # Providers globaux
```

## Gestion Erreurs API

`ApiException` contient `serverMessage` (message backend déjà traduit, prioritaire pour l'affichage).

```dart
class GameException extends AppException {
  final String? serverMessage;
  GameException(String message, {String? code, this.serverMessage})
      : super(message, code: code);
}
```

Dans le repository, préserver `serverMessage` :

```dart
} on ApiException catch (e) {
  throw GameException('API error', code: e.code ?? 'error.generic', serverMessage: e.serverMessage);
}
```

**Erreurs de validation DRF** : `ApiService._extractServerErrorMessage` gère `{"error": "..."}` et `{"field": ["msg"]}`.

## API & Dio Interceptors

- `ApiService` intercepte les erreurs HTTP → `ApiException(code: 'error.api.generic')`
- Pour les 401/403, le **repository** force le code spécifique basé sur `statusCode`
- **Retry** : propager l'erreur du retry via `handler.reject(retryError)`, pas l'erreur d'origine

## WebSocket

Deux canaux avec auth JWT. Voir [references/websocket-implementation.md](references/websocket-implementation.md) pour les détails.

| Canal | Phase | Service | Événements clés |
|-------|-------|---------|----------------|
| Lobby | WAITING | `LobbyWebSocketService` | `player_joined`, `game_started`, `settings_updated` |
| Game | DEPLOYMENT→FINISHED | `GameWebSocketService` | `roles_assigned`, `game_in_progress`, `game_finished`, `position_updated` |

**Auth** : `createWebSocketChannel` via imports conditionnels — headers sur mobile/desktop, query string sur web.

## Navigation

Voir [references/game-flow.md](references/game-flow.md) pour les détails.

```
LoginPage → HomePage → LobbyPage → DeploymentPage → GamePage → ResultsPage → HomePage
            (menu)    (pushReplace) (pushReplace)   (pushReplace)(pushAndRemoveUntil)
```

- `PopScope(canPop: false)` sur Deployment, Game, Results
- Transitions déclenchées par événements WS (pas depuis REST)
- DeploymentPage conserve la connexion WS lors de la navigation vers GamePage (`disposeResources(keepConnection: true)`)
- GamePage reprend la connexion via `setEventHandler` (pas de reconnexion)

## Modèles Spécifiques

| Modèle | Fichier | Contenu |
|--------|---------|---------|
| `LobbyPlayer` | `data/models/game/lobby_player.dart` | player_id, user_id, username, is_admin |
| `GameSettings` | `data/models/game/game_settings.dart` | Immutable, `fromJson`, `copyWith`, `==`, `hashCode` |
| `GamePlayerRole` | `data/models/game/game_player_role.dart` | playerId, userId, username, role. Getters `isSpirit`/`isHuman` |
| `GameScoreEntry` | `data/models/game/game_score_entry.dart` | playerId, userId, username, role, score. Triée par score desc. |

Constantes : `GameState` (waiting, deployment, inProgress, finished), `PlayerRole` (human, spirit) dans `core/constants/game_constants.dart`.

## Widgets Réutilisables

- **`ConnectingIndicator`** : indicateur de chargement centré avec message configurable
- **`ErrorStateView`** : vue d'erreur centrée avec icône, message traduit (`ErrorTranslator`) et bouton retry. Paramètres : `errorKey`, `retryLabel`, `onRetry`

## Validation Client

Correspondre exactement aux contraintes backend :

| Type champ | Contrainte | Backend |
|------------|-----------|---------|
| Durées | `>= 1` | `MinValueValidator(1)` |
| Points par minute | `>= 1` | `MinValueValidator(1)` |
| Pourcentages | `0-100` | `MinValueValidator(0)` + `MaxValueValidator(100)` |

## Données Temps Réel

- **WebSocket push** plutôt que polling
- REST uniquement pour chargement initial ou resynchronisation après coupure
- Ne pas utiliser `Future.delayed` + boucle ou `Timer.periodic` pour fetch périodique

## Checklist Nouvelle Fonctionnalité

- [ ] Clés i18n dans fichiers `.arb` (fr + en)
- [ ] Modèle `fromJson`/`toJson` dans `data/models/`
- [ ] Repository dans `data/repositories/`
- [ ] ViewModel (ChangeNotifier) avec clés d'erreur (pas messages traduits)
- [ ] Page déléguant au ViewModel
- [ ] Widgets réutilisables extraits
- [ ] Un fichier = une responsabilité
- [ ] Tests unitaires + widget
- [ ] `dart analyze` sans erreur
- [ ] `dart format .`
