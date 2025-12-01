"""
Lightweight Screener endpoints without DRF dependencies (Windows-safe).
Provides minimal implementations:
- screeners_list_api, screeners_create_api, screeners_detail_api,
  screeners_update_api, screeners_templates_api, screeners_results_api,
  screeners_export_csv_api, screeners_delete_api
"""
from __future__ import annotations

import csv
import io
import json
from typing import Any

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import Screener, Stock


def _fmt_decimal(v: Any):
    try:
        return float(v) if v is not None else None
    except Exception:
        return None


@csrf_exempt
@require_http_methods(["GET"])  # type: ignore
def screeners_list_api(request):
    try:
        try:
            limit = max(1, min(int(request.GET.get("limit", 50)), 200))
        except Exception:
            limit = 50
        qs = Screener.objects.order_by("-updated_at")[:limit]
        data = [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description or "",
                "criteria": s.criteria,
                "is_public": bool(getattr(s, "is_public", False)),
                "updated_at": s.updated_at.isoformat() if getattr(s, "updated_at", None) else None,
                "created_at": s.created_at.isoformat() if getattr(s, "created_at", None) else None,
            }
            for s in qs
        ]
        return JsonResponse({"success": True, "data": data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])  # type: ignore
def screeners_create_api(request):
    try:
        body = json.loads(request.body or "{}")
        name = (body.get("name") or "").strip()[:150]
        if not name:
            return JsonResponse({"success": False, "error": "name required"}, status=400)
        description = (body.get("description") or "").strip()[:500]
        criteria = body.get("criteria") or []
        s = Screener.objects.create(name=name, description=description, criteria=criteria)
        return JsonResponse({"success": True, "data": {"id": s.id, "name": s.name, "criteria": s.criteria}}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "invalid json"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])  # type: ignore
def screeners_detail_api(request, screener_id: str):
    try:
        s = Screener.objects.get(id=screener_id)
        return JsonResponse(
            {
                "success": True,
                "data": {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description or "",
                    "criteria": s.criteria,
                    "is_public": bool(getattr(s, "is_public", False)),
                    "updated_at": s.updated_at.isoformat() if getattr(s, "updated_at", None) else None,
                    "created_at": s.created_at.isoformat() if getattr(s, "created_at", None) else None,
                },
            }
        )
    except Screener.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])  # type: ignore
def screeners_update_api(request, screener_id: str):
    try:
        s = Screener.objects.get(id=screener_id)
        body = json.loads(request.body or "{}")
        changed = False
        for field in ["name", "description", "criteria", "is_public"]:
            if field in body:
                setattr(s, field, body[field])
                changed = True
        if changed:
            s.save()
        return JsonResponse({"success": True, "data": {"id": s.id, "name": s.name, "criteria": s.criteria}})
    except Screener.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])  # type: ignore
def screeners_templates_api(request):
    try:
        templates = [
            {"id": "rsi-oversold", "name": "RSI Oversold (RSI<30)", "criteria": [{"field": "rsi14", "op": "<", "value": 30}]},
            {"id": "ma-crossover", "name": "50/200 MA Bullish Cross", "criteria": [{"field": "ma50_over_ma200", "op": "==", "value": True}]},
        ]
        return JsonResponse({"success": True, "data": templates})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])  # type: ignore
def screeners_results_api(request, screener_id: str):
    try:
        _ = Screener.objects.get(id=screener_id)
        qs = Stock.objects.order_by("-last_updated")[:20]
        data = [
            {
                "ticker": s.ticker,
                "company_name": s.company_name or s.name,
                "current_price": _fmt_decimal(s.current_price),
            }
            for s in qs
        ]
        return JsonResponse({"success": True, "count": len(data), "data": data, "generated_at": timezone.now().isoformat()})
    except Screener.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])  # type: ignore
def screeners_export_csv_api(request, screener_id: str):
    try:
        _ = Screener.objects.get(id=screener_id)
        qs = Stock.objects.order_by("-last_updated")[:100]
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["ticker", "company_name", "current_price"])
        for s in qs:
            w.writerow([s.ticker, s.company_name or s.name, _fmt_decimal(s.current_price) or 0])
        resp = HttpResponse(buf.getvalue(), content_type="text/csv")
        resp["Content-Disposition"] = f'attachment; filename="screener_{screener_id}.csv"'
        return resp
    except Screener.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])  # type: ignore
def screeners_delete_api(request, screener_id: str):
    try:
        s = Screener.objects.get(id=screener_id)
        s.delete()
        return JsonResponse({"success": True})
    except Screener.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
