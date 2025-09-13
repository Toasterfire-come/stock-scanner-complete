import json
import logging
import os
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


def _paypal_config():
    return {
        "client_id": os.environ.get("PAYPAL_CLIENT_ID"),
        "client_secret": os.environ.get("PAYPAL_CLIENT_SECRET"),
        "mode": os.environ.get("PAYPAL_MODE", "sandbox"),
    }


@require_http_methods(["GET"])  # simple status probe, avoid CSRF
def paypal_status_api(request):
    cfg = _paypal_config()
    configured = bool(cfg["client_id"] and cfg["client_secret"])
    return JsonResponse({
        "configured": configured,
        "mode": cfg["mode"],
    })


@csrf_exempt
@require_http_methods(["POST"])  # avoid CSRF 403
def create_paypal_order_api(request):
    try:
        cfg = _paypal_config()
        if not (cfg["client_id"] and cfg["client_secret"]):
            logger.warning("Create PayPal order called without credentials")
            # Return 200 to prevent 500 spam in logs, but clearly mark not configured
            return JsonResponse({"success": False, "configured": False, "error": "paypal_not_configured"})

        data = _parse_json(request)
        # In placeholder mode, just echo back a fake order id
        amount = data.get("amount", 0)
        currency = data.get("currency", "USD")
        fake_order_id = "TEST-ORDER-" + os.urandom(4).hex().upper()
        return JsonResponse({
            "success": True,
            "configured": True,
            "orderID": fake_order_id,
            "amount": amount,
            "currency": currency,
            "mode": cfg["mode"],
        })
    except Exception as e:
        logger.error(f"Create PayPal order error: {e}")
        return JsonResponse({"success": False, "error": "create_failed"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])  # avoid CSRF 403
def capture_paypal_order_api(request):
    try:
        cfg = _paypal_config()
        if not (cfg["client_id"] and cfg["client_secret"]):
            logger.warning("Capture PayPal order called without credentials")
            return JsonResponse({"success": False, "configured": False, "error": "paypal_not_configured"})

        data = _parse_json(request)
        order_id = data.get("orderID") or data.get("order_id")
        if not order_id:
            return JsonResponse({"success": False, "error": "order_id_required"}, status=400)
        # Placeholder capture
        return JsonResponse({"success": True, "configured": True, "orderID": order_id, "status": "COMPLETED"})
    except Exception as e:
        logger.error(f"Capture PayPal order error: {e}")
        return JsonResponse({"success": False, "error": "capture_failed"}, status=500)