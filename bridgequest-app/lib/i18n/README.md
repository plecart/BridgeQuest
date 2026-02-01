# Fichiers de localisation

## Structure

- **`app_fr.arb`** et **`app_en.arb`** : Fichiers source contenant les traductions (à modifier)
- **`app_localizations.dart`**, **`app_localizations_fr.dart`**, **`app_localizations_en.dart`** : Fichiers générés automatiquement (ne jamais modifier)

## Workflow

1. **Modifier uniquement les fichiers `.arb`** pour ajouter ou modifier des traductions
2. **Exécuter `flutter pub get`** ou **`flutter gen-l10n`** pour régénérer les fichiers Dart
3. **Ne jamais modifier manuellement les fichiers `.dart`** générés (ils seront écrasés)

## Exemple d'ajout d'une traduction

1. Ajouter la clé dans `app_fr.arb` :
```json
"welcomeMessage": "Bienvenue",
"@welcomeMessage": {
  "description": "Message de bienvenue"
}
```

2. Ajouter la même clé dans `app_en.arb` :
```json
"welcomeMessage": "Welcome",
"@welcomeMessage": {
  "description": "Welcome message"
}
```

3. Exécuter `flutter pub get` pour régénérer les fichiers Dart

4. Utiliser dans le code :
```dart
AppLocalizations.of(context)!.welcomeMessage
```

## Note importante

Les fichiers `.dart` dans ce répertoire sont générés automatiquement par Flutter à partir des fichiers `.arb`. 
Ils sont ajoutés au `.gitignore` pour éviter toute confusion et modification accidentelle.
