from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def news_feed_api(request):
    # Minimal public feed to avoid 401s in clients expecting this endpoint
    items = [
        {"title": "Welcome to Stock Scanner", "summary": "News feed is active.", "ticker": None},
    ]
    return JsonResponse({"success": True, "count": len(items), "items": items})