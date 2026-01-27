# Bridge Quest - Backend Server

Backend Django pour l'application Bridge Quest.

## Installation

### Prérequis

- Python 3.10 ou supérieur
- pip

### Étapes d'installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
```

2. Activer l'environnement virtuel :
```bash
# Sur Windows
venv\Scripts\activate

# Sur Linux/Mac
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Appliquer les migrations :
```bash
python manage.py migrate
```

5. Créer un superutilisateur (optionnel) :
```bash
python manage.py createsuperuser
```

6. Lancer le serveur de développement :
```bash
python manage.py runserver
```

Le serveur sera accessible sur `http://127.0.0.1:8000/`

## Structure du projet

```
bridgequest-server/
├── bridgequest/          # Configuration Django principale
│   ├── settings/        # Settings modulaires (à venir)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/             # Module d'authentification (à venir)
├── games/                # Module de gestion des parties (à venir)
├── manage.py
└── requirements.txt
```

## Développement

### Tests

```bash
# Avec pytest
pytest

# Avec coverage
pytest --cov
```

### Formatage du code

```bash
# Formater avec black
black .

# Vérifier avec flake8
flake8 .

# Organiser les imports avec isort
isort .
```

## Variables d'environnement

Créer un fichier `.env` à la racine avec :

```
SECRET_KEY=votre_secret_key_ici
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```
