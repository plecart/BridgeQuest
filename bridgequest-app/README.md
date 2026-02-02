# Bridge Quest - Application Flutter

Application mobile Flutter pour Bridge Quest.

## Prérequis

- Flutter SDK (version 3.0 ou supérieure)
- Dart SDK (inclus avec Flutter)
- Android Studio / Xcode (pour le développement mobile)

## Installation

### Sur Linux/macOS

```bash
# Installer Flutter
# Voir: https://docs.flutter.dev/get-started/install

# Installer les dépendances
make install
```

### Sur Windows / WSL

Si vous utilisez WSL et que Flutter est installé sur Windows :

```bash
# Option 1: Spécifier le chemin complet
make install FLUTTER_PATH=/mnt/c/Users/VOTRE_USER/Downloads/flutter/bin/flutter.bat

# Option 2: Ajouter Flutter au PATH WSL
export PATH="$PATH:/mnt/c/Users/VOTRE_USER/Downloads/flutter/bin"
make install

# Option 3: Installer Flutter directement dans WSL (recommandé)
# Voir: https://docs.flutter.dev/get-started/install/linux
```

## Commandes disponibles

```bash
make help              # Affiche toutes les commandes disponibles
make install           # Installe les dépendances
make run               # Lance l'application
make test              # Lance les tests
make analyze           # Analyse le code
make format            # Formate le code
make clean             # Nettoie les fichiers générés
```

## Structure du projet

```
lib/
├── core/              # Configuration et utilitaires
│   ├── config/        # Configuration (API, app)
│   └── exceptions/    # Exceptions personnalisées
├── data/              # Couche de données
│   ├── models/        # Modèles de données
│   ├── repositories/  # Repositories
│   └── services/      # Services (API, storage, SSO)
├── presentation/      # Interface utilisateur
│   ├── pages/         # Pages de l'application
│   ├── widgets/       # Widgets réutilisables
│   └── theme/         # Thème de l'application
└── providers/         # State management (Provider)
```

## Authentification API

L'application utilise une **authentification OAuth2/JWT** : les tokens sont envoyés via l'en-tête `Authorization` (Bearer). Aucune authentification par cookies ni `dio_cookie_manager` n'est utilisée. Voir `lib/data/services/api_service.dart` et `lib/data/services/token_manager.dart`.

## Développement

L'application suit les standards définis dans `bridgequest-doc/CODING_STANDARDS_FLUTTER.md`.

### Internationalisation

Les textes sont gérés via les fichiers `.arb` dans `lib/i18n/`.

```bash
make i18n  # Génère les fichiers de localisation
```

## Tests

```bash
make test          # Tous les tests
make test-unit      # Tests unitaires uniquement
make test-widget    # Tests de widgets uniquement
```

## Build

```bash
make build-android          # Build Android (debug)
make build-android-release  # Build Android (release)
make build-ios              # Build iOS (debug)
make build-ios-release      # Build iOS (release)
```
