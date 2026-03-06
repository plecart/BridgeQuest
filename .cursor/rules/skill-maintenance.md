---
description: Mise à jour automatique des skills avec les standards de code ET les connaissances projet acquises au fil des échanges.
globs:
alwaysApply: true
---

# Maintenance des Skills

## Quand mettre à jour

### Standards et patterns de code
Lorsqu'un nouveau pattern, convention ou standard est établi pendant le développement (nouveau sujet abordé, leçon apprise, correction d'un anti-pattern), mettre à jour le skill approprié.

### Connaissances projet
Lorsque de nouvelles informations sur le projet sont communiquées ou décidées pendant un échange (règles métier, mécaniques de jeu, décisions d'architecture, règles de visibilité, choix techniques), les documenter dans le skill approprié. Ces connaissances constituent la mémoire persistante du projet entre les conversations.

## Où mettre à jour

| Type de pattern | Emplacement |
|----------------|-------------|
| Pattern Django général (réutilisable tous projets) | `~/.cursor/skills/django-coding-standards/` |
| Pattern Flutter général (réutilisable tous projets) | `~/.cursor/skills/flutter-coding-standards/` |
| Convention spécifique Bridge Quest backend | `.cursor/skills/bridgequest-django/` |
| Convention spécifique Bridge Quest Flutter | `.cursor/skills/bridgequest-flutter/` |

## Comment mettre à jour

1. Identifier si le pattern est **général** (applicable à tout projet Django/Flutter) ou **spécifique** (lié à l'architecture/modèles Bridge Quest)
2. Ajouter la nouvelle convention dans la section appropriée du `SKILL.md` ou dans un fichier `references/`
3. Garder le `SKILL.md` sous 500 lignes — déplacer les détails vers `references/` si nécessaire
4. Utiliser le format impératif, être concis (l'agent est intelligent — ne documenter que ce qui n'est pas évident)
5. Inclure un exemple concret BON/MAUVAIS si le pattern est contre-intuitif

## Quand NE PAS mettre à jour

- Détails d'implémentation spécifiques à une feature (pas un standard)
- Informations temporaires ou spécifiques à un sprint
- Code qui parle de lui-même sans convention particulière
- Informations déjà documentées ailleurs (éviter la duplication)
