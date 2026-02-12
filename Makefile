.PHONY: help server lifecycle run-app

# ============================================================================
# Variables
# ============================================================================

SERVER_DIR = bridgequest-server
APP_DIR = bridgequest-app

# Couleurs pour les messages
GREEN = \033[0;32m
NC = \033[0m

# ============================================================================
# Aide
# ============================================================================

help: ## Affiche cette aide
	@echo "$(GREEN)Makefile racine - Commandes principales$(NC)"
	@echo ""
	@echo "$(GREEN)Commandes disponibles:$(NC)"
	@echo "  $(GREEN)server$(NC)              Démarre le serveur Django"
	@echo "  $(GREEN)lifecycle$(NC)           Lance la boucle du cycle de vie des parties"
	@echo "  $(GREEN)run-app$(NC)             Lance l'application Flutter"
	@echo ""
	@echo "$(GREEN)Pour plus de commandes:$(NC)"
	@echo "  $(GREEN)cd $(SERVER_DIR) && make help$(NC)    Commandes Django"
	@echo "  $(GREEN)cd $(APP_DIR) && make help$(NC)       Commandes Flutter"

# ============================================================================
# Commandes principales
# ============================================================================

server: ## Démarre le serveur Django
	@cd $(SERVER_DIR) && $(MAKE) server

lifecycle: ## Lance la boucle de traitement du cycle de vie des parties
	@cd $(SERVER_DIR) && $(MAKE) lifecycle

run-app: ## Lance l'application Flutter
	@cd $(APP_DIR) && $(MAKE) run
