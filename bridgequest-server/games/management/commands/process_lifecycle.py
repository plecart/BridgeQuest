"""
Commande de management pour le traitement du cycle de vie des parties.

Alternative au worker automatique (``LIFECYCLE_AUTO_PROCESS``) pour les
déploiements où le worker tourne dans un processus séparé (supervisord,
systemd, Docker Compose, etc.).

La logique de polling est partagée avec ``lifecycle_worker``.

Usage :
    python manage.py process_lifecycle
    python manage.py process_lifecycle --interval 2
    python manage.py process_lifecycle --once
"""
import logging
import time

from django.core.management.base import BaseCommand

from games.services.lifecycle_worker import tick

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
            tick()
            return

        self._run_loop(interval)

    def _run_loop(self, interval):
        """
        Boucle principale de polling.

        Exécute ``tick`` à chaque intervalle jusqu'à interruption (Ctrl+C).

        Args:
            interval: Pause entre chaque cycle (en secondes).
        """
        logger.info(
            "process_lifecycle started (interval: %ss)", interval,
        )
        self.stdout.write(self.style.SUCCESS(
            f"process_lifecycle started (interval: {interval}s). "
            "Ctrl+C to stop."
        ))

        try:
            while True:
                tick()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("process_lifecycle stopped (Ctrl+C)")
            self.stdout.write(self.style.WARNING(
                "\nprocess_lifecycle stopped."
            ))
