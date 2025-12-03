"""
AI Chat API for Strategy Refinement (Phase 4 Enhancement)
Conversational interface for backtesting strategy development
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services.groq_backtesting_service import GroqBacktestingService


@csrf_exempt
@require_http_methods(["POST"])
def chat_strategy(request):
    """
    POST /api/backtesting/chat/
    
    Have a conversation with AI to refine trading strategy.
    
    Body:
    {
        "message": "User's message",
        "conversation_history": [{"role": "user/assistant", "content": "..."}],
        "category": "day_trading/swing_trading/long_term"
    }
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        history = data.get('conversation_history', [])
        category = data.get('category', 'swing_trading')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Message is required'
            }, status=400)
        
        service = GroqBacktestingService()
        
        if not service.is_ai_available:
            return JsonResponse({
                'success': False,
                'error': 'AI service not available. Please check GROQ_API_KEY.',
                'ai_available': False
            }, status=503)
        
        result = service.refine_strategy_conversation(history, message)
        
        return JsonResponse({
            'success': True,
            'response': result['response'],
            'understanding_complete': result['understanding_complete'],
            'understanding': result['understanding'],
            'ai_available': True
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def understand_strategy(request):
    """
    POST /api/backtesting/understand/
    
    Get AI understanding of a strategy without generating code.
    
    Body:
    {
        "strategy_text": "Strategy description",
        "category": "day_trading/swing_trading/long_term"
    }
    """
    try:
        data = json.loads(request.body)
        strategy_text = data.get('strategy_text', '')
        category = data.get('category', 'swing_trading')
        
        if not strategy_text:
            return JsonResponse({
                'success': False,
                'error': 'Strategy text is required'
            }, status=400)
        
        service = GroqBacktestingService()
        understanding = service.understand_strategy(strategy_text, category)
        
        return JsonResponse({
            'success': True,
            'understanding': understanding,
            'ai_available': service.is_ai_available
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_code(request):
    """
    POST /api/backtesting/generate-code/
    
    Generate backtesting code from strategy.
    
    Body:
    {
        "strategy_text": "Strategy description",
        "category": "day_trading/swing_trading/long_term",
        "understanding": {} (optional - pre-computed understanding)
    }
    """
    try:
        data = json.loads(request.body)
        strategy_text = data.get('strategy_text', '')
        category = data.get('category', 'swing_trading')
        understanding = data.get('understanding')
        
        if not strategy_text:
            return JsonResponse({
                'success': False,
                'error': 'Strategy text is required'
            }, status=400)
        
        service = GroqBacktestingService()
        code, error, ai_understanding = service.generate_strategy_code(
            strategy_text, category, understanding
        )
        
        if error:
            return JsonResponse({
                'success': False,
                'error': error,
                'understanding': ai_understanding,
                'ai_available': service.is_ai_available
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'code': code,
            'understanding': ai_understanding,
            'ai_available': service.is_ai_available
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def check_ai_status(request):
    """
    GET /api/backtesting/ai-status/
    
    Check if AI service is available.
    """
    service = GroqBacktestingService()
    
    return JsonResponse({
        'success': True,
        'ai_available': service.is_ai_available,
        'model': service.model if service.is_ai_available else None
    })
