# Fichiers de Traduction - Bridge Quest

Ce dossier contient les fichiers de traduction générés par Django.

## Structure

```
locale/
├── fr/
│   └── LC_MESSAGES/
│       ├── django.po      # Fichier de traduction français
│       └── django.mo       # Fichier compilé (généré)
└── en/
    └── LC_MESSAGES/
        ├── django.po      # Fichier de traduction anglais
        └── django.mo       # Fichier compilé (généré)
```

## Commandes

### Via Makefile (recommandé)

```bash
# Générer les fichiers de traduction pour toutes les langues
make makemessages

# Générer uniquement pour le français
make makemessages-fr

# Générer uniquement pour l'anglais
make makemessages-en

# Compiler les traductions
make compilemessages

# Générer ET compiler en une seule commande
make i18n
```

### Via Django directement

```bash
# Pour le français
python manage.py makemessages -l fr

# Pour l'anglais
python manage.py makemessages -l en

# Pour toutes les langues configurées
python manage.py makemessages -a

# Compiler toutes les traductions
python manage.py compilemessages
```

### Format d'un fichier .po

```po
# locale/fr/LC_MESSAGES/django.po
msgid "app.games.name"
msgstr "Parties de jeu"

msgid "validation.game.code.alphanumeric"
msgstr "Le code de partie doit être alphanumérique."

msgid "error.game.name.required"
msgstr "Le nom de la partie est requis."
```

## Workflow

1. **Ajouter une nouvelle clé** dans `utils/messages.py`
2. **Utiliser la clé** dans le code avec `_(Messages.KEY)`
3. **Générer les fichiers** : `make makemessages` ou `make makemessages-fr makemessages-en`
4. **Traduire** les messages dans les fichiers `.po`
5. **Compiler** : `make compilemessages` ou `make i18n` (génère + compile)
6. **Tester** que les traductions fonctionnent

## Notes

- Les fichiers `.po` sont versionnés dans Git
- Les fichiers `.mo` sont générés et peuvent être ignorés (dans .gitignore)
- Toujours vérifier que les traductions sont complètes avant de compiler
