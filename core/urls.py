from django.urls import path
from . import views, admin_api_views

urlpatterns = [
    path('', views.home, name='home'),
    path('news/', views.news_view, name='news_view'),
    path('search/', views.stock_search, name='stock_search'),
    path('filter/', views.filter_view, name='filter_view'),
    path('filter/download/', views.download_csv_view, name='download_csv'),
    path('email-filter/', views.email_filter_view, name='email_filter'),
    path('subscribe/<slug:category>/', views.subscription_form, name='subscription_form'),
    path('subscribe-<slug:route_name>', views.generic_subscribe),
    
    # Admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # WordPress data admin pages
    path('wordpress-stocks/', views.wordpress_stocks_page, name='wordpress_stocks_page'),
    path('wordpress-news/', views.wordpress_news_page, name='wordpress_news_page'),
    
    # Admin API endpoints
    path('api/admin/status/', admin_api_views.admin_status, name='admin_status'),
    path('api/admin/load-nasdaq/', admin_api_views.load_nasdaq_data, name='load_nasdaq'),
    path('api/admin/update-stocks/', admin_api_views.update_stocks, name='update_stocks'),
    path('api/admin/update-nasdaq-now/', admin_api_views.update_nasdaq_now, name='update_nasdaq_now'),
    path('api/admin/scrape-news/', admin_api_views.scrape_news, name='scrape_news'),
    path('api/admin/send-notifications/', admin_api_views.send_notifications, name='send_notifications'),
    path('api/admin/optimize-db/', admin_api_views.optimize_database, name='optimize_database'),
    path('api/admin/api-providers/', admin_api_views.api_providers_status, name='api_providers_status'),
    
    # News API endpoints
    path('api/news/recent/', admin_api_views.recent_news, name='recent_news'),
    
    # WordPress Integration endpoints
    path('api/wordpress/stocks/', admin_api_views.wordpress_stock_data, name='wordpress_stocks'),
    path('api/wordpress/news/', admin_api_views.wordpress_news_data, name='wordpress_news'),
]
