"""
Trade Journal API

Backs the frontend Trading Journal (trade log + P&L analytics).
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import TradeJournalEntry
from .serializers import TradeJournalEntrySerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def journal_list_create(request):
    if request.method == "GET":
        qs = TradeJournalEntry.objects.filter(user=request.user).order_by("-date", "-created_at")
        serializer = TradeJournalEntrySerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})

    # POST
    serializer = TradeJournalEntrySerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"success": False, "error": "Invalid data", "details": serializer.errors}, status=400)
    entry = serializer.save(user=request.user)
    return Response({"success": True, "data": TradeJournalEntrySerializer(entry).data}, status=201)


@api_view(["PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def journal_detail(request, entry_id):
    try:
        entry = TradeJournalEntry.objects.get(id=entry_id, user=request.user)
    except TradeJournalEntry.DoesNotExist:
        return Response({"success": False, "error": "Not found"}, status=404)

    if request.method == "DELETE":
        entry.delete()
        return Response({"success": True})

    # Accept partial updates for both PUT and PATCH (frontend commonly sends partial bodies).
    serializer = TradeJournalEntrySerializer(entry, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({"success": False, "error": "Invalid data", "details": serializer.errors}, status=400)
    entry = serializer.save()
    return Response({"success": True, "data": TradeJournalEntrySerializer(entry).data})

