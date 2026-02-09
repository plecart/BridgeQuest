.PHONY: help install run test clean i18n analyze format format-check check build-android build-android-release build-ios build-ios-release deps-outdated deps-upgrade setup run-ios run-android emulator

# ============================================================================
# Variables
# ============================================================================

FLUTTER = flutter
DART = dart

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
# Installation et configuration
# ============================================================================

install: ## Installe les dépendances Flutter
	$(call msg-start,Installation des dépendances Flutter)
	$(FLUTTER) pub get
	$(call msg-done,Dépendances installées)

i18n: ## Génère les fichiers de localisation Flutter
	$(call msg-start,Génération des fichiers de localisation)
	$(FLUTTER) gen-l10n
	$(call msg-done,Fichiers de localisation générés)

setup: install i18n ## Configuration initiale Flutter (install + i18n)
	$(call msg-done,Configuration Flutter terminée)

# ============================================================================
# Développement
# ============================================================================

run: ## Lance l'application Flutter en mode développement
	$(call msg-start,Lancement de l'application Flutter)
	$(FLUTTER) run

run-ios: ## Lance l'application Flutter sur iOS (macOS uniquement)
	$(call msg-start,Lancement sur iOS)
	$(FLUTTER) run -d ios

run-android: ## Lance l'application Flutter sur l'émulateur Android (emulator-5554)
	$(call msg-start,Lancement sur l'émulateur Android)
	$(FLUTTER) run -d emulator-5554

emulator: ## Démarre l'émulateur Android (Medium_Phone_API_36.1)
	$(call msg-start,Démarrage de l'émulateur Android)
	/c/Users/pacom/AppData/Local/Android/Sdk/emulator/emulator.exe -avd Medium_Phone_API_36.1
	$(call msg-done,Émulateur lancé)

# ============================================================================
# Qualité de code
# ============================================================================

analyze: ## Analyse le code Flutter (vérification statique)
	$(call msg-start,Analyse du code Flutter)
	$(FLUTTER) analyze
	$(call msg-done,Analyse terminée)

format: ## Formate le code Flutter avec dart format
	$(call msg-start,Formatage du code Flutter)
	$(DART) format .
	$(call msg-done,Formatage terminé)

format-check: ## Vérifie le formatage du code Flutter sans modifier
	$(call msg-start,Vérification du formatage)
	$(DART) format --set-exit-if-changed .
	$(call msg-done,Formatage correct)

check: analyze format-check test ## Vérifie le code Flutter (analyse + format + tests)
	$(call msg-done,Vérifications Flutter terminées)

# ============================================================================
# Tests
# ============================================================================

test: ## Lance tous les tests Flutter
	$(call msg-start,Lancement des tests Flutter)
	$(FLUTTER) test
	$(call msg-done,Tests terminés)

# ============================================================================
# Build
# ============================================================================

build-android: ## Build l'application Android (APK debug)
	$(call msg-start,Build Android (debug))
	$(FLUTTER) build apk --debug
	$(call msg-done,Build Android terminé)

build-android-release: ## Build l'application Android (APK release)
	$(call msg-start,Build Android (release))
	$(FLUTTER) build apk --release
	$(call msg-done,Build Android release terminé)

build-ios: ## Build l'application iOS (macOS uniquement)
	$(call msg-start,Build iOS (debug))
	$(FLUTTER) build ios --debug
	$(call msg-done,Build iOS terminé)

build-ios-release: ## Build l'application iOS release (macOS uniquement)
	$(call msg-start,Build iOS (release))
	$(FLUTTER) build ios --release
	$(call msg-done,Build iOS release terminé)

# ============================================================================
# Maintenance
# ============================================================================

clean: ## Nettoie les fichiers générés Flutter (build, cache, etc.)
	$(call msg-start,Nettoyage des fichiers Flutter)
	$(FLUTTER) clean
	$(call msg-done,Nettoyage terminé)

deps-outdated: ## Vérifie les dépendances Flutter obsolètes
	$(call msg-start,Vérification des dépendances obsolètes)
	$(FLUTTER) pub outdated
	$(call msg-done,Vérification terminée)

deps-upgrade: ## Met à jour les dépendances Flutter (dry-run)
	$(call msg-start,Vérification des mises à jour disponibles)
	$(FLUTTER) pub upgrade --dry-run
	$(call msg-done,Vérification terminée)
