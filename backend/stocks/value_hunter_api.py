"""
API endpoints for Value Hunter Portfolio (Phase 5)
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .services.value_hunter_service import ValueHunterService


@csrf_exempt
@require_http_methods(["GET"])
def get_current_week(request):
    """Get or create the current Value Hunter week"""
    try:
        service = ValueHunterService()
        week = service.get_or_create_week()
        
        summary = service.get_portfolio_summary(week.year, week.week_number)
        
        return JsonResponse({
            'success': True,
            'week': summary
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_week(request, year, week_number):
    """Get a specific Value Hunter week"""
    try:
        service = ValueHunterService()
        summary = service.get_portfolio_summary(int(year), int(week_number))
        
        if 'error' in summary:
            return JsonResponse({
                'success': False,
                'error': summary['error']
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'week': summary
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_all_weeks(request):
    """List all Value Hunter weeks"""
    try:
        service = ValueHunterService()
        weeks = service.get_all_weeks_summary()
        
        return JsonResponse({
            'success': True,
            'weeks': weeks
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def execute_entry(request):
    """Execute portfolio entry for current week (Monday 9:35 AM ET)"""
    try:
        data = json.loads(request.body) if request.body else {}
        year = data.get('year')
        week_number = data.get('week_number')
        
        service = ValueHunterService()
        week = service.get_or_create_week(year, week_number)
        
        # Check if already executed
        if week.status != 'pending':
            return JsonResponse({
                'success': False,
                'error': f'Week is already {week.status}. Cannot execute entry.'
            }, status=400)
        
        result = service.execute_entry(week)
        
        if not result['success']:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'message': f"Entry executed for week {week.week_number} of {week.year}",
            'positions': result['positions'],
            'symbols': result['symbols']
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def execute_exit(request):
    """Execute portfolio exit for current week (Friday 3:55 PM ET)"""
    try:
        data = json.loads(request.body) if request.body else {}
        year = data.get('year')
        week_number = data.get('week_number')
        
        service = ValueHunterService()
        
        if year and week_number:
            from .models import ValueHunterWeek
            week = ValueHunterWeek.objects.get(year=year, week_number=week_number)
        else:
            year, week_number = service.get_current_week()
            week = service.get_or_create_week(year, week_number)
        
        # Check if active
        if week.status != 'active':
            return JsonResponse({
                'success': False,
                'error': f'Week is {week.status}. Can only exit active weeks.'
            }, status=400)
        
        result = service.execute_exit(week)
        
        if not result['success']:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'message': f"Exit executed for week {week.week_number} of {week.year}",
            'starting_capital': result['starting_capital'],
            'ending_capital': result['ending_capital'],
            'weekly_return': result['weekly_return'],
            'positions_closed': result['positions_closed']
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_top_stocks(request):
    """Get current top 10 undervalued stocks"""
    try:
        service = ValueHunterService()
        stocks = service.select_top_stocks(limit=10)
        
        return JsonResponse({
            'success': True,
            'stocks': [
                {
                    'ticker': stock.ticker,
                    'name': stock.company_name or stock.name,
                    'current_price': float(stock.current_price) if stock.current_price else None,
                    'valuation_score': float(stock.fundamentals.valuation_score) if hasattr(stock, 'fundamentals') and stock.fundamentals else None,
                    'market_cap': stock.market_cap,
                    'volume': stock.volume
                }
                for stock in stocks
            ]
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
