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
from . import paper_trading_api
from . import sms_alert_api
from . import twofa_api
from . import options_api
from . import news_sentiment_api
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
from . import strategy_ranking_api
from . import education_api
from . import social_trading_api
from . import retention_api
from . import system_api
# Weekly challenges (viral engagement)
from . import challenges_api
# NEW MVP Feature APIs
from . import ai_chat_api
from . import enhanced_screener_api
from . import trade_journal_api
from . import exports_manager_api
from . import favorites_api
from . import fast_chart_api
from . import valuation_display_api
from . import grouping_api
from . import achievements_api



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
    # Custom reports + downloads (backed by Export Manager)
    path('reports/custom/', exports_manager_api.create_custom_report, name='reports_custom'),
    path('reports/<uuid:report_id>/download', exports_manager_api.download_report, name='reports_download'),

    # Shareable Watchlists & Portfolios
    path('share/watchlists/<str:slug>/', share_watchlist_public_view, name='share_watchlist_public'),
    path('share/portfolios/<str:slug>/', share_portfolio_public_view, name='share_portfolio_public'),
    path('share/watchlists/<str:slug>/export.json', share_watchlist_export_view, name='share_watchlist_export'),
    path('share/portfolios/<str:slug>/export.json', share_portfolio_export_view, name='share_portfolio_export'),
    path('share/watchlists/<str:slug>/copy', share_watchlist_copy_view, name='share_watchlist_copy'),
    path('share/portfolios/<str:slug>/copy', share_portfolio_copy_view, name='share_portfolio_copy'),
    path('share/watchlists/<str:watchlist_id>/create', share_watchlist_create_link_view, name='share_watchlist_create_link'),
    path('share/portfolios/<str:portfolio_id>/create', share_portfolio_create_link_view, name='share_portfolio_create_link'),
    path('share/portfolios/<str:portfolio_id>/revoke', _lazy_api('share_portfolio_revoke_link'), name='share_portfolio_revoke_link'),
    path('share/watchlists/<str:watchlist_id>/revoke', _lazy_api('share_watchlist_revoke_link'), name='share_watchlist_revoke_link'),
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
    path('indicators/<str:indicator_id>/', indicators_api.indicator_detail_api, name='indicators_detail'),
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
    path('backtesting/<int:backtest_id>/fork/', backtesting_api.fork_backtest, name='fork_backtest'),
    path('backtesting/public/<int:backtest_id>/', backtesting_api.get_public_backtest, name='get_public_backtest'),
    path('backtesting/list/', backtesting_api.list_backtests, name='list_backtests'),
    path('backtesting/baseline-strategies/', backtesting_api.list_baseline_strategies, name='baseline_strategies'),
    path('backtesting/limits/', backtesting_api.get_backtest_limits, name='backtest_limits'),

    # Backtest public sharing (Phase 8)
    path('share/backtests/<int:backtest_id>/create', backtesting_api.create_backtest_share_link, name='share_backtest_create_link'),
    path('share/backtests/<int:backtest_id>/revoke', backtesting_api.revoke_backtest_share_link, name='share_backtest_revoke_link'),
    path('share/backtests/<str:slug>/', backtesting_api.get_shared_backtest, name='share_backtest_public'),
    path('share/backtests/<str:slug>/fork', backtesting_api.fork_shared_backtest, name='share_backtest_fork'),
    
    # Achievement endpoints (Gamification)
    path('achievements/', achievements_api.get_achievements, name='get_achievements'),
    path('achievements/<str:achievement_id>/share/', achievements_api.share_achievement, name='share_achievement'),
    path('achievements/progress/', achievements_api.get_achievement_progress, name='achievement_progress'),

    # Value Hunter endpoints (Phase 5)
    path('value-hunter/current/', value_hunter_api.get_current_week, name='vh_current_week'),
    path('value-hunter/<int:year>/<int:week_number>/', value_hunter_api.get_week, name='vh_get_week'),
    path('value-hunter/list/', value_hunter_api.list_all_weeks, name='vh_list_weeks'),
    path('value-hunter/entry/', value_hunter_api.execute_entry, name='vh_execute_entry'),
    path('value-hunter/exit/', value_hunter_api.execute_exit, name='vh_execute_exit'),
    path('value-hunter/top-stocks/', value_hunter_api.get_top_stocks, name='vh_top_stocks'),
    
    # Strategy Ranking endpoints (Phase 6 - MVP2 v3.4)
    path('strategy-ranking/leaderboard/', strategy_ranking_api.get_strategy_leaderboard, name='strategy_leaderboard'),
    path('strategy-ranking/categories/', strategy_ranking_api.get_leaderboard_categories, name='leaderboard_categories'),
    path('strategy-ranking/my-strategies/', strategy_ranking_api.get_my_strategies, name='my_strategies'),
    path('strategy-ranking/<int:strategy_id>/', strategy_ranking_api.get_strategy_detail, name='strategy_detail'),
    path('strategy-ranking/<int:strategy_id>/clone/', strategy_ranking_api.clone_strategy, name='clone_strategy'),
    path('strategy-ranking/<int:strategy_id>/rate/', strategy_ranking_api.rate_strategy, name='rate_strategy'),
    path('strategy-ranking/<int:strategy_id>/recalculate/', strategy_ranking_api.recalculate_strategy_score, name='recalculate_strategy_score'),

    # Education & Context System endpoints (Phase 7 - MVP2 v3.4)
    path('education/paths/', education_api.get_learning_paths, name='learning_paths'),
    path('education/paths/recommended/', education_api.get_recommended_paths, name='recommended_paths'),
    path('education/paths/<int:path_id>/', education_api.get_learning_path_detail, name='learning_path_detail'),
    path('education/lessons/<int:lesson_id>/', education_api.get_lesson_detail, name='lesson_detail'),
    path('education/lessons/<int:lesson_id>/progress/', education_api.update_lesson_progress, name='update_lesson_progress'),
    path('education/lessons/<int:lesson_id>/quiz/', education_api.submit_quiz, name='submit_quiz'),
    path('education/indicators/', education_api.list_indicators, name='list_indicators'),
    path('education/indicators/<str:indicator_name>/tooltip/', education_api.get_indicator_tooltip, name='indicator_tooltip'),
    path('education/indicators/<str:indicator_name>/', education_api.get_indicator_explanation, name='indicator_explanation'),
    path('education/walkthroughs/active/', education_api.get_active_walkthroughs, name='active_walkthroughs'),
    path('education/walkthroughs/<int:walkthrough_id>/start/', education_api.start_walkthrough, name='start_walkthrough'),

    # Weekly challenges (Phase: Viral Engagement)
    path('challenges/current/', challenges_api.get_current_challenge, name='current_challenge'),
    path('challenges/leaderboard/', challenges_api.get_challenge_leaderboard, name='challenge_leaderboard'),

    # Trade Journal (trade log) endpoints used by the frontend Trading Journal page
    path('journal/', trade_journal_api.journal_list_create, name='trade_journal_list_create'),
    path('journal/<uuid:entry_id>/', trade_journal_api.journal_detail, name='trade_journal_detail'),

    # Export Manager (history + schedules)
    path('exports/history/', exports_manager_api.export_history, name='export_history'),
    path('exports/schedules/', exports_manager_api.schedules_list_create, name='export_schedules_list_create'),
    path('exports/schedules/<int:schedule_id>/', exports_manager_api.schedules_detail, name='export_schedules_detail'),
    path('exports/schedules/<int:schedule_id>/run-now/', exports_manager_api.schedules_run_now, name='export_schedules_run_now'),

    # Favorites (cross-device sync)
    path('favorites/', favorites_api.favorites_list_create, name='favorites_list_create'),
    path('favorites/all/', favorites_api.favorites_clear, name='favorites_clear'),
    path('favorites/<str:ticker>/', favorites_api.favorites_remove, name='favorites_remove'),
    path('education/walkthroughs/<int:walkthrough_id>/update/', education_api.update_walkthrough_step, name='update_walkthrough_step'),
    path('education/walkthroughs/<int:walkthrough_id>/dismiss/', education_api.dismiss_walkthrough, name='dismiss_walkthrough'),
    path('education/kb/search/', education_api.search_knowledge_base, name='search_knowledge_base'),
    path('education/kb/popular/', education_api.get_popular_kb_articles, name='popular_kb_articles'),
    path('education/kb/helpful/', education_api.get_helpful_kb_articles, name='helpful_kb_articles'),
    path('education/kb/<slug:slug>/', education_api.get_kb_article, name='kb_article'),
    path('education/kb/<int:article_id>/feedback/', education_api.submit_kb_feedback, name='submit_kb_feedback'),

    # ============================================================================
    # PHASE 8 - SOCIAL & COPY TRADING (MVP2 v3.4)
    # ============================================================================

    # User Profile endpoints
    path('social/profile/me/', social_trading_api.get_my_profile, name='my_profile'),
    path('social/profile/me/update/', social_trading_api.update_my_profile, name='update_my_profile'),
    path('social/profiles/', social_trading_api.get_public_profiles, name='public_profiles'),
    path('social/profiles/search/', social_trading_api.search_profiles, name='search_profiles'),
    path('social/profile/<int:user_id>/', social_trading_api.get_profile_by_id, name='profile_by_id'),

    # Follow endpoints
    path('social/follow/<int:user_id>/', social_trading_api.follow_user, name='follow_user'),
    path('social/unfollow/<int:user_id>/', social_trading_api.unfollow_user, name='unfollow_user'),
    path('social/followers/', social_trading_api.get_my_followers, name='my_followers'),
    path('social/following/', social_trading_api.get_my_following, name='my_following'),

    # Copy Trading endpoints
    path('social/copy/start/', social_trading_api.start_copy_trading, name='start_copy_trading'),
    path('social/copy/<int:relationship_id>/pause/', social_trading_api.pause_copy_trading, name='pause_copy_trading'),
    path('social/copy/<int:relationship_id>/resume/', social_trading_api.resume_copy_trading, name='resume_copy_trading'),
    path('social/copy/<int:relationship_id>/stop/', social_trading_api.stop_copy_trading, name='stop_copy_trading'),
    path('social/copy/my-relationships/', social_trading_api.get_my_copy_relationships, name='my_copy_relationships'),

    # Strategy Sharing endpoints
    path('social/share/strategy/', social_trading_api.share_strategy, name='share_strategy'),
    path('social/share/<str:share_token>/', social_trading_api.get_shared_strategy, name='get_shared_strategy'),
    path('social/share/<int:share_id>/revoke/', social_trading_api.revoke_share, name='revoke_share'),

    # Referral endpoints
    path('social/referral/apply/', social_trading_api.apply_referral_code, name='apply_referral'),
    path('social/referral/stats/', social_trading_api.get_referral_stats, name='referral_stats'),

    # ============================================================================
    # PHASE 9 - RETENTION & HABITS (MVP2 v3.4)
    # ============================================================================

    # Trading Journal endpoints
    path('journal/create/', retention_api.create_journal_entry, name='create_journal_entry'),
    path('journal/<int:entry_id>/update/', retention_api.update_journal_entry, name='update_journal_entry'),
    path('journal/my-entries/', retention_api.get_my_journal_entries, name='my_journal_entries'),
    path('journal/stats/', retention_api.get_journal_stats, name='journal_stats'),

    # Performance Review endpoints
    path('review/generate/', retention_api.generate_performance_review, name='generate_performance_review'),
    path('review/my-reviews/', retention_api.get_my_performance_reviews, name='my_performance_reviews'),
    path('review/<int:review_id>/', retention_api.get_performance_review, name='get_performance_review'),
    path('review/<int:review_id>/viewed/', retention_api.mark_review_viewed, name='mark_review_viewed'),

    # Custom Indicator endpoints
    path('indicators/custom/create/', retention_api.create_custom_indicator, name='create_custom_indicator'),
    path('indicators/custom/my-indicators/', retention_api.get_my_custom_indicators, name='my_custom_indicators'),
    path('indicators/custom/public/', retention_api.get_public_custom_indicators, name='public_custom_indicators'),

    # Trade Export endpoints
    path('exports/request/', retention_api.request_trade_export, name='request_trade_export'),
    path('exports/my-exports/', retention_api.get_my_exports, name='my_exports'),

    # Alert Template endpoints
    path('alerts/create/', retention_api.create_alert, name='create_alert'),
    path('alerts/<int:alert_id>/update/', retention_api.update_alert, name='update_alert'),
    path('alerts/<int:alert_id>/delete/', retention_api.delete_alert, name='delete_alert'),
    path('alerts/my-alerts/', retention_api.get_my_alerts, name='my_alerts'),

    # Triggered Alert endpoints
    path('alerts/triggered/', retention_api.get_triggered_alerts, name='triggered_alerts'),
    path('alerts/triggered/<int:trigger_id>/acknowledge/', retention_api.acknowledge_alert, name='acknowledge_alert'),

    # ============================================================================
    # NEW MVP FEATURES
    # ============================================================================
    
    # Feature 1: AI Backtester with Groq Chat Integration
    path('backtesting/chat/', ai_chat_api.chat_strategy, name='ai_chat_strategy'),
    path('backtesting/understand/', ai_chat_api.understand_strategy, name='ai_understand_strategy'),
    path('backtesting/generate-code/', ai_chat_api.generate_code, name='ai_generate_code'),
    path('backtesting/ai-status/', ai_chat_api.check_ai_status, name='ai_status'),
    
    # Feature 2: Enhanced Screener - Filter ALL fields
    path('screener/fields/', enhanced_screener_api.get_filter_fields, name='screener_fields'),
    path('screener/filter/', enhanced_screener_api.advanced_filter, name='screener_filter'),
    path('screener/presets/', enhanced_screener_api.get_presets, name='screener_presets'),
    
    # Feature 3: Fast Charting with Quick Updates
    path('chart/<str:ticker>/quote/', fast_chart_api.get_fast_quote, name='fast_quote'),
    path('chart/<str:ticker>/intraday/', fast_chart_api.get_intraday_data, name='intraday_chart'),
    path('chart/<str:ticker>/latest/', fast_chart_api.get_latest_candle, name='latest_candle'),
    path('chart/<str:ticker>/full/', fast_chart_api.get_chart_with_indicators, name='full_chart'),
    path('chart/batch-quotes/', fast_chart_api.batch_quotes, name='batch_quotes'),
    
    # Feature 4: Aesthetic Valuation Display
    path('valuation/<str:ticker>/display/', valuation_display_api.get_valuation_display, name='valuation_display'),
    path('valuation/display/compare/', valuation_display_api.get_valuation_comparison, name='valuation_comparison'),
    path('valuation/sector/<str:sector>/', valuation_display_api.get_sector_valuation, name='sector_valuation'),
    
    # Feature 5: Stock Grouping
    path('groups/create/', grouping_api.create_stock_group, name='create_group'),
    path('groups/<str:group_id>/', grouping_api.get_stock_group, name='get_group'),
    path('groups/<str:group_id>/chart/', grouping_api.get_group_chart, name='group_chart'),
    
    # Feature 6: Stock/Group Comparison
    path('compare/stocks/', grouping_api.compare_stocks, name='compare_stocks'),
    path('compare/groups/', grouping_api.compare_groups, name='compare_groups'),
    path('compare/chart/', grouping_api.get_comparison_chart, name='comparison_chart'),

    # ============================================================================
    # PAPER TRADING SYSTEM (MVP2 v3.4)
    # ============================================================================
    
    # Paper Trading Account Management
    path('paper-trading/account/', paper_trading_api.paper_account, name='paper_account'),
    path('paper-trading/account/reset/', paper_trading_api.reset_account, name='reset_paper_account'),
    
    # Order Placement
    path('paper-trading/orders/place/', paper_trading_api.place_order, name='place_paper_order'),
    path('paper-trading/orders/<int:trade_id>/cancel/', paper_trading_api.cancel_order, name='cancel_paper_order'),
    
    # Position Management
    path('paper-trading/positions/', paper_trading_api.open_positions, name='paper_open_positions'),
    path('paper-trading/positions/<int:trade_id>/close/', paper_trading_api.close_position, name='close_paper_position'),
    
    # Trade History & Performance
    path('paper-trading/history/', paper_trading_api.trade_history, name='paper_trade_history'),
    path('paper-trading/performance/', paper_trading_api.performance_metrics, name='paper_performance'),
    path('paper-trading/leaderboard/', paper_trading_api.leaderboard, name='paper_leaderboard'),

    # ============================================================================
    # SMS ALERT SYSTEM (MVP2 v3.4 - TextBelt)
    # ============================================================================
    
    # Alert Rule Management
    path('sms-alerts/', sms_alert_api.alert_rules, name='sms_alert_rules'),
    path('sms-alerts/<int:alert_id>/', sms_alert_api.alert_rule_detail, name='sms_alert_detail'),
    path('sms-alerts/<int:alert_id>/toggle/', sms_alert_api.toggle_alert, name='toggle_sms_alert'),
    path('sms-alerts/<int:alert_id>/test/', sms_alert_api.test_alert, name='test_sms_alert'),
    
    # Alert History & Quota
    path('sms-alerts/history/', sms_alert_api.alert_history, name='sms_alert_history'),
    path('sms-alerts/quota/', sms_alert_api.quota_status, name='sms_quota_status'),
    
    # Alert Configuration
    path('sms-alerts/conditions/available/', sms_alert_api.available_conditions, name='available_alert_conditions'),
    path('sms-alerts/summary/', sms_alert_api.alert_summary, name='sms_alert_summary'),
    
    # TextBelt Status & Monitoring
    path('sms-alerts/textbelt/status/', sms_alert_api.textbelt_status, name='textbelt_status'),
    
    # Cron Endpoint (Internal - should be protected)
    path('sms-alerts/cron/check/', sms_alert_api.check_alerts_cron, name='check_alerts_cron'),

    # ============================================================================
    # TWO-FACTOR AUTHENTICATION (2FA) - SMS-BASED
    # ============================================================================
    
    # 2FA Status & Configuration
    path('2fa/status/', twofa_api.twofa_status, name='twofa_status'),
    path('2fa/settings/', twofa_api.update_settings, name='twofa_settings'),
    
    # Enable/Disable 2FA
    path('2fa/enable/', twofa_api.enable_twofa, name='enable_twofa'),
    path('2fa/enable/verify/', twofa_api.verify_enable_twofa, name='verify_enable_twofa'),
    path('2fa/disable/', twofa_api.disable_twofa, name='disable_twofa'),
    
    # Code Management
    path('2fa/code/send/', twofa_api.send_code, name='send_2fa_code'),
    path('2fa/code/verify/', twofa_api.verify_code, name='verify_2fa_code'),
    
    # Backup Codes
    path('2fa/backup/verify/', twofa_api.verify_backup_code, name='verify_backup_code'),
    path('2fa/backup/regenerate/', twofa_api.regenerate_backup_codes, name='regenerate_backup_codes'),
    
    # Trusted Devices
    path('2fa/devices/', twofa_api.trusted_devices, name='trusted_devices'),
    path('2fa/devices/trust/', twofa_api.trust_current_device, name='trust_device'),
    path('2fa/devices/<int:device_id>/revoke/', twofa_api.revoke_device, name='revoke_device'),
    
    # Audit & Monitoring
    path('2fa/audit/', twofa_api.audit_log, name='twofa_audit_log'),
    
    # Login Helper (No Auth Required)
    path('2fa/check-required/', twofa_api.check_2fa_required, name='check_2fa_required'),

    # ============================================================================
    # OPTIONS ANALYTICS SYSTEM (MVP2 v3.4 - Pro Tier)
    # ============================================================================

    # Options Chain & Data (REAL-TIME - Pro Tier)
    path('options/<str:ticker>/chain/', options_api.get_option_chain, name='options_chain'),
    path('options/<str:ticker>/expirations/', options_api.get_expirations, name='options_expirations'),

    # Greeks & Analytics (REAL-TIME - Pro Tier)
    path('options/<str:ticker>/greeks/', options_api.get_greeks_surface, name='options_greeks'),
    path('options/<str:ticker>/iv-surface/', options_api.get_iv_surface, name='options_iv_surface'),
    path('options/calculator/', options_api.calculate_greeks, name='options_calculator'),

    # ============================================================================
    # NEWS & SENTIMENT SYSTEM (MVP2 v3.4)
    # ============================================================================

    # News Feed & Articles
    path('news/feed/', news_sentiment_api.get_news_feed, name='news_feed'),
    path('news/trending/', news_sentiment_api.get_trending_news, name='trending_news'),
    path('news/article/<int:article_id>/', news_sentiment_api.get_article_detail, name='article_detail'),
    path('news/article/<int:article_id>/click/', news_sentiment_api.track_article_click, name='track_article_click'),

    # Stock-Specific News
    path('news/stock/<str:ticker>/', news_sentiment_api.get_stock_news, name='stock_news'),
    path('news/stock/<str:ticker>/sentiment/', news_sentiment_api.get_sentiment_summary, name='stock_sentiment_summary'),
    path('news/stock/<str:ticker>/sentiment/timeseries/', news_sentiment_api.get_sentiment_timeseries, name='sentiment_timeseries'),

    # User Feed Settings
    path('news/feed/settings/', news_sentiment_api.news_feed_settings, name='news_feed_settings'),

    # News Alerts
    path('news/alerts/', news_sentiment_api.news_alerts, name='news_alerts'),
    path('news/alerts/<int:alert_id>/read/', news_sentiment_api.mark_alert_read, name='mark_alert_read'),

    # News Sources
    path('news/sources/', news_sentiment_api.list_news_sources, name='news_sources'),

    # Admin/Pro Operations
    path('news/fetch/trigger/', news_sentiment_api.trigger_news_fetch, name='trigger_news_fetch'),
    path('news/sentiment/analyze/', news_sentiment_api.trigger_sentiment_analysis, name='trigger_sentiment_analysis'),

    # ============================================================================
    # PHASE 10 & 11 - POLISH, SCALE & TRUST + SETUP (MVP2 v3.4)
    # ============================================================================

    # Dashboards
    path('dashboards/create/', system_api.create_dashboard, name='create_dashboard'),
    path('dashboards/my/', system_api.get_my_dashboards, name='my_dashboards'),
    path('dashboards/public/', system_api.get_public_dashboards, name='public_dashboards'),
    path('dashboards/<int:dashboard_id>/update/', system_api.update_dashboard, name='update_dashboard'),

    # Chart Presets
    path('chart-presets/create/', system_api.create_chart_preset, name='create_chart_preset'),
    path('chart-presets/my/', system_api.get_my_chart_presets, name='my_chart_presets'),
    path('chart-presets/public/', system_api.get_public_chart_presets, name='public_chart_presets'),

    # Performance Monitoring
    path('performance/record/', system_api.record_performance_metric, name='record_performance_metric'),
    path('performance/report/', system_api.get_performance_report, name='performance_report'),

    # Feature Flags
    path('features/<str:flag_name>/check/', system_api.check_feature_flag, name='check_feature_flag'),
    path('features/all/', system_api.get_all_feature_flags, name='all_feature_flags'),
    path('features/<str:flag_name>/toggle/', system_api.toggle_feature_flag, name='toggle_feature_flag'),

    # System Health
    path('health/', system_api.health_check, name='health_check'),
    path('health/history/', system_api.get_health_history, name='health_history'),
    path('system/info/', system_api.get_system_info, name='system_info'),
    path('system/verify/', system_api.verify_setup, name='verify_setup'),
]
