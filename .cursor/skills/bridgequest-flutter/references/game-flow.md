# Bridge Quest — Navigation & Pages (Flutter)

## Flux de Navigation

```
LoginPage → HomePage (menu) → LobbyPage → DeploymentPage → GamePage → ResultsPage → HomePage
```

Toutes les navigations entre phases utilisent `pushReplacement`. ResultsPage → HomePage utilise `pushAndRemoveUntil`.

## LobbyPage (Salle d'attente)

- **ViewModel** : charge joueurs via REST (`getGamePlayers`), settings via REST (`getSettings`), connecte au WebSocket lobby
- Maintient la liste de joueurs en temps réel
- Expose `settings`, `isUpdatingSettings`, `updateSetting(key, value)`
- `navigationResult` : `LobbyNavigateToGame` (avec `deploymentEndsAt`) ou `LobbyNavigateToMenu`
- Navigation déclenchée par événement WS `game_started` (pas depuis REST `startGame`)
- Utilise `ConnectingIndicator` et `ErrorStateView`

### LobbySettingsCard

- Admin : champs éditables (`TextFormField`, validation numérique, soumission au blur/enter)
- Non-admin : lecture seule (label + valeur)
- Mise à jour temps réel via WS `settings_updated`

## DeploymentPage (Phase déploiement)

- **ViewModel** : connecte au canal game WS, gère countdown (`deploymentEndsAt` → `remainingTime`), stocke rôles (`roles_assigned`) et `currentPlayerId` (`connected`), déclenche navigation vers GamePage (`game_in_progress`)
- `disposeResources(keepConnection: true)` conserve la connexion WS lors de la navigation forward
- `PopScope(canPop: false)` empêche le retour arrière
- Affiche countdown mm:ss avec `FontFeature.tabularFigures`, message d'instruction, bannière rôles
- Navigation sealed class : `DeploymentNavigateToGame` (gameId, gameEndsAt, roles, currentPlayerId) ou `DeploymentNavigateToMenu`

## GamePage (Partie en cours)

- **ViewModel** : reprend connexion WS via `setEventHandler` (pas de reconnexion), gère countdown (`gameEndsAt` → `remainingTime`), identifie rôle via `currentPlayerId` dans `roles`
- `game_finished` → navigation vers ResultsPage
- `position_updated` → placeholder carte future
- `PopScope(canPop: false)`
- Affiche countdown, carte de rôle (couleur Humain/Esprit), liste joueurs avec rôles
- Sealed class : `GameNavigateToResults` (gameId, scores) ou `GameNavigateToMenu`

## ResultsPage (Résultats)

- **StatelessWidget** (pas de ViewModel) — reçoit `gameId` et `scores` (List<GameScoreEntry>)
- Podium top 3 (or/argent/bronze)
- Classement complet à partir du 4e
- Rôle de chaque joueur (Humain/Esprit coloré)
- Bouton "Retour au menu" (`pushAndRemoveUntil` vers `HomePage`)
- `PopScope(canPop: false)`

## Positions (Géolocalisation)

- **Mise à jour** : `POST /api/locations/` avec `{game_id, latitude, longitude}`
- **Réception temps réel** : événement `position_updated` sur canal game
- **Chargement initial** : `GET /api/games/{id}/positions/`
- Ne PAS utiliser de fetch périodique

## API Config

- `ApiConfig.gameSettings(id)` : GET/PATCH settings
- `ApiConfig.gameWebSocketUrl(gameId)` : URL WS game (sans token dans l'URL)
- `ApiConfig.gamesCreate`, `gamesJoin`, `gamesPlayers(id)`, `gamesStart(id)`
