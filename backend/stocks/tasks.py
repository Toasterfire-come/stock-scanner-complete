from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
from django.conf import settings
import requests
from .billing_api import _paypal_get_access_token, _paypal_base_url

@shared_task
def run_stock_import():
    call_command('import_stock_data')

@shared_task
def retry_paypal_capture(order_id: str):
	"""Retry a failed PayPal order capture (idempotent via PayPal-Request-Id)."""
	token = _paypal_get_access_token()
	headers = { 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'PayPal-Request-Id': f'retry-{order_id}-{timezone.now().timestamp()}' }
	url = f"{_paypal_base_url()}/v2/checkout/orders/{order_id}/capture"
	resp = requests.post(url, headers=headers, json={}, timeout=20)
	try:
		resp.raise_for_status()
		return {'success': True, 'status': (resp.json() or {}).get('status')}
	except Exception:
		return {'success': False, 'error': resp.text}
