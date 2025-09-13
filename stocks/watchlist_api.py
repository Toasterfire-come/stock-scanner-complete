from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def watchlist_list_api(request):
    if not request.user.is_authenticated:
        # return empty list instead of 401 to keep clients working without auth
        return JsonResponse({"success": True, "watchlist": []})
    # No watchlist storage yet; placeholder structure
    return JsonResponse({"success": True, "watchlist": []})