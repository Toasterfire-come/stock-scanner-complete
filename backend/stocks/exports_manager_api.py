"""
Export Manager API

Provides minimal backend support for:
- Custom report generation + download
- Export history
- Scheduled export configuration (manual run for MVP)
"""

import csv
import io
from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UserExportJob, UserExportSchedule, PortfolioHolding, WatchlistItem, Stock
from .serializers import UserExportJobSerializer, UserExportScheduleSerializer


def _csv_response(content: str, filename: str) -> HttpResponse:
    resp = HttpResponse(content, content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


def _generate_report_csv(user, report_config: dict) -> tuple[str, str]:
    """
    Generate a CSV report based on a subset of requested data sources.
    Returns (csv_text, filename).
    """
    name = (report_config.get("name") or "custom-report").strip()[:120]
    report_type = (report_config.get("type") or "custom").strip()[:80]
    data_sources = report_config.get("data_sources") or []
    if not isinstance(data_sources, list):
        data_sources = []

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Report Name", name])
    writer.writerow(["Report Type", report_type])
    writer.writerow(["Generated At", timezone.now().isoformat()])
    writer.writerow([])

    # Portfolio holdings
    if "portfolio" in data_sources:
        writer.writerow(["Portfolio Holdings"])
        writer.writerow(["symbol", "shares", "average_cost", "current_price", "market_value"])
        for h in PortfolioHolding.objects.filter(portfolio__user=user).select_related("stock")[:5000]:
            writer.writerow([
                getattr(h.stock, "ticker", "") or getattr(h.stock, "symbol", ""),
                str(h.shares or ""),
                str(h.average_cost or ""),
                str(h.current_price or ""),
                str(h.market_value or ""),
            ])
        writer.writerow([])

    # Watchlists
    if "watchlists" in data_sources:
        writer.writerow(["Watchlists"])
        writer.writerow(["watchlist", "symbol", "added_price", "current_price", "price_change_percent"])
        for it in WatchlistItem.objects.filter(watchlist__user=user).select_related("stock", "watchlist")[:5000]:
            writer.writerow([
                it.watchlist.name,
                getattr(it.stock, "ticker", "") or getattr(it.stock, "symbol", ""),
                str(getattr(it, "added_price", "") or ""),
                str(getattr(it, "current_price", "") or ""),
                str(getattr(it, "price_change_percent", "") or ""),
            ])
        writer.writerow([])

    # Market data snapshot (limited)
    if "market_data" in data_sources:
        writer.writerow(["Market Data Snapshot (sample)"])
        writer.writerow(["symbol", "company_name", "current_price", "price_change_percent", "volume", "market_cap"])
        for s in Stock.objects.all().order_by("-market_cap")[:200]:
            writer.writerow([
                s.ticker,
                s.company_name or s.name,
                str(s.current_price or ""),
                str(s.price_change_percent or s.change_percent or ""),
                str(s.volume or ""),
                str(s.market_cap or ""),
            ])
        writer.writerow([])

    filename = f"{name.replace(' ', '_')}-{timezone.now().date().isoformat()}.csv"
    return out.getvalue(), filename


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_custom_report(request):
    cfg = request.data if isinstance(request.data, dict) else {}
    fmt = (cfg.get("format") or "csv").lower()
    if fmt != "csv":
        return Response({"success": False, "error": "Only CSV reports are supported right now."}, status=400)

    job = UserExportJob.objects.create(
        user=request.user,
        name=(cfg.get("name") or "Custom Report").strip()[:200] or "Custom Report",
        type="custom_report",
        format="csv",
        status="processing",
        payload=cfg,
        content_type="text/csv",
    )

    try:
        csv_text, filename = _generate_report_csv(request.user, cfg)
        job.content_text = csv_text
        job.filename = filename
        job.status = "completed"
        job.completed_at = timezone.now()
        job.save()
        return Response({"success": True, "report_id": str(job.id), "job": UserExportJobSerializer(job).data})
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.completed_at = timezone.now()
        job.save()
        return Response({"success": False, "error": "Failed to generate report"}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_report(request, report_id):
    try:
        job = UserExportJob.objects.get(id=report_id, user=request.user)
    except UserExportJob.DoesNotExist:
        return Response({"success": False, "error": "Report not found"}, status=404)

    if job.status != "completed" or not job.content_text:
        return Response({"success": False, "error": "Report not ready"}, status=400)

    job.download_count = int(job.download_count or 0) + 1
    job.save(update_fields=["download_count"])
    return _csv_response(job.content_text, job.filename or f"report-{job.id}.csv")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_history(request):
    qs = UserExportJob.objects.filter(user=request.user).order_by("-created_at")[:200]
    return Response({"success": True, "data": UserExportJobSerializer(qs, many=True).data})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def schedules_list_create(request):
    if request.method == "GET":
        qs = UserExportSchedule.objects.filter(user=request.user).order_by("-created_at")[:200]
        return Response({"success": True, "data": UserExportScheduleSerializer(qs, many=True).data})

    serializer = UserExportScheduleSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"success": False, "error": "Invalid data", "details": serializer.errors}, status=400)
    sched = serializer.save(user=request.user)
    return Response({"success": True, "data": UserExportScheduleSerializer(sched).data}, status=201)


@api_view(["PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def schedules_detail(request, schedule_id: int):
    try:
        sched = UserExportSchedule.objects.get(id=schedule_id, user=request.user)
    except UserExportSchedule.DoesNotExist:
        return Response({"success": False, "error": "Not found"}, status=404)

    if request.method == "DELETE":
        sched.delete()
        return Response({"success": True})

    serializer = UserExportScheduleSerializer(sched, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({"success": False, "error": "Invalid data", "details": serializer.errors}, status=400)
    sched = serializer.save()
    return Response({"success": True, "data": UserExportScheduleSerializer(sched).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def schedules_run_now(request, schedule_id: int):
    try:
        sched = UserExportSchedule.objects.get(id=schedule_id, user=request.user)
    except UserExportSchedule.DoesNotExist:
        return Response({"success": False, "error": "Not found"}, status=404)

    # Create a simple job record; for MVP, generate a CSV immediately.
    job_cfg = {
        "name": sched.name,
        "type": sched.export_type,
        "format": sched.format,
        "data_sources": ["portfolio"] if sched.export_type == "portfolio" else (
            ["watchlists"] if sched.export_type == "watchlist" else ["market_data"]
        ),
    }
    job = UserExportJob.objects.create(
        user=request.user,
        name=sched.name,
        type=sched.export_type,
        format="csv",
        status="processing",
        payload=job_cfg,
        content_type="text/csv",
    )
    try:
        csv_text, filename = _generate_report_csv(request.user, job_cfg)
        job.content_text = csv_text
        job.filename = filename
        job.status = "completed"
        job.completed_at = timezone.now()
        job.save()
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.completed_at = timezone.now()
        job.save()

    sched.last_run_at = timezone.now()
    sched.run_count = int(sched.run_count or 0) + 1
    # Approximate next run (best-effort)
    sched.next_run_at = timezone.now() + (timedelta(days=1) if sched.frequency == "daily" else timedelta(days=7) if sched.frequency == "weekly" else timedelta(days=30))
    sched.save(update_fields=["last_run_at", "run_count", "next_run_at"])

    return Response({"success": True, "job": UserExportJobSerializer(job).data, "schedule": UserExportScheduleSerializer(sched).data})

