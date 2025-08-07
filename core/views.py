from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def homepage(request):
    """Homepage view with API information"""
    context = {
        'title': 'Stock Scanner - NASDAQ Data API',
        'version': '1.0.0',
        'endpoints': [
            {'url': '/admin/', 'description': 'Django Admin Panel'},
            {'url': '/api/stocks/', 'description': 'Stock Data API'},
            {'url': '/docs/', 'description': 'API Documentation'},
            {'url': '/revenue/revenue-analytics/', 'description': 'Revenue Analytics'},
        ]
    }
    return render(request, 'core/homepage.html', context)

def api_documentation(request):
    """API documentation page"""
    return render(request, 'api/documentation.html')

@csrf_exempt
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'database': 'connected',
        'version': '1.0.0',
        'endpoints': {
            'stocks': '/api/stocks/',
            'health': '/api/health/',
            'revenue': '/revenue/revenue-analytics/',
            'docs': '/docs/',
        }
    })
