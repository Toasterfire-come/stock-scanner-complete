from django.urls import path
from . import views
from .wordpress_api import WordPressStockView, WordPressNewsView, WordPressAlertsView
from .simple_api import SimpleStockView, SimpleNewsView

urlpatterns = [
    # Main API endpoints
    path('', views.index, name='api_index'),
    path('stocks/', views.index, name='stocks_api'),
    
    # WordPress Integration APIs
    path('wordpress/', WordPressStockView.as_view(), name='wordpress_stocks'),
    path('wordpress/stocks/', WordPressStockView.as_view(), name='wordpress_stocks_detailed'),
    path('wordpress/news/', WordPressNewsView.as_view(), name='wordpress_news'),
    path('wordpress/alerts/', WordPressAlertsView.as_view(), name='wordpress_alerts'),
    
    # Simple APIs (no database required)
    path('simple/stocks/', SimpleStockView.as_view(), name='simple_stocks'),
    path('simple/news/', SimpleNewsView.as_view(), name='simple_news'),
]
