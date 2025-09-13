import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

VALID_CODES = {
    "WELCOME10": {"type": "percent", "value": 10, "description": "Welcome discount"},
    "SUMMER20": {"type": "percent", "value": 20, "description": "Seasonal offer"},
    "PRO5": {"type": "amount", "value": 5, "description": "$5 off"},
}


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
@require_http_methods(["POST"])  # avoid CSRF issues
def validate_discount_api(request):
    try:
        data = _parse_json(request)
        code = (data.get("code") or data.get("coupon") or "").strip().upper()
        amount = float(data.get("amount", 0))
        if not code:
            return JsonResponse({"success": False, "error": "code_required"}, status=400)

        info = VALID_CODES.get(code)
        if not info:
            return JsonResponse({"success": False, "valid": False, "error": "invalid_code"}, status=200)

        discount_value = info["value"]
        discounted_amount = amount
        if info["type"] == "percent":
            discounted_amount = max(0.0, amount * (1 - discount_value / 100.0))
        elif info["type"] == "amount":
            discounted_amount = max(0.0, amount - discount_value)

        return JsonResponse({
            "success": True,
            "valid": True,
            "code": code,
            "discount": info,
            "amount_before": amount,
            "amount_after": round(discounted_amount, 2),
        })
    except Exception as e:
        logger.error(f"validate_discount error: {e}")
        return JsonResponse({"success": False, "error": "validation_failed"}, status=500)