"""
Commande de management pour le traitement du cycle de vie des parties.

Boucle de polling qui détecte les parties dont un timer a expiré
et déclenche la transition d'état correspondante :
- DEPLOYMENT -> IN_PROGRESS (deployment_ends_at atteint)
- IN_PROGRESS -> FINISHED (game_ends_at atteint)

Usage :
    python manage.py process_lifecycle
    python manage.py process_lifecycle --interval 2
    python manage.py process_lifecycle --once
"""
import logging
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from games.models import Game, GameState
from games.services.lifecycle_service import begin_in_progress, finish_game

logger = logging.getLogger("bridgequest.lifecycle")

_DEFAULT_INTERVAL = 1  # secondes


class Command(BaseCommand):
    """Boucle de polling pour les transitions automatiques du cycle de vie."""

    help = (
        "Traite le cycle de vie des parties : transitions automatiques "
        "DEPLOYMENT -> IN_PROGRESS et IN_PROGRESS -> FINISHED."
    )

    def add_arguments(self, parser):
        """Ajoute les arguments de la commande."""
        parser.add_argument(
            "--interval",
            type=float,
            default=_DEFAULT_INTERVAL,
            help=(
                "Intervalle de polling en secondes "
                f"(défaut : {_DEFAULT_INTERVAL}s)."
            ),
        )
        parser.add_argument(
            "--once",
            action="store_true",
            default=False,
            help="Exécute un seul cycle puis s'arrête (utile pour les tests).",
        )

    def handle(self, *args, **options):
        """Point d'entrée : boucle infinie ou exécution unique."""
        interval = options["interval"]
        once = options["once"]

        if once:
            self._tick()
            return

        self._run_loop(interval)

    def _run_loop(self, interval):
        """
        Boucle principale de polling.

        Exécute ``_tick`` à chaque intervalle jusqu'à interruption (Ctrl+C).

        Args:
            interval: Pause entre chaque cycle (en secondes).
        """
        logger.info(
            "process_lifecycle démarré (intervalle : %ss)", interval,
        )
        self.stdout.write(self.style.SUCCESS(
            f"process_lifecycle démarré (intervalle : {interval}s). "
            "Ctrl+C pour arrêter."
        ))

        try:
            while True:
                self._tick()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("process_lifecycle arrêté (Ctrl+C)")
            self.stdout.write(self.style.WARNING(
                "\nprocess_lifecycle arrêté."
            ))

    def _tick(self):
        """Exécute un cycle de polling : vérifie les timers expirés."""
        now = timezone.now()
        self._process_deployment_ended(now)
        self._process_game_ended(now)

    def _process_deployment_ended(self, now):
        """
        Transition DEPLOYMENT -> IN_PROGRESS.

        Sélectionne les parties en déploiement dont le timer
        ``deployment_ends_at`` est dépassé et appelle
        ``begin_in_progress`` pour chacune.
        """
        games = Game.objects.select_related("settings").filter(
            state=GameState.DEPLOYMENT,
            deployment_ends_at__lte=now,
        )
        for game in games:
            self._transition_game(
                game,
                begin_in_progress,
                "DEPLOYMENT -> IN_PROGRESS",
            )

    def _process_game_ended(self, now):
        """
        Transition IN_PROGRESS -> FINISHED.

        Sélectionne les parties en cours dont le timer
        ``game_ends_at`` est dépassé et appelle
        ``finish_game`` pour chacune.
        """
        games = Game.objects.select_related("settings").filter(
            state=GameState.IN_PROGRESS,
            game_ends_at__lte=now,
        )
        for game in games:
            self._transition_game(
                game,
                finish_game,
                "IN_PROGRESS -> FINISHED",
            )

    def _transition_game(self, game, transition_fn, label):
        """
        Applique une transition à une partie avec gestion d'erreur.

        En cas d'exception, l'erreur est loguée et la boucle
        continue avec les autres parties.

        Args:
            game: La partie à traiter.
            transition_fn: Fonction de transition (begin_in_progress ou finish_game).
            label: Libellé de la transition pour les logs.
        """
        try:
            transition_fn(game)
            logger.info("Game %s (%s): %s", game.id, game.code, label)
        except Exception:
            logger.exception(
                "Game %s (%s): erreur %s", game.id, game.code, label,
            )
