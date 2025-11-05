"""
Matomo proxy views to serve tracker from our domain and forward hits to upstream Matomo.

Why: some browsers block third-party trackers; serving from first-party domain improves reliability.
Config env:
  MATOMO_UPSTREAM_URL (e.g., https://matomo.example.com/)
  MATOMO_SITE_ID (string)

Endpoints:
  GET /api/matomo/matomo.js        -> proxies upstream matomo.js
  GET /api/matomo/matomo.php       -> proxies upstream tracking pixel
  POST /api/matomo/matomo.php      -> proxies event payload
"""
import os
import requests
from urllib.parse import urljoin
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

UPSTREAM = (os.environ.get('MATOMO_UPSTREAM_URL') or '').strip()


def _up(url_path: str) -> str:
    base = UPSTREAM
    if not base:
        # fallback typical path
        base = 'http://127.0.0.1:8088/'
    if not base.endswith('/'):
        base += '/'
    return urljoin(base, url_path.lstrip('/'))


def _passthrough_headers(resp):
    h = {}
    # Minimal safe headers
    for k in ['Content-Type', 'Content-Length', 'Cache-Control', 'ETag', 'Last-Modified']:
        if k in resp.headers:
            h[k] = resp.headers[k]
    return h


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def matomo_js(request):
    try:
        upstream = _up('matomo.js')
        r = requests.get(upstream, timeout=10)
        return HttpResponse(r.content, status=r.status_code, content_type=r.headers.get('Content-Type', 'application/javascript'))
    except Exception as e:
        return HttpResponse('// matomo proxy failed', status=503, content_type='application/javascript')


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def matomo_php(request):
    try:
        # Forward query/body as-is
        upstream = _up('matomo.php')
        if request.method == 'GET':
            r = requests.get(upstream, params=request.GET, timeout=10)
        else:
            body = request.body
            headers = {'Content-Type': request.META.get('CONTENT_TYPE', 'application/x-www-form-urlencoded')}
            r = requests.post(upstream, params=request.GET, data=body, headers=headers, timeout=10)
        resp = HttpResponse(r.content, status=r.status_code)
        for k, v in _passthrough_headers(r).items():
            resp[k] = v
        return resp
    except Exception as e:
        return JsonResponse({'success': False}, status=503)
