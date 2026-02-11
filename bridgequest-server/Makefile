.PHONY: help server server-ws run migrate install test clean makemessages makemessages-fr makemessages-en compilemessages i18n shell createsuperuser check clean-db reset-db test-quiet test-unit

# ============================================================================
# Variables
# ============================================================================

PYTHON = python3
PIP = $(PYTHON) -m pip
MANAGE = manage.py

# Couleurs pour les messages
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m

# ============================================================================
# Fonctions shell réutilisables
# ============================================================================

# Affiche un message de début
define msg-start
	@echo "$(GREEN)$(1)...$(NC)"
endef

# Affiche un message de fin
define msg-done
	@echo "$(GREEN)$(1)$(NC)"
endef

# Affiche un message d'avertissement
define msg-warn
	@echo "$(YELLOW)$(1)...$(NC)"
endef

# ============================================================================
# Aide
# ============================================================================

help: ## Affiche cette aide
	@echo "$(GREEN)Commandes disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-30s$(NC) %s\n", $$1, $$2}'

# ============================================================================
# Serveur
# ============================================================================

server: ## Démarre le serveur Django de développement (HTTP uniquement)
	$(call msg-start,Démarrage du serveur Django)
	$(PYTHON) $(MANAGE) runserver

server-ws: ## Démarre le serveur avec Daphne (HTTP + WebSocket)
	$(call msg-start,Démarrage du serveur Daphne)
	$(PYTHON) -m daphne -b 0.0.0.0 -p 8000 bridgequest.asgi:application

server-8001: ## Démarre le serveur Django sur le port 8001
	$(call msg-start,Démarrage du serveur Django sur le port 8001)
	$(PYTHON) $(MANAGE) runserver 8001

run: server ## Alias pour server (cohérence avec Flutter)

# ============================================================================
# Base de données
# ============================================================================

migrate: ## Applique les migrations de la base de données
	$(call msg-start,Application des migrations)
	$(PYTHON) $(MANAGE) migrate

makemigrations: ## Crée de nouvelles migrations
	$(call msg-start,Création des migrations)
	$(PYTHON) $(MANAGE) makemigrations

clean-db: ## Supprime la base de données SQLite (ATTENTION: supprime toutes les données)
	$(call msg-warn,ATTENTION: Suppression de la base de données)
	rm -f db.sqlite3
	$(call msg-done,Base de données supprimée)

reset-db: clean-db migrate ## Réinitialise la base de données (supprime et recrée)
	$(call msg-done,Base de données réinitialisée)

# ============================================================================
# Installation et configuration
# ============================================================================

install: ## Installe les dépendances Python
	$(call msg-start,Installation des dépendances)
	$(PIP) install --break-system-packages -r requirements.txt

shell: ## Ouvre le shell Django
	$(call msg-start,Ouverture du shell Django)
	$(PYTHON) $(MANAGE) shell

createsuperuser: ## Crée un superutilisateur Django
	$(call msg-start,Création d'un superutilisateur)
	$(PYTHON) $(MANAGE) createsuperuser

check: ## Vérifie la configuration Django
	$(call msg-start,Vérification de la configuration)
	$(PYTHON) $(MANAGE) check

# ============================================================================
# Tests
# ============================================================================

test: ## Lance les tests avec logging optimisé
	$(call msg-start,Lancement des tests)
	DJANGO_SETTINGS_MODULE=bridgequest.settings.testing $(PYTHON) $(MANAGE) test --verbosity=2

test-quiet: ## Lance les tests sans verbosité
	$(call msg-start,Lancement des tests (mode silencieux))
	DJANGO_SETTINGS_MODULE=bridgequest.settings.testing $(PYTHON) $(MANAGE) test --verbosity=0

test-unit: test ## Alias pour test (cohérence avec Flutter)

# ============================================================================
# Internationalisation
# ============================================================================

makemessages: ## Génère les fichiers de traduction pour toutes les langues
	$(call msg-start,Génération des fichiers de traduction)
	$(PYTHON) $(MANAGE) makemessages -a

makemessages-fr: ## Génère les fichiers de traduction pour le français
	$(call msg-start,Génération des fichiers de traduction français)
	$(PYTHON) $(MANAGE) makemessages -l fr

makemessages-en: ## Génère les fichiers de traduction pour l'anglais
	$(call msg-start,Génération des fichiers de traduction anglais)
	$(PYTHON) $(MANAGE) makemessages -l en

compilemessages: ## Compile les fichiers de traduction (.po -> .mo)
	$(call msg-start,Compilation des traductions)
	$(PYTHON) $(MANAGE) compilemessages

i18n: makemessages compilemessages ## Génère et compile toutes les traductions Django
	$(call msg-done,Traductions générées et compilées)

# ============================================================================
# Nettoyage
# ============================================================================

clean: ## Nettoie les fichiers temporaires (cache Python, __pycache__, etc.)
	$(call msg-start,Nettoyage des fichiers temporaires)
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	$(call msg-done,Nettoyage terminé)
