from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
list_display = ('email', 'category', 'subscribed_at')
list_filter = ('category', 'subscribed_at')
search_fields = ('email', 'category')
ordering = ('-subscribed_at',)
