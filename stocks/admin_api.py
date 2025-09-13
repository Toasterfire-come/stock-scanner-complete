import os
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

@require_http_methods(["GET"])  # simple status
def admin_status_api(request):
    return JsonResponse({
        "total_stocks": 0,
        "unsent_notifications": 0,
        "success_rate": 100,
        "last_update": None,
    })

@require_http_methods(["GET"])  # provider config visibility
def admin_api_providers_api(request):
    providers = {
        "yfinance": {"configured": True, "rate_limit": "0.5s/request"},
        "paypal": {
            "configured": bool(os.environ.get("PAYPAL_CLIENT_ID") and os.environ.get("PAYPAL_CLIENT_SECRET")),
            "rate_limit": "N/A",
        },
    }
    return JsonResponse(providers)

@csrf_exempt
@require_http_methods(["POST"])  # echo
def admin_execute_api(request):
    return JsonResponse({"success": True, "message": "Operation queued"})
