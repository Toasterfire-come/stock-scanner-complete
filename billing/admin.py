from django.contrib import admin
from .models import Subscription, Payment, Invoice, PayPalWebhookEvent


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_tier', 'billing_cycle', 'status', 'current_period_end', 'created_at']
    list_filter = ['plan_tier', 'billing_cycle', 'status']
    search_fields = ['user__username', 'user__email', 'paypal_subscription_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'plan_tier', 'status', 'created_at']
    list_filter = ['status', 'plan_tier', 'billing_cycle']
    search_fields = ['user__username', 'user__email', 'paypal_order_id', 'paypal_capture_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'user', 'payment', 'pdf_generated', 'created_at']
    search_fields = ['invoice_number', 'user__username', 'user__email']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(PayPalWebhookEvent)
class PayPalWebhookEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'event_id', 'processed', 'created_at']
    list_filter = ['event_type', 'processed']
    search_fields = ['event_id', 'event_type']
    readonly_fields = ['id', 'created_at', 'processed_at']
    date_hierarchy = 'created_at'
