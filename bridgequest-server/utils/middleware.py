"""
Middleware pour Bridge Quest.

Responsabilité : AccessLogMiddleware — enregistre les requêtes HTTP
avec le format unifié du projet pour une cohérence visuelle en console.
"""
import logging
from urllib.parse import parse_qs, urlencode, urlparse

logger = logging.getLogger('bridgequest.access')

# Format NCSA-like pour alignement avec le formatter 'verbose' Django
_LOG_FORMAT = '{client} - - "{method} {path}" {status} {size}'

# Paramètres de query string à ne jamais logger en clair (JWT, tokens, clés API)
_SENSITIVE_QUERY_PARAMS = frozenset(
    ('token', 'jwt', 'access_token', 'refresh_token', 'api_key', 'key', 'secret')
)


def _get_client_ip(request):
    """Récupère l'adresse IP du client (supporte X-Forwarded-For en cas de proxy)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '-')


def _can_measure_response_size(response):
    """
    Vérifie si la taille de la réponse peut être mesurée sans erreur.

    Retourne False pour TemplateResponse non rendue (ContentNotRenderedError)
    et StreamingHttpResponse (pas de content mesurable).
    """
    if hasattr(response, 'is_rendered') and not response.is_rendered:
        return False
    if hasattr(response, 'streaming_content'):
        return False
    return True


def _get_response_size(response):
    """
    Récupère la taille de la réponse en octets.

    Retourne 0 pour StreamingHttpResponse, TemplateResponse non rendue,
    ou si la taille n'est pas déterminable.
    """
    if not _can_measure_response_size(response):
        return 0
    content = getattr(response, 'content', None)
    if isinstance(content, bytes):
        return len(content)
    return 0


def _get_safe_log_path(request):
    """
    Retourne le chemin pour les logs, avec paramètres sensibles redactés.

    Évite d'exposer les JWT (ex: ?token=xxx pour WebSocket) dans les logs
    console et agrégateurs.
    """
    full_path = request.get_full_path()
    parsed = urlparse(full_path)
    if not parsed.query:
        return parsed.path
    params = parse_qs(parsed.query, keep_blank_values=True)
    for param in params.keys() & _SENSITIVE_QUERY_PARAMS:
        params[param] = ['***']
    safe_query = urlencode(params, doseq=True)
    return f"{parsed.path}?{safe_query}" if safe_query else parsed.path


def _format_access_log_message(client, method, path, status, size):
    """Construit le message de log au format NCSA pour cohérence avec le formatter verbose."""
    return _LOG_FORMAT.format(
        client=client,
        method=method,
        path=path,
        status=status,
        size=size,
    )


class AccessLogMiddleware:
    """
    Middleware qui enregistre les requêtes HTTP avec le format unifié du projet.

    Remplace les access logs Daphne en console par un format cohérent avec
    les autres logs ({levelname} {asctime} [{module}] {message}).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._log_request(request, response)
        return response

    def _log_request(self, request, response):
        """Enregistre la requête avec le format unifié."""
        client = _get_client_ip(request)
        method = request.method
        path = _get_safe_log_path(request)
        status = response.status_code
        size = _get_response_size(response)

        message = _format_access_log_message(client, method, path, status, size)
        logger.info(message)
