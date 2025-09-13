import json
import logging
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

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
@require_http_methods(["POST"])
def login_api(request):
    data = _parse_json(request)
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        return JsonResponse({"success": False, "error": "username and password required"}, status=400)

    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({"success": False, "error": "invalid_credentials"}, status=401)

    login(request, user)
    return JsonResponse({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    })


@require_http_methods(["GET"])
def user_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False}, status=401)
    user = request.user
    return JsonResponse({
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request):
    logout(request)
    return JsonResponse({"success": True})