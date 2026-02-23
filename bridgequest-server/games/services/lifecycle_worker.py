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
sur PostgreSQL/MySQL. SQLite (dev par défaut) ne supporte pas skip_locked :
on utilise une requête sans verrou (transaction.atomic suffit pour l'isolation).
"""
import logging
import os
import sys
import threading
import time

from django.db import connection, transaction
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

    # Exclure les commandes de gestion Django (migrate, test, shell, etc.)
    if sys.argv[0].endswith("manage.py"):
        return False

    # Daphne, Gunicorn, etc. : lancés directement (pas via manage.py) — démarrer le worker
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
    logger.info("Lifecycle worker started (interval: %ss)", interval)


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
            logger.exception("Lifecycle worker: error during tick")
        time.sleep(interval)


def _try_acquire_and_transition(*, model, game_id, filters, use_row_lock,
                                 transition_fn, label):
    """
    Tente d'acquérir une partie et d'exécuter la transition.

    Applique à nouveau les filtres (state, timestamp) dans la requête atomique :
    si la partie a été transitionnée entre le fetch des IDs et ici (autre worker),
    elle ne matchera plus et on retourne sans traiter. Pas de travail inutile.

    Sur Postgres/MySQL : verrouillage via select_for_update(skip_locked=True).
    Sur SQLite : requête simple (transaction.atomic suffit).
    """
    with transaction.atomic():
        qs = (
            model.objects
            .select_related("settings")
            .filter(id=game_id, **filters)
        )
        if use_row_lock:
            qs = qs.select_for_update(skip_locked=True)
        game = qs.first()

        if game is None:
            return

        transition_fn(game)
        logger.info("Game %s (%s) : %s", game.id, game.code, label)


def _process_transitions(*, model, filters, transition_fn, label):
    """
    Applique une transition à chaque partie correspondant aux filtres.

    **Protection contre les races** : Sur PostgreSQL/MySQL, utilise
    ``select_for_update(skip_locked=True)`` pour éviter qu'un worker
    multi-processus traite la même transition en parallèle. SQLite (dev)
    ne supporte pas skip_locked : on utilise une requête simple dans
    transaction.atomic (isolation suffisante pour un processus unique).

    Args:
        model: Modèle Game.
        filters: Dictionnaire de filtres pour le queryset (ex: {"state": DEPLOYMENT, ...}).
        transition_fn: Fonction de transition (begin_in_progress ou finish_game).
        label: Label pour le logging (ex: "DEPLOYMENT -> IN_PROGRESS").
    """
    # Fetch des IDs sans verrou ; _try_acquire_and_transition re-vérifie
    # les filtres (state, timestamp) dans son bloc atomique, donc on ne
    # traite pas les parties déjà transitionnées par un autre worker.
    game_ids = list(
        model.objects.filter(**filters).values_list("id", flat=True)
    )
    use_row_lock = connection.features.has_select_for_update_skip_locked

    for game_id in game_ids:
        try:
            _try_acquire_and_transition(
                model=model,
                game_id=game_id,
                filters=filters,
                use_row_lock=use_row_lock,
                transition_fn=transition_fn,
                label=label,
            )
        except Exception:
            logger.exception("Game %s: error during %s", game_id, label)
