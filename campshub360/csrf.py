from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


def csrf_failure(request, reason=None):
    """Custom CSRF failure handler that logs details and avoids generic 500s."""
    logger.warning(
        "CSRF failure",
        extra={
            'path': request.path,
            'method': request.method,
            'reason': reason,
            'origin': request.headers.get('Origin'),
            'referer': request.headers.get('Referer'),
            'host': request.get_host(),
            'cookies': list(request.COOKIES.keys()),
        }
    )

    # Return JSON for API/AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('Accept', '').find('application/json') != -1:
        return JsonResponse({
            'success': False,
            'error': 'CSRF Failed',
            'reason': reason or 'Invalid or missing CSRF token',
        }, status=403)

    # Fallback simple 400/403 response for browser form posts
    return HttpResponseBadRequest("CSRF verification failed. Please refresh the page and try again.")


