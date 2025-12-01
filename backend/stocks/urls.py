from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import views, views_health
from . import simple_market_api
from . import simple_screeners_api
from . import alerts_api
from .wordpress_api import WordPressStockView, WordPressNewsView, WordPressAlertsView
from .simple_api import SimpleStockView, SimpleNewsView, simple_status_api
from .api_views_fixed import trigger_stock_update, trigger_news_update
from . import logs_api
from . import revenue_views
try:
    from .billing_api import cancel_subscription_api, paypal_plans_meta_api, developer_usage_stats_api
except Exception as _billing_import_err:  # Graceful fallback if optional deps (DRF) missing
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    from django.views.decorators.http import require_http_methods

    @csrf_exempt
    @require_http_methods(["GET"])  # type: ignore
    def paypal_plans_meta_api(request):  # type: ignore
        return JsonResponse({
            'success': False,
            'error': 'Billing module unavailable',
            'details': str(_billing_import_err)
        }, status=503)

    @csrf_exempt
    @require_http_methods(["POST"])  # type: ignore
    def cancel_subscription_api(request):  # type: ignore
        return JsonResponse({
            'success': False,
            'error': 'Billing module unavailable',
            'details': str(_billing_import_err)
        }, status=503)

    @csrf_exempt
    @require_http_methods(["GET"])  # type: ignore
    def developer_usage_stats_api(request):  # type: ignore
        return JsonResponse({
            'success': False,
            'error': 'Billing module unavailable',
            'details': str(_billing_import_err)
        }, status=503)
from . import indicators_api
from . import enterprise_api
from . import admin_api
from . import matomo_proxy
from django.conf import settings
from django.utils import timezone
import hashlib
from django.shortcuts import redirect
from . import partner_analytics_api
from . import valuation_api
from . import valuation_endpoints
from . import charting_api
from . import backtesting_api
from . import value_hunter_api



# Lazy loader for api_views with safe fallbacks so Windows environments start reliably
def _lazy_api(name, fallback=None):
    @csrf_exempt
    def _view(request, *args, **kwargs):
        try:
            from . import api_views as _av  # Import on-demand to avoid module load failures
            view_func = getattr(_av, name, None)
            if callable(view_func):
                return view_func(request, *args, **kwargs)
        except Exception:
            # Swallow import/attribute errors and fall back
            pass
        if fallback is not None:
            return fallback(request, *args, **kwargs)
        return JsonResponse({'success': False, 'error': f'{name} unavailable'}, status=503)
    return _view


@csrf_exempt
def _stock_insiders_fallback(request, ticker: str):
    return JsonResponse({'success': True, 'ticker': ticker.upper(), 'insiders': []})


# Market endpoints with robust fallback to lightweight implementations
top_gainers_view = _lazy_api('top_gainers_api', fallback=simple_market_api.top_gainers_api)
top_losers_view = _lazy_api('top_losers_api', fallback=simple_market_api.top_losers_api)
most_active_view = _lazy_api('most_active_api', fallback=simple_market_api.most_active_api)

# Generic lazy wrappers for api_views endpoints
stock_detail_view = _lazy_api('stock_detail_api')
stock_search_view = _lazy_api('stock_search_api')
stock_list_view = _lazy_api('stock_list_api')
filter_stocks_view = _lazy_api('filter_stocks_api')
stock_statistics_view = _lazy_api('stock_statistics_api')
market_stats_view = _lazy_api('market_stats_api')
realtime_stock_view = _lazy_api('realtime_stock_api')
trending_stocks_view = _lazy_api('trending_stocks_api')

# Screener endpoints
screeners_list_view = _lazy_api('screeners_list_api', fallback=simple_screeners_api.screeners_list_api)
screeners_create_view = _lazy_api('screeners_create_api', fallback=simple_screeners_api.screeners_create_api)
screeners_templates_view = _lazy_api('screeners_templates_api', fallback=simple_screeners_api.screeners_templates_api)
screeners_update_view = _lazy_api('screeners_update_api', fallback=simple_screeners_api.screeners_update_api)
screeners_results_view = _lazy_api('screeners_results_api', fallback=simple_screeners_api.screeners_results_api)
screeners_export_csv_view = _lazy_api('screeners_export_csv_api', fallback=simple_screeners_api.screeners_export_csv_api)
screeners_delete_view = _lazy_api('screeners_delete_api', fallback=simple_screeners_api.screeners_delete_api)
screeners_detail_view = _lazy_api('screeners_detail_api', fallback=simple_screeners_api.screeners_detail_api)

