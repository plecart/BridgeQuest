---
description: Convention de commits Bridge Quest. Appliquée automatiquement lors de la création de commits.
globs:
alwaysApply: true
---

# Convention de Commits

## Format

```
<type>(<scope>): <description>
```

## Types

- `feat` : Nouvelle fonctionnalité
- `fix` : Correction de bug
- `refactor` : Refactorisation sans changement fonctionnel
- `perf` : Amélioration de performance
- `test` : Ajout/modification de tests
- `docs` : Documentation
- `chore` : Maintenance, dépendances, config
- `style` : Formatage (pas de changement de code)
- `build` : Système de build, dépendances externes

## Scopes

### Backend
`auth`, `games`, `players`, `locations`, `interactions`, `powers`, `scores`, `logs`, `api`, `websocket`, `models`, `services`, `serializers`

### Flutter
`ui`, `auth`, `menu`, `lobby`, `game`, `qr`, `profile`, `results`, `widgets`, `services`, `models`, `i18n`, `theme`

### Général
`config`, `deps`, `ci`, `docs`

## Règles

- Messages en **français**
- Impératif présent ("ajouter" pas "ajouté")
- Pas de majuscule en début, pas de point final
- Maximum 72 caractères
- Un commit = une modification logique
- Corps optionnel : expliquer le **pourquoi** (séparé par ligne vide)
- Ne pas committer artefacts de build ou secrets

## Exemples

```
feat(games): ajout du timer serveur pour les transitions d'état
fix(score): correction du calcul des points lors d'une conversion
refactor(services): séparation de la logique métier dans game_service
test(games): tests unitaires pour game_service
chore(deps): mise à jour de Django vers 4.2
```
