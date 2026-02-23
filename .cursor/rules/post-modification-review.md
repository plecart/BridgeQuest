---
description: Revue systématique après chaque modification de code. Appliquée automatiquement à la fin de chaque tâche de développement.
globs:
alwaysApply: true
---

# Revue Post-Modification

Après chaque modification de code terminée, effectuer systématiquement les vérifications suivantes sur le code ajouté ou modifié :

## 1. Conformité aux standards

- **Django** : vérifier la conformité avec les skills `django-coding-standards` et `bridgequest-django`
- **Flutter** : vérifier la conformité avec les skills `flutter-coding-standards` et `bridgequest-flutter`

## 2. Qualité du code

- **Supprimer** tout code dupliqué, inutile ou mort
- **Fractionner** les fonctions trop longues (>20 lignes) et découper les responsabilités
- **Réorganiser** et structurer pour un code clair, cohérent et maintenable
- **Vérifier** qu'un fichier = une responsabilité

## 3. Internationalisation

- **Aucun texte brut** dans l'UI : tout passe par `l10n` (Flutter) ou `gettext_lazy` (Django)
- **Clés explicites** : pas de texte français/anglais en dur
- **Logs exclus** : les messages de logging restent en anglais sans i18n

## 4. Vérifications techniques

- **Django** : `python manage.py check`, migrations cohérentes, docstrings
- **Flutter** : `dart analyze` sans erreur, `dart format`, conventions de nommage
- **Tests** : les modifications sont couvertes par des tests

## 5. Mise à jour des skills

Si un nouveau pattern ou standard a été établi pendant le développement, mettre à jour le skill approprié (voir rule `skill-maintenance`).
