.PHONY: help server migrate install test clean makemessages makemessages-fr makemessages-en compilemessages i18n

# Variables
SERVER_DIR = bridgequest-server
PYTHON = python3
PIP = $(PYTHON) -m pip
MANAGE = $(SERVER_DIR)/manage.py

# Couleurs pour les messages
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

help: ## Affiche cette aide
	@echo "$(GREEN)Commandes disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

server: ## Démarre le serveur Django de développement
	@echo "$(GREEN)Démarrage du serveur Django...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py runserver

server-8001: ## Démarre le serveur Django sur le port 8001
	@echo "$(GREEN)Démarrage du serveur Django sur le port 8001...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py runserver 8001

migrate: ## Applique les migrations de la base de données
	@echo "$(GREEN)Application des migrations...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py migrate

makemigrations: ## Crée de nouvelles migrations
	@echo "$(GREEN)Création des migrations...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py makemigrations

install: ## Installe les dépendances Python
	@echo "$(GREEN)Installation des dépendances...$(NC)"
	cd $(SERVER_DIR) && $(PIP) install --break-system-packages -r requirements.txt

shell: ## Ouvre le shell Django
	@echo "$(GREEN)Ouverture du shell Django...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py shell

createsuperuser: ## Crée un superutilisateur Django
	@echo "$(GREEN)Création d'un superutilisateur...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py createsuperuser

test: ## Lance les tests
	@echo "$(GREEN)Lancement des tests...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py test

check: ## Vérifie la configuration Django
	@echo "$(GREEN)Vérification de la configuration...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py check

clean: ## Nettoie les fichiers temporaires (cache Python, __pycache__, etc.)
	@echo "$(GREEN)Nettoyage des fichiers temporaires...$(NC)"
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	@echo "$(GREEN)Nettoyage terminé$(NC)"

clean-db: ## Supprime la base de données SQLite (ATTENTION: supprime toutes les données)
	@echo "$(YELLOW)ATTENTION: Suppression de la base de données...$(NC)"
	cd $(SERVER_DIR) && rm -f db.sqlite3
	@echo "$(GREEN)Base de données supprimée$(NC)"

reset-db: clean-db migrate ## Réinitialise la base de données (supprime et recrée)
	@echo "$(GREEN)Base de données réinitialisée$(NC)"

makemessages: ## Génère les fichiers de traduction pour toutes les langues
	@echo "$(GREEN)Génération des fichiers de traduction...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py makemessages -a

makemessages-fr: ## Génère les fichiers de traduction pour le français
	@echo "$(GREEN)Génération des fichiers de traduction français...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py makemessages -l fr

makemessages-en: ## Génère les fichiers de traduction pour l'anglais
	@echo "$(GREEN)Génération des fichiers de traduction anglais...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py makemessages -l en

compilemessages: ## Compile les fichiers de traduction (.po -> .mo)
	@echo "$(GREEN)Compilation des traductions...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) manage.py compilemessages

i18n: makemessages compilemessages ## Génère et compile toutes les traductions
	@echo "$(GREEN)Traductions générées et compilées$(NC)"
