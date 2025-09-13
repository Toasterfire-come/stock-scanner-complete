from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["GET"])
def docs_page(request):
    # Simple docs landing to avoid 500s
    return HttpResponse("<h1>API Docs</h1><p>See /api/ for endpoints.</p>")

@require_http_methods(["GET"])
def schema_page(request):
    return JsonResponse({"detail": "Schema not configured", "success": True})

@require_http_methods(["GET"])
def redoc_page(request):
    return HttpResponse("<h1>ReDoc</h1><p>Not configured.</p>")

@require_http_methods(["GET"])
def openapi_json(request):
    return JsonResponse({
        "openapi": "3.0.0",
        "info": {"title": "Stock Scanner API", "version": "1.0.0"},
        "paths": {},
    })

@require_http_methods(["GET"])
def endpoint_status(request):
    return JsonResponse({
        "status": "ok",
        "endpoints": [
            "/",
            "/api/",
            "/api/stocks/",
            "/api/auth/login/",
            "/api/usage/track/",
            "/api/billing/paypal-status/",
            "/api/revenue/validate-discount/",
        ]
    })