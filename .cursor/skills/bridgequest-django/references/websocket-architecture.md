# Bridge Quest — Architecture WebSocket (Backend)

## Deux Canaux Distincts

### Lobby (`ws/lobby/{game_id}/`)

Phase WAITING uniquement. Connexion en salle d'attente.

**Événements :**
- `connected` : connexion établie (`game_id`, `player`)
- `player_joined` : un joueur a rejoint
- `player_left` : un joueur a quitté (déconnexion WS — peut se reconnecter sous 30s)
- `player_excluded` : joueur exclu après 30s sans reconnexion
- `admin_transferred` : admin exclu, droits transférés au plus ancien
- `game_deleted` : partie supprimée (admin exclu seul)
- `game_started` : partie lancée (`state: DEPLOYMENT`, `deployment_ends_at`)
- `settings_updated` : admin a modifié les paramètres

### Game (`ws/game/{game_id}/`)

Phases DEPLOYMENT, IN_PROGRESS, FINISHED.

**Événements :**
- `connected` : connexion établie (`game_id`, `player`)
- `roles_assigned` : rôles attribués (Map playerId → role)
- `game_in_progress` : partie en cours (`game_ends_at`)
- `game_finished` : scores finaux et classement
- `position_updated` : (player_id, user, latitude, longitude, recorded_at)

## Authentification

- **Session Django** (cookies) : clients web
- **JWT** : clients mobile/desktop, via header `Authorization: Bearer <token>` (priorité) ou query string `?token=` (fallback web)
- `JWTAuthMiddleware` (`accounts/websocket_auth.py`) accepte les deux méthodes

## Sécurité

- `AccessLogMiddleware` redacte `?token=xxx` → `?token=***`
- HTTPS obligatoire en production
- Tokens à courte durée de vie (15 min)
- Paramètres redactés : `token`, `jwt`, `access_token`, `refresh_token`, `api_key`, `key`, `secret`

## Codes de Fermeture

- `4001` : non authentifié
- `4002` : non dans la partie
- `4003` : mauvais canal ou phase

## Services de Diffusion

- `games/services/lobby_broadcast.py` : `broadcast_game_started`, `broadcast_player_excluded`, `broadcast_admin_transferred`, `broadcast_game_deleted`, `broadcast_settings_updated`
- `games/services/game_broadcast.py` : `broadcast_position_updated`, `broadcast_roles_assigned`, `broadcast_game_in_progress`, `broadcast_game_finished`

## Gestion des Déconnexions (Salle d'attente)

- Délai 30 secondes avant exclusion (reconnexion possible)
- Après 30s : exclusion + diffusion `player_excluded`
- Si exclu était admin : transfert au plus ancien (`admin_transferred`) ou suppression partie (`game_deleted`)
- Service : `games/services/lobby_service.py`

## Flux Client

1. En salle d'attente → lobby
2. À `game_started` : déconnexion lobby → connexion game
3. À `game_deleted` : quitter le lobby
4. Si partie déjà en cours à l'ouverture : connexion directe au game
5. Récupération d'état : `GET /api/games/{id}/` pour vérifier `state`
