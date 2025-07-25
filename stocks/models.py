from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    exchange = models.CharField(max_length=50, default='NASDAQ')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.symbol} - {self.name}'

class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50, default='free')
    is_active = models.BooleanField(default=True)
