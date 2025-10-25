"""
Watchlist URL Configuration
Dedicated URL patterns for watchlist management endpoints.
"""

from django.urls import path
from . import watchlist_api, watchlist_api_updated

app_name = 'watchlist'

urlpatterns = [
    # New RESTful endpoints (matching specification)
    path('', watchlist_api_updated.watchlist_api, name='watchlist_list'),
    path('add/', watchlist_api_updated.watchlist_add_api, name='watchlist_add'),
    path('<str:item_id>/', watchlist_api_updated.watchlist_delete_api, name='watchlist_delete'),
    
    # Legacy endpoints (keeping for backward compatibility)
    path('create/', watchlist_api.create_watchlist, name='create'),
    path('list/', watchlist_api.list_watchlists, name='list'),
    path('<int:watchlist_id>/update/', watchlist_api.update_watchlist, name='update'),
    path('<int:watchlist_id>/delete/', watchlist_api.delete_watchlist, name='delete'),
    path('<int:watchlist_id>/performance/', watchlist_api.watchlist_performance, name='performance'),
    
    # Watchlist item management
    path('add-stock/', watchlist_api.add_stock, name='add_stock'),
    path('remove-stock/', watchlist_api.remove_stock, name='remove_stock'),
    path('item/<int:item_id>/', watchlist_api.update_watchlist_item, name='update_item'),
    
    # Import/Export functionality
    path('<int:watchlist_id>/export/csv/', watchlist_api.export_csv, name='export_csv'),
    path('<int:watchlist_id>/export/json/', watchlist_api.export_json, name='export_json'),
    path('import/csv/', watchlist_api.import_csv, name='import_csv'),
    path('import/json/', watchlist_api.import_json, name='import_json'),
]