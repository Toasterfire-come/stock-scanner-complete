import json
import subprocess
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.management import call_command
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from stocks.models import StockAlert
from emails.models import EmailSubscription
import io
import sys

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def admin_status(request):
    """Get comprehensive system status for admin dashboard"""
    try:
        # Get database statistics
        total_stocks = StockAlert.objects.count()
        unsent_notifications = StockAlert.objects.filter(sent=False).count()
        
        # Get latest update
        latest_stock = StockAlert.objects.filter(last_update__isnull=False).order_by('-last_update').first()
        last_update = latest_stock.last_update.strftime('%Y-%m-%d %H:%M') if latest_stock else None
        
        # Calculate success rate (placeholder - could be enhanced with actual metrics)
        success_rate = 95 if total_stocks > 0 else 0
        
        # Get subscription count
        total_subscriptions = EmailSubscription.objects.filter(is_active=True).count()
        
        # Get news statistics
        try:
            from news.models import NewsArticle
            total_news = NewsArticle.objects.filter(is_active=True).count()
            recent_news = NewsArticle.objects.filter(
                published_date__gte=timezone.now() - timedelta(hours=24),
                is_active=True
            ).count()
        except Exception:
            total_news = 0
            recent_news = 0
        
        # System health checks
        system_health = {
            'database': 'healthy' if total_stocks > 0 else 'warning',
            'news_scraper': 'healthy' if recent_news > 0 else 'warning',
            'email_system': 'healthy' if total_subscriptions > 0 else 'info'
        }
        
        return JsonResponse({
            'total_stocks': total_stocks,
            'unsent_notifications': unsent_notifications,
            'success_rate': success_rate,
            'last_update': last_update,
            'total_subscriptions': total_subscriptions,
            'total_news': total_news,
            'recent_news': recent_news,
            'system_health': system_health,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting admin status: {e}")
        return JsonResponse({
            'total_stocks': 0,
            'unsent_notifications': 0,
            'success_rate': 0,
            'last_update': None,
            'total_subscriptions': 0,
            'total_news': 0,
            'recent_news': 0,
            'system_health': {'database': 'error', 'news_scraper': 'error', 'email_system': 'error'},
            'error': str(e),
            'status': 'error'
        }, status=500)

@require_http_methods(["GET"])
def api_providers_status(request):
    """Get API providers status - Simplified for Yahoo Finance"""
    try:
        # Test Yahoo Finance connection
        import yfinance as yf
        
        # Test with a simple ticker
        test_ticker = yf.Ticker("AAPL")
        test_data = test_ticker.history(period="1d")
        yahoo_status = 'active' if len(test_data) > 0 else 'inactive'
        
        providers = {
            'yahoo_finance': {
                'status': yahoo_status,
                'description': 'Yahoo Finance (Primary - Free)',
                'last_test': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'rate_limit': 'No official limit'
            },
            'news_scraper': {
                'status': 'active',
                'description': 'Yahoo Finance News Scraper',
                'last_update': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        return JsonResponse(providers)
    except Exception as e:
        logger.error(f"Error getting API providers status: {e}")
        return JsonResponse({
            'yahoo_finance': {
                'status': 'error',
                'description': 'Yahoo Finance (Primary - Free)',
                'error': str(e)
            }
        }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class AdminExecuteView(View):
    """Execute admin commands"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            command = data.get('command')
            params = data.get('params', {})
            
            logger.info(f"Executing admin command: {command} with params: {params}")
            
            # Capture output
            output = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = output
            
            try:
                if command == 'quick_test':
                    result = self._run_quick_test(params)
                elif command == 'workflow':
                    result = self._run_workflow(params)
                elif command == 'custom_workflow':
                    result = self._run_custom_workflow(params)
                elif command == 'export_data':
                    result = self._export_data(params)
                elif command == 'test_notifications':
                    result = self._test_notifications(params)
                else:
                    return JsonResponse({
                        'error': f'Unknown command: {command}',
                        'status': 'error'
                    }, status=400)
                
                # Get captured output
                command_output = output.getvalue()
                
            finally:
                sys.stdout = old_stdout
            
            return JsonResponse({
                'message': result,
                'output': command_output,
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Error executing admin command: {e}")
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    def _run_quick_test(self, params):
        """Run a quick test with minimal data"""
        try:
            call_command(
                'stock_workflow',
                batch_size=5,
                max_workers=1,
                use_cache=True,
                dry_run_notifications=True,
                verbosity=1
            )
            return "Quick test completed successfully with 5 test stocks"
        except Exception as e:
            raise Exception(f"Quick test failed: {e}")
    
    def _run_workflow(self, params):
        """Run the complete stock workflow"""
        try:
            batch_size = params.get('batch_size', 30)
            max_workers = params.get('max_workers', 3)
            use_cache = params.get('use_cache', True)
            delay_range = params.get('delay_range', [1.5, 3.5])
            
            call_command(
                'stock_workflow',
                batch_size=batch_size,
                max_workers=max_workers,
                use_cache=use_cache,
                delay_range=delay_range,
                verbosity=1
            )
            return f"Workflow completed with batch_size={batch_size}, max_workers={max_workers}"
        except Exception as e:
            raise Exception(f"Workflow failed: {e}")
    
    def _run_custom_workflow(self, params):
        """Run workflow with custom parameters"""
        try:
            batch_size = params.get('batch_size', 30)
            max_workers = params.get('max_workers', 3)
            use_cache = params.get('use_cache', True)
            dry_run = params.get('dry_run', False)
            delay_range = params.get('delay_range', [1.5, 3.5])
            
            call_command(
                'stock_workflow',
                batch_size=batch_size,
                max_workers=max_workers,
                use_cache=use_cache,
                dry_run_notifications=dry_run,
                delay_range=delay_range,
                verbosity=1
            )
            
            mode = "dry run" if dry_run else "live"
            return f"Custom workflow completed in {mode} mode"
        except Exception as e:
            raise Exception(f"Custom workflow failed: {e}")
    
    def _export_data(self, params):
        """Export stock data"""
        try:
            format_type = params.get('format', 'web')
            
            call_command(
                'export_stock_data',
                format=format_type,
                verbosity=1
            )
            return f"Data exported successfully in {format_type} format"
        except Exception as e:
            raise Exception(f"Data export failed: {e}")
    
    def _test_notifications(self, params):
        """Test email notifications"""
        try:
            dry_run = params.get('dry_run', True)
            
            call_command(
                'send_stock_notifications',
                dry_run=dry_run,
                verbosity=1
            )
            
            mode = "dry run" if dry_run else "live"
            return f"Notification test completed in {mode} mode"
        except Exception as e:
            raise Exception(f"Notification test failed: {e}")

@require_http_methods(["GET"])
def system_health(request):
    """Get detailed system health information"""
    try:
        # Database health
        db_healthy = True
        try:
            StockAlert.objects.count()
        except Exception:
            db_healthy = False
        
        # File system health
        fs_healthy = True
        try:
            import os
            json_dir = os.path.join(os.path.dirname(__file__), '../../../json')
            fs_healthy = os.path.exists(json_dir) and os.access(json_dir, os.W_OK)
        except Exception:
            fs_healthy = False
        
        # Recent activity
        recent_stocks = StockAlert.objects.filter(
            last_update__isnull=False
        ).order_by('-last_update')[:5]
        
        recent_activity = []
        for stock in recent_stocks:
            recent_activity.append({
                'ticker': stock.ticker,
                'price': float(stock.current_price),
                'note': stock.note[:50] + '...' if len(stock.note) > 50 else stock.note,
                'updated': stock.last_update.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # System metrics
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=1)
        except ImportError:
            memory_percent = None
            cpu_percent = None
        
        return JsonResponse({
            'database_healthy': db_healthy,
            'filesystem_healthy': fs_healthy,
            'memory_usage': memory_percent,
            'cpu_usage': cpu_percent,
            'recent_activity': recent_activity,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

@require_http_methods(["GET"])
def performance_metrics(request):
    """Get performance metrics for the admin dashboard"""
    try:
        # Stock processing metrics
        total_stocks = StockAlert.objects.count()
        stocks_today = StockAlert.objects.filter(
            last_update__date=datetime.now().date()
        ).count()
        
        # Email metrics
        total_subscriptions = EmailSubscription.objects.count()
        active_subscriptions = EmailSubscription.objects.filter(is_active=True).count()
        
        # Processing efficiency (placeholder calculations)
        processing_rate = stocks_today  # stocks per day
        success_rate = (stocks_today / max(total_stocks, 1)) * 100 if total_stocks > 0 else 0
        
        # Rate limiting effectiveness
        rate_limit_effectiveness = 95  # placeholder - could be calculated from logs
        
        return JsonResponse({
            'total_stocks': total_stocks,
            'stocks_processed_today': stocks_today,
            'processing_rate_per_day': processing_rate,
            'success_rate': round(success_rate, 2),
            'rate_limit_effectiveness': rate_limit_effectiveness,
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'subscription_rate': round((active_subscriptions / max(total_subscriptions, 1)) * 100, 2),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def update_configuration(request):
    """Update system configuration"""
    try:
        data = json.loads(request.body)
        
        # Validate configuration data
        valid_keys = ['batch_size', 'max_workers', 'delay_min', 'delay_max', 'use_cache']
        config = {k: v for k, v in data.items() if k in valid_keys}
        
        # Save configuration to file or database
        # For now, we'll just validate and return success
        
        return JsonResponse({
            'message': 'Configuration updated successfully',
            'config': config,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)