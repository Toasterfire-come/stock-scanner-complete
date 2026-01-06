"""
Favorites API

Minimal backend support for favoriting tickers across devices.
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .authentication import CsrfExemptSessionAuthentication, BearerSessionAuthentication
from .models import FavoriteTicker


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def favorites_list_create(request):
    if request.method == "GET":
        qs = FavoriteTicker.objects.filter(user=request.user).order_by("-created_at")
        return Response({"success": True, "favorites": [f.ticker for f in qs]})

    ticker = str(request.data.get("ticker") or "").upper().strip()
    if not ticker:
        return Response({"success": False, "error": "ticker required"}, status=400)

    FavoriteTicker.objects.get_or_create(user=request.user, ticker=ticker, defaults={"created_at": timezone.now()})
    qs = FavoriteTicker.objects.filter(user=request.user).order_by("-created_at")
    return Response({"success": True, "favorites": [f.ticker for f in qs]})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def favorites_remove(request, ticker: str):
    FavoriteTicker.objects.filter(user=request.user, ticker=str(ticker).upper().strip()).delete()
    qs = FavoriteTicker.objects.filter(user=request.user).order_by("-created_at")
    return Response({"success": True, "favorites": [f.ticker for f in qs]})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def favorites_clear(request):
    FavoriteTicker.objects.filter(user=request.user).delete()
    return Response({"success": True, "favorites": []})

