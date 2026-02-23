---
name: bridgequest-django
description: Standards spécifiques au backend Django de Bridge Quest. Système d'exceptions BridgeQuestException avec message_key (sans gettext_lazy), i18n via utils/messages.py (Messages, ModelMessages, ErrorMessages), format de réponse API standardisé, architecture WebSocket deux canaux (lobby + game), cycle de vie des parties (WAITING→DEPLOYMENT→IN_PROGRESS→FINISHED), scoring deux phases, configuration production fail-fast. Utiliser pour tout développement sur bridgequest-server.
---

# Bridge Quest — Standards Backend Django

Ce skill complète `django-coding-standards` (standards généraux) avec les conventions spécifiques au projet Bridge Quest.

## Système d'Exceptions

Toutes les exceptions métier héritent de `BridgeQuestException` (`utils/exceptions.py`).

**Règle critique :** Passer la clé via `message_key`, **sans appeler `_()`**. La traduction est effectuée en interne. Une double traduction casse l'i18n.

```python
# ✅ BON
raise GameException(message_key=ErrorMessages.GAME_NOT_FOUND)

# ❌ MAUVAIS : double traduction
raise GameException(_(ErrorMessages.GAME_NOT_FOUND))
```

Sous-classes : `GameException`, `PlayerException`, `InteractionException`.

## i18n — Implémentation Spécifique

### Fichier centralisé : `utils/messages.py`

Toutes les clés organisées en classes : `Messages`, `ModelMessages`, `ErrorMessages`.

Format des clés : `"category.subcategory.key"` (ex: `"error.game.not_found"`).

```python
from django.utils.translation import gettext_lazy as _
from utils.messages import ModelMessages

class Game(models.Model):
    code = models.CharField(verbose_name=_(ModelMessages.GAME_CODE))
    class Meta:
        verbose_name = _(ModelMessages.GAME_VERBOSE_NAME)
```

### Ajouter une nouvelle clé

1. Ajouter dans `utils/messages.py`
2. Utiliser avec `_(Messages.KEY)` (sauf exceptions → `message_key`)
3. `makemessages -l fr && makemessages -l en`
4. Traduire dans `.po`
5. `compilemessages`

## Serializers

### Validation métier obligatoire

Les serializers doivent valider les bornes métier, pas seulement les contraintes modèle :

```python
game_duration = serializers.IntegerField(
    validators=[MinValueValidator(1, message=_(ErrorMessages.SETTINGS_GAME_DURATION_TOO_LOW))],
)
spirit_percentage = serializers.IntegerField(
    validators=[
        MinValueValidator(0, message=_(ErrorMessages.SETTINGS_SPIRIT_PERCENTAGE_OUT_OF_RANGE)),
        MaxValueValidator(100, message=_(ErrorMessages.SETTINGS_SPIRIT_PERCENTAGE_OUT_OF_RANGE)),
    ],
)
```

`gettext_lazy` dans `message=` est correct : le proxy lazy est évalué pendant la requête.

### Serializers imbriqués

Service → `select_related("relation")`. Tests → vérifier tous les champs imbriqués.

### Accès OneToOne sans backfill

Utiliser une fonction helper qui gère `DoesNotExist` → exception métier (404) :

```python
def get_game_settings(game):
    try:
        return game.settings
    except GameSettings.DoesNotExist:
        raise GameException(message_key=ErrorMessages.SETTINGS_NOT_FOUND, status_code=404)
```

## Format de Réponse API

```python
# Succès : données du serializer directement
{"id": 1, "code": "ABC123", "state": "WAITING"}

# Erreur métier
{"error": "Message traduit"}

# Erreurs de validation (format DRF)
{"field1": ["Message pour field1."], "field2": ["Message pour field2."]}
```

Retourner **toutes** les erreurs de validation (`validation_error_response(serializer)` de `utils/responses`).

## Utilitaires (`utils/`)

| Fichier | Rôle |
|---------|------|
| `messages.py` | Clés de traduction centralisées |
| `exceptions.py` | Hiérarchie BridgeQuestException |
| `validators.py` | Validateurs réutilisables avec `gettext_lazy` |
| `permissions.py` | Permissions DRF personnalisées |
| `responses.py` | `validation_error_response` |
| `middleware.py` | `AccessLogMiddleware` (redaction tokens) |

## Configuration Production

**Fail-fast** : si `REDIS_URL` manque en production, lever `ValueError` (pas de fallback vers InMemoryChannelLayer).

**Cache partagé** : `CACHES` avec Redis (aligné sur `REDIS_URL`) requis pour état partagé (`lobby_service`).

## WebSocket & Temps Réel

Deux canaux distincts. Voir [references/websocket-architecture.md](references/websocket-architecture.md) pour les détails.

| Canal | URL | Phase | Événements clés |
|-------|-----|-------|----------------|
| Lobby | `ws/lobby/{game_id}/` | WAITING | `player_joined`, `player_left`, `game_started`, `settings_updated` |
| Game | `ws/game/{game_id}/` | DEPLOYMENT, IN_PROGRESS, FINISHED | `roles_assigned`, `game_in_progress`, `game_finished`, `position_updated` |

Auth : Session Django (web) ou JWT header/query string. Codes fermeture : 4001/4002/4003.

## Cycle de Vie & Scoring

Machine à états et scoring deux phases. Voir [references/lifecycle-scoring.md](references/lifecycle-scoring.md) pour les détails.

| Transition | Déclencheur | Service |
|---|---|---|
| WAITING → DEPLOYMENT | Admin POST `start/` | `lifecycle_service.begin_deployment` |
| DEPLOYMENT → IN_PROGRESS | Timer `deployment_ends_at` | `lifecycle_service.begin_in_progress` |
| IN_PROGRESS → FINISHED | Timer `game_ends_at` ou plus d'Humains | `lifecycle_service.finish_game` |

Pré-conditions lancement : minimum 2 joueurs, demandeur = admin.

Scoring : points passifs déploiement (tous) + points passifs IN_PROGRESS (Humains, arrêt à `converted_at`).

## Checklist Nouvelle Fonctionnalité

- [ ] Clés dans `utils/messages.py`
- [ ] Modèle avec i18n (`_(ModelMessages.*)`)
- [ ] Service avec logique métier (exceptions via `message_key`)
- [ ] Serializer avec validation métier
- [ ] View mince déléguant au service
- [ ] URLs nommées
- [ ] Tests (models, services, views)
- [ ] Migrations nommées
- [ ] Traductions `.po` mises à jour
- [ ] Docstrings
