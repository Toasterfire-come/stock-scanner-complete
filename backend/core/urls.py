from django.urls import path
from . import views

urlpatterns = [
    path('screeners/', views.screeners_list, name='screeners_list'),
    path('screeners/<str:key>/', views.screener_detail, name='screener_detail'),
    path('stocks/<str:ticker>/', views.stock_detail_page, name='stock_detail_page'),
]
