from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
import json
import uuid

from .models import CustomIndicator


def _uid() -> str:
    return uuid.uuid4().hex


def _safe_json(body):
    try:
        return json.loads(body) if body else {}
    except json.JSONDecodeError:
        return {}


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def list_indicators(request):
    qs = CustomIndicator.objects.filter(user=request.user).order_by('-updated_at')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    p = Paginator(qs, limit)
    items = [model_to_dict(obj, fields=['id','name','mode','privacy','version','created_at','updated_at']) for obj in p.get_page(page)]
    return JsonResponse({ 'success': True, 'data': items, 'pagination': { 'page': page, 'pages': p.num_pages, 'total': p.count } })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_indicator(request):
    data = _safe_json(request.body)
    name = (data.get('name') or '').strip()[:150]
    mode = (data.get('mode') or 'formula').lower()
    if mode not in ['formula','js']:
        mode = 'formula'
    formula = data.get('formula') or ''
    js_code = data.get('jsCode') or data.get('js_code') or ''
    params = data.get('params') or []
    palette = data.get('palette') or {}
    privacy = (data.get('privacy') or 'private').lower()
    if privacy not in ['private','unlisted','public']:
        privacy = 'private'
    if not name:
        return JsonResponse({ 'success': False, 'error': 'name required' }, status=400)
    cid = _uid()
    obj = CustomIndicator.objects.create(
        id=cid,
        user=request.user,
        name=name,
        mode=mode,
        formula=formula,
        js_code=js_code,
        params=params,
        palette=palette,
        privacy=privacy,
        version=1,
    )
    d = model_to_dict(obj)
    return JsonResponse({ 'success': True, 'data': d }, status=201)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_indicator(request, indicator_id: str):
    try:
        obj = CustomIndicator.objects.get(id=indicator_id, user=request.user)
    except CustomIndicator.DoesNotExist:
        return JsonResponse({ 'success': False, 'error': 'Not found' }, status=404)
    d = model_to_dict(obj)
    return JsonResponse({ 'success': True, 'data': d })


@csrf_exempt
@require_http_methods(["PUT","PATCH"])]
@login_required
def update_indicator(request, indicator_id: str):
    try:
        obj = CustomIndicator.objects.get(id=indicator_id, user=request.user)
    except CustomIndicator.DoesNotExist:
        return JsonResponse({ 'success': False, 'error': 'Not found' }, status=404)
    data = _safe_json(request.body)
    changed = False
    for field in ['name','mode','formula','js_code','params','palette','privacy']:
        key_client = field
        if field == 'js_code':
            key_client = 'jsCode'
        if key_client in data:
            setattr(obj, field, data[key_client])
            changed = True
    if changed:
        obj.version = int(obj.version or 1) + 1
        obj.updated_at = timezone.now()
        obj.save()
    d = model_to_dict(obj)
    return JsonResponse({ 'success': True, 'data': d })


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_indicator(request, indicator_id: str):
    try:
        obj = CustomIndicator.objects.get(id=indicator_id, user=request.user)
    except CustomIndicator.DoesNotExist:
        return JsonResponse({ 'success': False, 'error': 'Not found' }, status=404)
    obj.delete()
    return JsonResponse({ 'success': True })
