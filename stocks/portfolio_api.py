from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def portfolio_list_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": True, "portfolio": []})
    # Placeholder portfolio payload
    return JsonResponse({"success": True, "portfolio": []})