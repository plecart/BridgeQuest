# Bridge Quest - Application Mobile Flutter

Application mobile Flutter pour Bridge Quest, un jeu de réalité alternée.

## Structure du Projet

Le projet suit l'architecture définie dans `bridgequest-doc/CODING_STANDARDS_FLUTTER.md` :

- `lib/core/` : Configuration et utilitaires de base
- `lib/data/` : Couche de données (models, repositories, services)
- `lib/presentation/` : Interface utilisateur (pages, widgets, theme)
- `lib/i18n/` : Internationalisation
- `lib/providers/` : State management (Provider)

## Installation

```bash
# Installer les dépendances
flutter pub get

# Générer les fichiers de localisation
flutter gen-l10n

# Lancer l'application
flutter run
```

## Standards de Code

Tous les standards sont définis dans `bridgequest-doc/CODING_STANDARDS_FLUTTER.md`.

## Tests

```bash
# Tests unitaires
flutter test test/unit/

# Tests de widgets
flutter test test/widget/

# Tous les tests
flutter test
```
