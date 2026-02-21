"""
Worker daemon pour le traitement automatique du cycle de vie des parties.

Lance un thread daemon qui sonde la base toutes les N secondes
et déclenche les transitions d'état expirées :
- DEPLOYMENT  -> IN_PROGRESS  (deployment_ends_at dépassé)
- IN_PROGRESS -> FINISHED     (game_ends_at dépassé)

Le thread est un daemon : il s'arrête automatiquement quand le
processus principal (serveur Daphne) se termine.

Démarrage automatique :
    Appelé par ``GamesConfig.ready()`` lorsque ``LIFECYCLE_AUTO_PROCESS``
    est activé et que le processus est un serveur (pas migrate, test, etc.).

Démarrage manuel (production) :
    ``python manage.py process_lifecycle`` reste disponible pour les
    déploiements où le worker tourne dans un processus séparé.

**Protection contre les races** : Les transitions sont protégées par
verrouillage transactionnel (``select_for_update(skip_locked=True)``)
pour éviter qu'un worker multi-processus traite la même transition
en parallèle (double attribution de rôles, double incrément de scores).
"""
import logging
import os
import sys
import threading
import time

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger("bridgequest.lifecycle")

_DEFAULT_INTERVAL = 1  # secondes

_started = False
_lock = threading.Lock()


# ── Public API ───────────────────────────────────────────────────────

def should_auto_start():
    """
    Détermine si le worker doit démarrer automatiquement.

    Retourne ``True`` uniquement quand le processus est un serveur
    (Daphne standalone ou ``manage.py runserver``), jamais pour les
    commandes de gestion (migrate, test, shell, etc.).
    """
    from django.conf import settings

    if not getattr(settings, "LIFECYCLE_AUTO_PROCESS", True):
        return False

    # Détection pour runserver avec reload
    if len(sys.argv) >= 2 and sys.argv[1] == "runserver":
        if "--noreload" in sys.argv:
            return True
        return os.environ.get("RUN_MAIN") == "true"

    # Exclure les commandes de gestion Django
    if len(sys.argv) >= 1 and sys.argv[0].endswith("manage.py"):
        return False

    return True


def start(interval=_DEFAULT_INTERVAL):
    """
    Démarre le worker dans un thread daemon (idempotent).

    Args:
        interval: Pause entre chaque cycle de polling (en secondes).
    """
    global _started
    with _lock:
        if _started:
            return
        _started = True

    thread = threading.Thread(
        target=_run_loop,
        args=(interval,),
        daemon=True,
        name="lifecycle-worker",
    )
    thread.start()
    logger.info("Lifecycle worker démarré (intervalle : %ss)", interval)


# ── Shared tick logic (réutilisé par la management command) ──────────

def tick():
    """
    Exécute un cycle de polling : détecte les timers expirés
    et déclenche les transitions correspondantes.
    """
    from games.models import Game, GameState
    from games.services.lifecycle_service import begin_in_progress, finish_game

    now = timezone.now()

    _process_transitions(
        model=Game,
        filters={
            "state": GameState.DEPLOYMENT,
            "deployment_ends_at__lte": now,
        },
        transition_fn=begin_in_progress,
        label="DEPLOYMENT -> IN_PROGRESS",
    )
    _process_transitions(
        model=Game,
        filters={
            "state": GameState.IN_PROGRESS,
            "game_ends_at__lte": now,
        },
        transition_fn=finish_game,
        label="IN_PROGRESS -> FINISHED",
    )


# ── Internal ─────────────────────────────────────────────────────────

def _run_loop(interval):
    """Boucle principale du thread daemon."""
    while True:
        try:
            tick()
        except Exception:
            logger.exception("Lifecycle worker : erreur pendant le tick")
        time.sleep(interval)


def _process_transitions(*, model, filters, transition_fn, label):
    """
    Applique une transition à chaque partie correspondant aux filtres.

    **Protection contre les races** : Utilise ``select_for_update(skip_locked=True)``
    dans une transaction atomique pour éviter qu'un worker multi-processus traite
    la même transition en parallèle. Si une partie est déjà verrouillée par un
    autre worker, elle est ignorée (skip_locked=True).

    Args:
        model: Modèle Game.
        filters: Dictionnaire de filtres pour le queryset (ex: {"state": DEPLOYMENT, ...}).
        transition_fn: Fonction de transition (begin_in_progress ou finish_game).
        label: Label pour le logging (ex: "DEPLOYMENT -> IN_PROGRESS").
    """
    # Récupérer les IDs pour éviter de charger les objets avant le verrouillage
    game_ids = list(
        model.objects.filter(**filters).values_list("id", flat=True)
    )

    for game_id in game_ids:
        try:
            with transaction.atomic():
                # Verrouiller la ligne pour cette transition uniquement
                # skip_locked=True : ignorer si déjà verrouillé par un autre worker
                game = (
                    model.objects
                    .select_for_update(skip_locked=True)
                    .select_related("settings")
                    .filter(id=game_id, **filters)
                    .first()
                )

                # Si la partie est déjà verrouillée ou l'état a changé, skip
                if game is None:
                    continue

                transition_fn(game)
                logger.info("Game %s (%s) : %s", game.id, game.code, label)
        except Exception:
            logger.exception("Game %s : erreur %s", game_id, label)
