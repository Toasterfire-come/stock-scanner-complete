import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

logger = logging.getLogger(__name__)


def _parse_json(request):
    try:
        if hasattr(request, "_cached_json_body"):
            return request._cached_json_body
        body = request.body.decode("utf-8") or "{}"
        data = json.loads(body)
        request._cached_json_body = data
        return data
    except Exception as e:
        logger.warning(f"JSON parse error: {e}")
        return {}


@csrf_exempt
@require_http_methods(["POST"])  # Explicitly allow POST and avoid 403 CSRF
def usage_track_api(request):
    try:
        data = _parse_json(request)
        event = data.get("event", "generic")
        meta = data.get("meta", {})
        stats = {
            "received_at": timezone.now().isoformat(),
            "event": event,
            "meta": meta,
            "ip": request.META.get("REMOTE_ADDR"),
            "user_agent": request.META.get("HTTP_USER_AGENT"),
        }
        logger.info(f"Usage event: {stats}")
        return JsonResponse({"success": True, "tracked": True})
    except Exception as e:
        logger.error(f"Usage track error: {e}")
        return JsonResponse({"success": False, "error": "tracking_failed"}, status=500)