# Other endpoints requiring api_views
stock_insiders_view = _lazy_api('stock_insiders_api', fallback=_stock_insiders_fallback)
export_stocks_csv_view = _lazy_api('export_stocks_csv_api')
export_portfolio_csv_view = _lazy_api('export_portfolio_csv_api')
export_watchlist_csv_view = _lazy_api('export_watchlist_csv_api')
reports_download_view = _lazy_api('reports_download_api')
share_watchlist_public_view = _lazy_api('share_watchlist_public')
share_portfolio_public_view = _lazy_api('share_portfolio_public')
share_watchlist_export_view = _lazy_api('share_watchlist_export')
share_portfolio_export_view = _lazy_api('share_portfolio_export')
share_watchlist_copy_view = _lazy_api('share_watchlist_copy')
share_portfolio_copy_view = _lazy_api('share_portfolio_copy')
share_watchlist_create_link_view = _lazy_api('share_watchlist_create_link')
share_portfolio_create_link_view = _lazy_api('share_portfolio_create_link')
total_tickers_view = _lazy_api('total_tickers_api')
gainers_losers_stats_view = _lazy_api('gainers_losers_stats_api')
total_alerts_view = _lazy_api('total_alerts_api')
portfolio_value_view = _lazy_api('portfolio_value_api')
portfolio_pnl_view = _lazy_api('portfolio_pnl_api')
portfolio_return_view = _lazy_api('portfolio_return_api')
portfolio_holdings_count_view = _lazy_api('portfolio_holdings_count_api')
wordpress_subscription_view = _lazy_api('wordpress_subscription_api')

