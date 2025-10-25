"""
Portfolio URL Configuration
Dedicated URL patterns for portfolio management endpoints.
"""

from django.urls import path
from . import portfolio_api, portfolio_api_updated

app_name = 'portfolio'

urlpatterns = [
    # New RESTful endpoints (matching specification)
    path('', portfolio_api_updated.portfolio_api, name='portfolio_list'),
    path('add/', portfolio_api_updated.portfolio_add_api, name='portfolio_add'),
    path('<str:holding_id>/', portfolio_api_updated.portfolio_delete_api, name='portfolio_delete'),
    
    # Legacy endpoints (keeping for backward compatibility)
    path('create/', portfolio_api.create_portfolio, name='create'),
    path('list/', portfolio_api.list_portfolios, name='list'),
    path('<int:portfolio_id>/delete/', portfolio_api.delete_portfolio, name='delete_legacy'),
    path('<int:portfolio_id>/update/', portfolio_api.update_portfolio, name='update'),
    path('<int:portfolio_id>/performance/', portfolio_api.portfolio_performance, name='performance'),
    
    # Portfolio holdings management
    path('add-holding/', portfolio_api.add_holding, name='add_holding'),
    path('sell-holding/', portfolio_api.sell_holding, name='sell_holding'),
    
    # Portfolio import/export and analytics
    path('import-csv/', portfolio_api.import_csv, name='import_csv'),
    path('alert-roi/', portfolio_api.alert_roi, name='alert_roi'),
]