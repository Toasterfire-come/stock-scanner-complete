from django.urls import path
from . import api_views, analytics_views, admin_dashboard, portfolio_api_views, market_analysis_views, comprehensive_api_views, page_endpoints, advanced_features, wordpress_api, simple_api
try:
from . import paywall_api_views
PAYWALL_AVAILABLE = True
except ImportError:
PAYWALL_AVAILABLE = False

app_name = 'stocks_api'

urlpatterns = [
# Simple WordPress API endpoints (no database required - for testing)
path('api/simple/status/', simple_api.simple_status_api, name='simple_status'),
path('api/simple/stocks/', simple_api.simple_stocks_api, name='simple_stocks'),
path('api/simple/stocks/<str:ticker>/', simple_api.simple_stock_detail_api, name='simple_stock_detail'),
path('api/simple/news/', simple_api.simple_news_api, name='simple_news'),

# WordPress-specific API endpoints (requires database)
path('api/wordpress/stocks/', wordpress_api.wordpress_stocks_api, name='wordpress_stocks'),
path('api/wordpress/stocks/<str:ticker>/', wordpress_api.wordpress_stock_detail_api, name='wordpress_stock_detail'),
path('api/wordpress/news/', wordpress_api.wordpress_news_api, name='wordpress_news'),
path('api/wordpress/status/', wordpress_api.wordpress_status_api, name='wordpress_status'),

# REST API endpoints for WordPress integration
path('api/stocks/', api_views.stock_list_api, name='stock_list'),
path('api/stocks/<str:ticker>/', api_views.stock_detail_api, name='stock_detail'),
path('api/stocks/search/', api_views.stock_search_api, name='stock_search'),
path('api/market-movers/', api_views.market_movers_api, name='market_movers'),
path('api/stats/', api_views.stock_statistics_api, name='stock_statistics'),
path('api/wordpress/subscribe/', api_views.wordpress_subscription_api, name='wordpress_subscribe'),

# NEW FRONTEND INTEGRATION ENDPOINTS
path('api/email-signup/', api_views.email_signup_api, name='email_signup'),
path('api/stocks/filter/', api_views.stock_filter_api, name='stock_filter'),
path('api/stocks/lookup/<str:ticker>/', api_views.stock_lookup_api, name='stock_lookup'),
path('api/news/', api_views.stock_news_api, name='stock_news'),

# ANALYTICS ENDPOINTS
path('api/analytics/members/', analytics_views.member_analytics_api, name='member_analytics'),
path('api/analytics/public/', analytics_views.public_stats_api, name='public_stats'),
path('api/admin/dashboard/', admin_dashboard.dashboard_data, name='admin_dashboard_data'),

# PORTFOLIO TRACKER ENDPOINTS
path('api/portfolio/', portfolio_api_views.portfolio_list_api, name='portfolio_list'),
path('api/portfolio/create/', portfolio_api_views.portfolio_create_api, name='portfolio_create'),
path('api/portfolio/<int:portfolio_id>/', portfolio_api_views.portfolio_detail_api, name='portfolio_detail'),
path('api/portfolio/<int:portfolio_id>/add-holding/', portfolio_api_views.portfolio_add_holding_api, name='portfolio_add_holding'),

# MARKET ANALYSIS ENDPOINTS
path('api/market-analysis/', market_analysis_views.market_analysis_list_api, name='market_analysis_list'),
path('api/market-analysis/<int:analysis_id>/', market_analysis_views.market_analysis_detail_api, name='market_analysis_detail'),
path('api/technical-indicators/<str:ticker>/', market_analysis_views.technical_indicators_api, name='technical_indicators'),
path('api/market-overview/', market_analysis_views.market_overview_api, name='market_overview'),
path('api/sector-analysis/', market_analysis_views.sector_analysis_api, name='sector_analysis'),

# COMPREHENSIVE PAGE FUNCTIONALITY ENDPOINTS
path('api/watchlist/', comprehensive_api_views.watchlist_api, name='watchlist'),
path('api/stock-screener/', comprehensive_api_views.stock_screener_api, name='stock_screener'),
path('api/earnings-calendar/', comprehensive_api_views.earnings_calendar_api, name='earnings_calendar'),
path('api/research-reports/', comprehensive_api_views.research_reports_api, name='research_reports'),
path('api/educational-content/', comprehensive_api_views.educational_content_api, name='educational_content'),
path('api/contact/', comprehensive_api_views.contact_form_api, name='contact_form'),
path('api/faq/', comprehensive_api_views.faq_api, name='faq'),
path('api/member-dashboard/', comprehensive_api_views.member_dashboard_api, name='member_dashboard'),

# PAGE-SPECIFIC ENDPOINTS FOR ALL 24 WORDPRESS PAGES
path('api/pages/premium-plans/', page_endpoints.premium_plans_api, name='premium_plans'),
path('api/pages/email-stock-lists/', page_endpoints.email_stock_lists_api, name='email_stock_lists'),
path('api/pages/all-stock-alerts/', page_endpoints.all_stock_alerts_api, name='all_stock_alerts'),
path('api/pages/popular-stock-lists/', page_endpoints.popular_stock_lists_api, name='popular_stock_lists'),
path('api/pages/personalized-stock-finder/', page_endpoints.personalized_stock_finder_api, name='personalized_stock_finder'),
path('api/pages/news-scrapper/', page_endpoints.news_scrapper_api, name='news_scrapper'),
path('api/pages/filter-scrapper/', page_endpoints.filter_and_scrapper_pages_api, name='filter_scrapper'),
path('api/pages/membership-account/', page_endpoints.membership_account_api, name='membership_account_page'),
path('api/pages/membership-billing/', page_endpoints.membership_billing_api, name='membership_billing'),
path('api/pages/membership-cancel/', page_endpoints.membership_cancel_api, name='membership_cancel'),
path('api/pages/membership-checkout/', page_endpoints.membership_checkout_api, name='membership_checkout'),
path('api/pages/membership-confirmation/', page_endpoints.membership_confirmation_api, name='membership_confirmation'),
path('api/pages/membership-orders/', page_endpoints.membership_orders_api, name='membership_orders'),
path('api/pages/membership-levels/', page_endpoints.membership_levels_api, name='membership_levels'),
path('api/pages/login/', page_endpoints.login_api, name='login_page'),
path('api/pages/your-profile/', page_endpoints.your_profile_api, name='your_profile'),
path('api/pages/terms-conditions/', page_endpoints.terms_and_conditions_api, name='terms_conditions'),
path('api/pages/privacy-policy/', page_endpoints.privacy_policy_api, name='privacy_policy'),
path('api/pages/stock-dashboard/', page_endpoints.stock_dashboard_api, name='stock_dashboard'),
path('api/pages/stock-watchlist/', page_endpoints.stock_watchlist_api, name='stock_watchlist'),
path('api/pages/stock-market-news/', page_endpoints.stock_market_news_api, name='stock_market_news'),
path('api/pages/membership-plans/', page_endpoints.membership_plans_api, name='membership_plans'),

# ==================== ADVANCED FEATURES ====================

# API Usage Analytics
path('api/advanced/usage-analytics/', advanced_features.api_usage_analytics, name='api_usage_analytics'),
path('api/advanced/admin-usage/', advanced_features.admin_usage_analytics, name='admin_usage_analytics'),

# Market Sentiment Analysis
path('api/advanced/sentiment/<str:ticker>/', advanced_features.market_sentiment_api, name='market_sentiment'),
path('api/advanced/sentiment-dashboard/', advanced_features.sentiment_dashboard_api, name='sentiment_dashboard'),

# Portfolio Analytics
path('api/advanced/portfolio-analytics/<int:portfolio_id>/', advanced_features.portfolio_analytics_api, name='portfolio_analytics'),

# Compliance & Security
path('api/advanced/compliance-dashboard/', advanced_features.compliance_dashboard_api, name='compliance_dashboard'),
path('api/advanced/security-event/', advanced_features.report_security_event, name='report_security_event'),
path('api/advanced/gdpr-export/', advanced_features.gdpr_data_export, name='gdpr_data_export'),
path('api/advanced/gdpr-deletion/', advanced_features.gdpr_data_deletion, name='gdpr_data_deletion'),

# CORS handling
path('api/cors/', api_views.cors_handler, name='cors_handler'),
]

# Add paywall-protected endpoints if available
if PAYWALL_AVAILABLE:
urlpatterns += [
# Paywall-protected endpoints
path('api/protected/stocks/', paywall_api_views.protected_stock_list_api, name='protected_stock_list'),
path('api/protected/stocks/<str:ticker>/', paywall_api_views.protected_stock_detail_api, name='protected_stock_detail'),
path('api/premium/analytics/', paywall_api_views.premium_market_analytics_api, name='premium_analytics'),
path('api/premium/alerts/', paywall_api_views.premium_stock_alerts_api, name='premium_alerts'),
]