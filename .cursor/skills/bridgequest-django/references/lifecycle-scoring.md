# Bridge Quest — Cycle de Vie & Scoring (Backend)

## Machine à États

```
WAITING → DEPLOYMENT → IN_PROGRESS → FINISHED
```

### Services

- `games/services/lifecycle_service.py` : orchestration des transitions (`begin_deployment`, `begin_in_progress`, `finish_game`)
- `games/services/lifecycle_worker.py` : thread daemon, sonde la base pour timers expirés
- `games/services/role_service.py` : attribution aléatoire des rôles
- `games/services/score_service.py` : scoring deux phases

### Transitions

| Transition | Déclencheur | Service | Actions |
|---|---|---|---|
| WAITING → DEPLOYMENT | Admin POST `/api/games/{id}/start/` | `begin_deployment` | Vérifie min 2 joueurs + admin, calcule `deployment_ends_at`, broadcast `game_started` |
| DEPLOYMENT → IN_PROGRESS | `deployment_ends_at` atteint | `begin_in_progress` | Attribue rôles, calcule `game_ends_at`, persiste scores déploiement, broadcast `roles_assigned` + `game_in_progress` |
| IN_PROGRESS → FINISHED | `game_ends_at` atteint ou plus d'Humains | `finish_game` | Calcule scores finaux, broadcast `game_finished` |

### Timestamps de fin de phase

- `deployment_ends_at` = `now + deployment_duration` minutes (dans `begin_deployment`)
- `game_ends_at` = `now + game_duration` minutes (dans `begin_in_progress`)
- Le début d'IN_PROGRESS se déduit : `game_ends_at - game_duration`

## Attribution des Rôles

`role_service.assign_roles(game, spirit_percentage)` :
- Sélection aléatoire via `random.sample`, `bulk_update`
- Nombre d'Esprits : `max(1, min(round(N * % / 100), N - 1))` — toujours ≥1 Esprit et ≥1 Humain
- **Aléatoire intentionnel** : pas de seed, non déterministe pour l'équité
- Tests : vérifier les invariants (≥1 Esprit, ≥1 Humain), pas une répartition particulière

## Scoring — Deux Phases

### Phase 1 : Déploiement (tous les joueurs)

`score_service.apply_deployment_scores(game)` — appelé par `begin_in_progress` :
- Tous reçoivent `round(deployment_duration * points_per_minute)`
- Persisté via `bulk_update`

### Phase 2 : IN_PROGRESS (Humains uniquement)

`score_service.calculate_final_scores(game)` — appelé par `finish_game` :

| Type joueur | Calcul points passifs |
|---|---|
| Humain non converti (`role=HUMAN`) | `round(minutes_IN_PROGRESS * points_per_minute)` (durée complète) |
| Humain converti (`role=SPIRIT` + `converted_at`) | Minutes de `game_start` jusqu'à `converted_at` |
| Esprit initial (sans `converted_at`) | 0 point passif |

- **Utiliser `game.game_ends_at`** (pas `timezone.now()`) pour un scoring déterministe
- Vérifier `game.game_ends_at is not None` en début de fonction
- Sauvegarde via `bulk_update(players, ["score"])`
- Payload trié par score décroissant

### Score de conversion (temps réel)

`conversion_points_percentage` % des points de l'Humain converti, appliqué au moment de l'interaction.

## Lifecycle Worker

- Thread daemon dans `games/services/lifecycle_worker.py`
- Démarré par `GamesConfig.ready()` si `LIFECYCLE_AUTO_PROCESS = True`
- Polling 1s, détecte timers expirés
- Ne démarre que pour les processus serveur (pas `migrate`, `test`, `shell`)
- Logger : `bridgequest.lifecycle`
- Management command alternative : `process_lifecycle` (réutilise `tick()`)

## Pré-conditions de Lancement

- Minimum 2 joueurs (`_MIN_PLAYERS_TO_START`)
- Demandeur = admin de la partie
- Vérifié dans `game_service.start_game` → `lifecycle_service.begin_deployment`
