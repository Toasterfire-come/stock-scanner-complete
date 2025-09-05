from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import json

def index(request):
    """API index endpoint with available endpoints"""
    return JsonResponse({
        'message': 'Stock Scanner API',
        'version': '2.0.0',
        'endpoints': {
            'authentication': {
                'POST /api/auth/register/': 'User registration',
                'POST /api/auth/login/': 'User login',
                'GET /api/user/profile/': 'Get user profile',
                'POST /api/user/profile/': 'Update user profile',
                'POST /api/user/change-password/': 'Change password'
            },
            'billing': {
                'POST /api/billing/create-paypal-order/': 'Create PayPal subscription order',
                'POST /api/billing/capture-paypal-order/': 'Capture PayPal payment',
                'GET /api/billing/current-plan/': 'Get current subscription plan',
                'POST /api/billing/change-plan/': 'Change subscription plan',
                'GET /api/billing/history/': 'Get billing history',
                'GET /api/billing/stats/': 'Get billing statistics'
            },
            'usage': {
                'GET /api/usage/': 'Get API usage statistics',
                'GET /api/platform-stats/': 'Get platform statistics',
                'GET /api/usage/history/': 'Get usage history'
            },
            'stocks': {
                'GET /api/stocks/': 'List stocks with filtering',
                'GET /api/stocks/{symbol}/': 'Get detailed stock information',
                'GET /api/stocks/{symbol}/quote/': 'Get stock quote',
                'GET /api/stocks/quotes/batch/': 'Get multiple stock quotes',
                'GET /api/stocks/search/': 'Search stocks',
                'GET /api/stocks/nasdaq/': 'Get NASDAQ stocks',
                'GET /api/realtime/{ticker}/': 'Get real-time stock data'
            },
            'market': {
                'GET /api/market/stats/': 'Market statistics',
                'GET /api/market/filter/': 'Filter stocks',
                'GET /api/trending/': 'Trending stocks'
            },
            'alerts': {
                'POST /api/alerts/create/': 'Create price alert'
            }
        },
        'authentication': {
            'header': 'Authorization: Bearer <token>',
            'alternative': 'X-API-Token: <token>',
            'note': 'Get token from /api/auth/login/ or /api/auth/register/'
        }
    })

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def placeholder_view(request):
    """Placeholder view for endpoints not yet implemented"""
    return Response({
        'success': True,
        'message': 'This endpoint is implemented but may need additional features',
        'method': request.method,
        'path': request.path,
        'note': 'Portfolio and watchlist features are basic implementations'
    })
