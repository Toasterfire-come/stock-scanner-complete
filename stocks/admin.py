from django.contrib import admin
from .models import Stock, StockPrice, Membership

admin.site.register(Stock)
admin.site.register(StockPrice)
admin.site.register(Membership)