urlpatterns = [
    # Health check endpoints (must be first for monitoring)
    path('health/', views_health.health_check, name='health_check'),
    path('health/detailed/', views_health.health_check_detailed, name='health_check_detailed'),
    path('health/ready/', views_health.readiness_check, name='readiness_check'),
    path('health/live/', views_health.liveness_check, name='liveness_check'),
    
    # Status endpoint (required by problem statement)  
    path('status/', simple_status_api, name='api_status'),
    
    # Basic API endpoint
    path('', views.index, name='index'),
    
    # Include authentication and user management endpoints
    path('', include('stocks.auth_urls')),
    
    # Stock data endpoints - using lazy-loaded api_views functions
    path('stock/<str:ticker>/', stock_detail_view, name='stock_detail'),
    # WordPress and search aliases should come BEFORE the generic stocks/<ticker> route
    path('stocks/search/', stock_search_view, name='stock_search_wp'),
    path('search/', stock_search_view, name='stock_search'),
    
    # NEW STOCK CATEGORY ENDPOINTS (must come before stocks/<ticker>/)
    path('stocks/top-gainers/', top_gainers_view, name='top_gainers'),
    path('stocks/top-losers/', top_losers_view, name='top_losers'),
    path('stocks/most-active/', most_active_view, name='most_active'),
    
    # Screener endpoints (static routes MUST come before dynamic <screener_id> routes)
    path('screeners/', screeners_list_view, name='screeners_list'),
    path('screeners/create/', screeners_create_view, name='screeners_create'),
    path('screeners/templates/', screeners_templates_view, name='screeners_templates'),
    path('screeners/<str:screener_id>/update/', screeners_update_view, name='screeners_update'),
    path('screeners/<str:screener_id>/results/', screeners_results_view, name='screeners_results'),
    path('screeners/<str:screener_id>/export.csv', screeners_export_csv_view, name='screeners_export_csv'),
    # delete alias to support client flexibility
    path('screeners/<str:screener_id>/delete/', screeners_delete_view, name='screeners_delete_alias'),
    path('screeners/<str:screener_id>/', screeners_detail_view, name='screeners_detail'),

    # Generic stock endpoints (after specific routes)
    path('stocks/<str:ticker>/', stock_detail_view, name='stock_detail_alias'),
    path('stocks/<str:ticker>/insiders/', stock_insiders_view, name='stock_insiders'),
    # CSV Exports
    path('export/stocks/csv', export_stocks_csv_view, name='export_stocks_csv'),
    path('export/portfolio/csv', export_portfolio_csv_view, name='export_portfolio_csv'),
    path('export/watchlist/csv', export_watchlist_csv_view, name='export_watchlist_csv'),
    # Reports download stub
    path('reports/<str:report_id>/download', reports_download_view, name='reports_download'),

    # Shareable Watchlists & Portfolios
    path('share/watchlists/<str:slug>/', share_watchlist_public_view, name='share_watchlist_public'),
    path('share/portfolios/<str:slug>/', share_portfolio_public_view, name='share_portfolio_public'),
    path('share/watchlists/<str:slug>/export.json', share_watchlist_export_view, name='share_watchlist_export'),
    path('share/portfolios/<str:slug>/export.json', share_portfolio_export_view, name='share_portfolio_export'),
    path('share/watchlists/<str:slug>/copy', share_watchlist_copy_view, name='share_watchlist_copy'),
    path('share/portfolios/<str:slug>/copy', share_portfolio_copy_view, name='share_portfolio_copy'),
    path('share/watchlists/<str:watchlist_id>/create', share_watchlist_create_link_view, name='share_watchlist_create_link'),
    path('share/portfolios/<str:portfolio_id>/create', share_portfolio_create_link_view, name='share_portfolio_create_link'),
    path('realtime/<str:ticker>/', realtime_stock_view, name='realtime_stock'),
    path('trending/', trending_stocks_view, name='trending_stocks'),
    path('market-stats/', market_stats_view, name='market_stats'),
    # Aliases for platform/frontend compatibility
    path('platform-stats/', market_stats_view, name='platform_stats_alias'),
    path('developer/usage-stats/', developer_usage_stats_api, name='developer_usage_stats'),
    # path('nasdaq/', api_views.nasdaq_stocks_api, name='nasdaq_stocks'),  # Removed: only NYSE in DB
    path('stocks/', stock_list_view, name='stock_list'),
    path('stocks/<str:ticker>/quote/', stock_detail_view, name='stock_quote'),
    path('filter/', filter_stocks_view, name='filter_stocks'),
    path('statistics/', stock_statistics_view, name='stock_statistics'),
    
    # NEW ENDPOINTS REQUESTED BY USER
    # Stats endpoints
    path('stats/total-tickers/', total_tickers_view, name='total_tickers'),
    path('stats/gainers-losers/', gainers_losers_stats_view, name='gainers_losers_stats'),
    path('stats/total-alerts/', total_alerts_view, name='total_alerts'),
    
    # Portfolio endpoints
    path('portfolio/value/', portfolio_value_view, name='portfolio_value'),
    path('portfolio/pnl/', portfolio_pnl_view, name='portfolio_pnl'),
    path('portfolio/return/', portfolio_return_view, name='portfolio_return'),
    path('portfolio/holdings-count/', portfolio_holdings_count_view, name='portfolio_holdings_count'),
    
    # WordPress-friendly endpoints
    path('wordpress/stocks/', WordPressStockView.as_view(), name='wp_stocks'),
    path('wordpress/news/', WordPressNewsView.as_view(), name='wp_news'),
    path('wordpress/alerts/', WordPressAlertsView.as_view(), name='wp_alerts'),
    # Simple API (no DB)
    path('simple/stocks/', SimpleStockView.as_view(), name='simple_stocks'),
    
    # Hosted WP workflow triggers
    path('stocks/update/', trigger_stock_update, name='stocks_update_trigger'),
    path('news/update/', trigger_news_update, name='news_update_trigger'),
    
    # Alerts endpoints (auth required)
    path('alerts/', alerts_api.alerts_list_api, name='alerts_list'),
    path('alerts/create/', alerts_api.alerts_create_api, name='create_alert'),
    path('alerts/<int:alert_id>/toggle/', alerts_api.alerts_toggle_api, name='toggle_alert'),
    path('alerts/<int:alert_id>/delete/', alerts_api.alerts_delete_api, name='delete_alert'),
    path('alerts/unread-count/', alerts_api.alerts_unread_count_api, name='alerts_unread_count'),
    path('alerts/meta/', alerts_api.alerts_meta_api, name='alerts_meta'),
    
    # Subscription endpoints
    path('subscription/', wordpress_subscription_view, name='wordpress_subscription'),
    path('wordpress/subscribe/', wordpress_subscription_view, name='wp_subscribe'),
    
    # Portfolio endpoints
    path('portfolio/', include('stocks.portfolio_urls')),
    
    # Watchlist endpoints  
    path('watchlist/', include('stocks.watchlist_urls')),
    
    # News endpoints
    path('news/', include('stocks.news_urls')),
    path('sms/', include('stocks.sms_urls')),

    # Revenue and discount endpoints
    path('revenue/', include('stocks.revenue_urls')),
    path('billing/validate-discount/', revenue_views.validate_discount_code, name='validate_discount_code_alt'),
    path('billing/apply-discount/', revenue_views.apply_discount_code, name='apply_discount_code_alt'),

    # Billing and subscription management (PayPal, history, payment methods)
    path('billing/', include('stocks.billing_urls')),

    # Custom Indicators CRUD
    path('indicators/', indicators_api.list_indicators, name='indicators_list'),
    path('indicators/create/', indicators_api.create_indicator, name='indicators_create'),
    path('indicators/<str:indicator_id>/', indicators_api.get_indicator, name='indicators_get'),
    path('indicators/<str:indicator_id>/update/', indicators_api.update_indicator, name='indicators_update'),
    path('indicators/<str:indicator_id>/delete/', indicators_api.delete_indicator, name='indicators_delete'),

    # Enterprise contact/solutions endpoints
    path('enterprise/contact/', enterprise_api.enterprise_contact_api, name='enterprise_contact'),
    path('enterprise/quote-request/', enterprise_api.enterprise_quote_request_api, name='enterprise_quote_request'),
    path('enterprise/solutions/', enterprise_api.enterprise_solutions_api, name='enterprise_solutions'),

    # Logging & monitoring endpoints
    path('logs/client/', logs_api.client_logs_api, name='client_logs'),
    path('logs/metrics/', logs_api.metrics_logs_api, name='metrics_logs'),
    path('logs/security/', logs_api.security_logs_api, name='security_logs'),
    # Admin endpoints (staff only)
    path('admin/metrics/', admin_api.admin_metrics_api, name='admin_metrics'),
    # Matomo proxy (first-party path)
    path('matomo/matomo.js', matomo_proxy.matomo_js, name='matomo_js'),
    path('matomo/matomo.php', matomo_proxy.matomo_php, name='matomo_php'),
    
    # Partner referral redirect: /r/<code>
    path('r/<str:code>/', partner_analytics_api.referral_redirect, name='referral_redirect'),
    # Partner analytics (auth required + gating)
    path('partner/analytics/summary', partner_analytics_api.partner_analytics_summary_api, name='partner_analytics_summary'),
    path('partner/analytics/timeseries', partner_analytics_api.partner_analytics_timeseries_api, name='partner_analytics_timeseries'),
    
    # Valuation endpoints
    path('valuation/<str:ticker>/', valuation_api.get_stock_valuation, name='stock_valuation'),
    path('valuation/<str:ticker>/quick/', valuation_api.get_quick_valuation, name='quick_valuation'),
    path('screener/undervalued/', valuation_api.get_undervalued_screener, name='undervalued_screener'),
    
    # Additional Valuation endpoints (Phase 2)
    path('fundamentals/<str:ticker>/sync/', valuation_endpoints.sync_stock_fundamentals, name='sync_fundamentals'),
    path('valuation/sectors/', valuation_endpoints.get_sector_analysis, name='sector_analysis'),
    path('valuation/top-value/', valuation_endpoints.get_top_value_stocks, name='top_value_stocks'),
    path('valuation/compare/', valuation_endpoints.get_value_comparison, name='value_comparison'),
    
    # Charting endpoints (Phase 3)
    path('chart/<str:ticker>/', charting_api.get_chart_data, name='chart_data'),
    path('chart/<str:ticker>/indicators/', charting_api.get_chart_indicators, name='chart_indicators'),
    path('chart/timeframes/', charting_api.get_available_timeframes, name='chart_timeframes'),
    
    # AI Backtesting endpoints (Phase 4)
    path('backtesting/create/', backtesting_api.create_backtest, name='create_backtest'),
    path('backtesting/<int:backtest_id>/run/', backtesting_api.run_backtest, name='run_backtest'),
    path('backtesting/<int:backtest_id>/', backtesting_api.get_backtest, name='get_backtest'),
    path('backtesting/list/', backtesting_api.list_backtests, name='list_backtests'),
    path('backtesting/baseline-strategies/', backtesting_api.list_baseline_strategies, name='baseline_strategies'),
    
    # Value Hunter endpoints (Phase 5)
    path('value-hunter/current/', value_hunter_api.get_current_week, name='vh_current_week'),
    path('value-hunter/<int:year>/<int:week_number>/', value_hunter_api.get_week, name='vh_get_week'),
    path('value-hunter/list/', value_hunter_api.list_all_weeks, name='vh_list_weeks'),
    path('value-hunter/entry/', value_hunter_api.execute_entry, name='vh_execute_entry'),
    path('value-hunter/exit/', value_hunter_api.execute_exit, name='vh_execute_exit'),
    path('value-hunter/top-stocks/', value_hunter_api.get_top_stocks, name='vh_top_stocks'),
]
