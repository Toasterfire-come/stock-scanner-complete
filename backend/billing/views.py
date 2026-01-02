from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from decimal import Decimal
import json
import requests
import logging
from datetime import datetime, timedelta

from .models import Subscription, Payment, Invoice, PayPalWebhookEvent, PlanTier, BillingCycle

logger = logging.getLogger(__name__)


# Plan pricing configuration - Updated December 30, 2025
PLAN_PRICING = {
    'basic': {
        'monthly': Decimal('9.99'),
        'annual': Decimal('101.99'),  # 15% discount (9.99 * 12 * 0.85)
    },
    'pro': {
        'monthly': Decimal('24.99'),
        'annual': Decimal('254.99'),  # 15% discount (24.99 * 12 * 0.85)
    },
    'pay_per_use': {
        'monthly': Decimal('24.99'),
        'annual': Decimal('254.99'),  # 15% discount (base price, same as Pro)
    },
}

# US State sales tax rates (2024)
SALES_TAX_RATES = {
    'AL': 4.00, 'AK': 0.00, 'AZ': 5.60, 'AR': 6.50, 'CA': 7.25,
    'CO': 2.90, 'CT': 6.35, 'DE': 0.00, 'FL': 6.00, 'GA': 4.00,
    'HI': 4.00, 'ID': 6.00, 'IL': 6.25, 'IN': 7.00, 'IA': 6.00,
    'KS': 6.50, 'KY': 6.00, 'LA': 4.45, 'ME': 5.50, 'MD': 6.00,
    'MA': 6.25, 'MI': 6.00, 'MN': 6.875, 'MS': 7.00, 'MO': 4.225,
    'MT': 0.00, 'NE': 5.50, 'NV': 6.85, 'NH': 0.00, 'NJ': 6.625,
    'NM': 5.125, 'NY': 8.00, 'NC': 4.75, 'ND': 5.00, 'OH': 5.75,
    'OK': 4.50, 'OR': 0.00, 'PA': 6.00, 'RI': 7.00, 'SC': 6.00,
    'SD': 4.50, 'TN': 7.00, 'TX': 6.25, 'UT': 5.95, 'VT': 6.00,
    'VA': 5.30, 'WA': 6.50, 'WV': 6.00, 'WI': 5.00, 'WY': 4.00,
    'DC': 6.00,
}


def get_paypal_access_token():
    """Get PayPal OAuth access token"""
    client_id = getattr(settings, 'PAYPAL_CLIENT_ID', None)
    client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', None)
    mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
    
    if not client_id or not client_secret:
        raise ValueError("PayPal credentials not configured")
    
    base_url = 'https://api-m.paypal.com' if mode == 'live' else 'https://api-m.sandbox.paypal.com'
    
    response = requests.post(
        f'{base_url}/v1/oauth2/token',
        headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
        data={'grant_type': 'client_credentials'},
        auth=(client_id, client_secret),
        timeout=10  # 10 second timeout for PayPal API calls
    )
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        # Log status code only, not sensitive response text
        logger.error(f"PayPal auth failed: HTTP {response.status_code}")
        raise Exception("Failed to authenticate with PayPal")


def calculate_sales_tax(amount, state_code=None):
    """Calculate sales tax based on state"""
    if not state_code or state_code not in SALES_TAX_RATES:
        return Decimal('0.00'), Decimal('0.00')
    
    tax_rate = Decimal(str(SALES_TAX_RATES[state_code]))
    tax_amount = (amount * tax_rate / Decimal('100')).quantize(Decimal('0.01'))
    return tax_amount, tax_rate


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def detect_state_from_ip(ip_address):
    """Detect US state from IP address using ipapi.co"""
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('country_code') == 'US':
                return data.get('region_code')
    except (requests.RequestException, requests.Timeout, ValueError, KeyError) as e:
        logger.debug(f"IP geolocation failed for {ip_address}: {e}")
    return None


@require_http_methods(["POST"])
@login_required
def create_paypal_order(request):
    """Create PayPal order on server side"""
    try:
        data = json.loads(request.body)
        plan_type = data.get('plan_type', '').lower()
        billing_cycle = data.get('billing_cycle', 'monthly').lower()
        discount_code = data.get('discount_code')
        
        # Validate plan
        if plan_type not in PLAN_PRICING:
            return JsonResponse({'success': False, 'error': 'Invalid plan type'}, status=400)
        
        if billing_cycle not in ['monthly', 'annual']:
            return JsonResponse({'success': False, 'error': 'Invalid billing cycle'}, status=400)
        
        # Get base price (already includes any discounts)
        amount = PLAN_PRICING[plan_type][billing_cycle]

        # Apply additional discount code if provided
        discount_percentage = 0
        if discount_code:
            # Validate discount code format (alphanumeric, underscore, hyphen, max 50 chars)
            import re
            if not re.match(r'^[A-Z0-9_-]{1,50}$', discount_code.upper()):
                logger.warning(f"Invalid discount code format: {discount_code[:20]}")
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid discount code format'
                }, status=400)

            # Check for referral codes (50% off first month for monthly plans)
            if discount_code.upper().startswith('REF_') and billing_cycle == 'monthly':
                discount_percentage = 50
                amount = amount * Decimal('0.5')
            # Add more discount code logic here as needed
        
        # Detect user's state for sales tax
        ip_address = get_client_ip(request)
        state_code = detect_state_from_ip(ip_address)
        tax_amount, tax_rate = calculate_sales_tax(amount, state_code)

        total_amount = amount + tax_amount

        # Validate amount (minimum $0.50 for PayPal)
        if total_amount < Decimal('0.50'):
            logger.error(f"Total amount too low: {total_amount}")
            return JsonResponse({
                'success': False,
                'error': 'Transaction amount too low (minimum $0.50)'
            }, status=400)

        # Additional validation: reasonable max amount to prevent errors
        if total_amount > Decimal('10000.00'):
            logger.warning(f"Unusually high payment amount: {total_amount}")
            # Allow but log for review
        
        # Create PayPal order
        access_token = get_paypal_access_token()
        mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
        base_url = 'https://api-m.paypal.com' if mode == 'live' else 'https://api-m.sandbox.paypal.com'
        
        order_data = {
            'intent': 'CAPTURE',
            'purchase_units': [{
                'amount': {
                    'currency_code': 'USD',
                    'value': str(total_amount.quantize(Decimal('0.01'))),
                    'breakdown': {
                        'item_total': {'currency_code': 'USD', 'value': str(amount.quantize(Decimal('0.01')))},
                        'tax_total': {'currency_code': 'USD', 'value': str(tax_amount.quantize(Decimal('0.01')))},
                    }
                },
                'description': f'{plan_type.capitalize()} Plan - {billing_cycle.capitalize()}',
                'custom_id': f'{request.user.id}:{plan_type}:{billing_cycle}',
            }],
            'application_context': {
                'brand_name': 'Trade Scan Pro',
                'landing_page': 'NO_PREFERENCE',
                'user_action': 'PAY_NOW',
                'return_url': f'{settings.FRONTEND_URL}/checkout/success',
                'cancel_url': f'{settings.FRONTEND_URL}/checkout/failure',
            }
        }
        
        response = requests.post(
            f'{base_url}/v2/checkout/orders',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            },
            json=order_data,
            timeout=10  # 10 second timeout for PayPal API calls
        )
        
        if response.status_code in [200, 201]:
            order = response.json()
            order_id = order['id']
            
            # Create payment record
            Payment.objects.create(
                user=request.user,
                paypal_order_id=order_id,
                amount=amount,
                tax_amount=tax_amount,
                currency='USD',
                status='pending',
                plan_tier=plan_type,
                billing_cycle=billing_cycle,
                discount_code=discount_code,
                ip_address=ip_address,
                tax_state=state_code,
                tax_rate=tax_rate,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            logger.info(f"PayPal order created: {order_id} for user {request.user.id}")
            
            return JsonResponse({
                'success': True,
                'order_id': order_id,
                'amount': float(total_amount),
                'tax_amount': float(tax_amount),
                'state': state_code,
            })
        else:
            # Log status code only, not sensitive details
            logger.error(f"PayPal order creation failed: HTTP {response.status_code}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to create PayPal order',
                'error_code': 'PAYPAL_ORDER_FAILED'
            }, status=500)
            
    except Exception as e:
        logger.exception(f"Error creating PayPal order: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
@transaction.atomic  # Performance & Data Integrity: Ensure all DB operations succeed or rollback
def capture_paypal_order(request):
    """Capture PayPal order and activate subscription"""
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        
        if not order_id:
            return JsonResponse({'success': False, 'error': 'Order ID required'}, status=400)
        
        # Get payment record
        try:
            payment = Payment.objects.get(paypal_order_id=order_id, user=request.user)
        except Payment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Payment not found'}, status=404)

        # Idempotency check - if already completed, return success (idempotent)
        if payment.status == 'completed':
            logger.info(f"Payment already captured (idempotent): {order_id}")
            # Return success with existing data to make this call idempotent
            return JsonResponse({
                'success': True,
                'message': 'Payment already captured',
                'order_id': order_id,
                'capture_id': payment.paypal_capture_id or '',
                'status': 'completed',
                'idempotent': True
            })

        if payment.status == 'failed':
            logger.warning(f"Attempted to capture failed payment: {order_id}")
            return JsonResponse({
                'success': False,
                'error': 'Cannot capture failed payment'
            }, status=400)

        if payment.status != 'pending':
            logger.warning(f"Invalid payment state for capture: {payment.status}")
            return JsonResponse({
                'success': False,
                'error': f'Invalid payment state: {payment.status}'
            }, status=400)

        # Capture the order
        access_token = get_paypal_access_token()
        mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
        base_url = 'https://api-m.paypal.com' if mode == 'live' else 'https://api-m.sandbox.paypal.com'
        
        response = requests.post(
            f'{base_url}/v2/checkout/orders/{order_id}/capture',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            },
            timeout=15  # 15 second timeout for capture (may take longer)
        )
        
        if response.status_code in [200, 201]:
            capture_data = response.json()
            
            # Verify capture was successful
            if capture_data.get('status') == 'COMPLETED':
                capture_id = capture_data['purchase_units'][0]['payments']['captures'][0]['id']
                payer_id = capture_data.get('payer', {}).get('payer_id')
                
                # Update payment record
                payment.status = 'completed'
                payment.paypal_capture_id = capture_id
                payment.paypal_payer_id = payer_id
                payment.save()
                
                # Create or update subscription
                subscription, created = Subscription.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'plan_tier': payment.plan_tier,
                        'billing_cycle': payment.billing_cycle,
                        'status': 'active',
                        'monthly_price': payment.amount,
                        'discount_code': payment.discount_code,
                        'current_period_start': timezone.now(),
                        'current_period_end': timezone.now() + timedelta(days=30 if payment.billing_cycle == 'monthly' else 365),
                    }
                )
                
                if not created:
                    # Update existing subscription
                    subscription.plan_tier = payment.plan_tier
                    subscription.billing_cycle = payment.billing_cycle
                    subscription.status = 'active'
                    subscription.monthly_price = payment.amount
                    subscription.discount_code = payment.discount_code
                    subscription.current_period_start = timezone.now()
                    subscription.current_period_end = timezone.now() + timedelta(days=30 if payment.billing_cycle == 'monthly' else 365)
                    subscription.save()
                
                payment.subscription = subscription
                payment.save()
                
                # Create invoice
                invoice = Invoice.objects.create(
                    user=request.user,
                    payment=payment,
                    invoice_number=Invoice().generate_invoice_number()
                )
                
                logger.info(f"Payment captured successfully: {capture_id} for user {request.user.id}")
                
                return JsonResponse({
                    'success': True,
                    'capture_id': capture_id,
                    'subscription_id': str(subscription.id),
                    'plan': payment.plan_tier,
                    'status': 'active'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Payment not completed: {capture_data.get("status")}'
                }, status=400)
        else:
            # Log status code only, not sensitive details
            logger.error(f"PayPal capture failed: HTTP {response.status_code}")
            payment.status = 'failed'
            payment.save()
            return JsonResponse({
                'success': False,
                'error': 'Failed to capture payment',
                'error_code': 'CAPTURE_REQUEST_FAILED'
            }, status=500)
            
    except Exception as e:
        logger.exception(f"Error capturing PayPal order: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def change_plan(request):
    """Change user's subscription plan"""
    try:
        data = json.loads(request.body)
        plan = data.get('plan', '').lower()
        billing_cycle = data.get('billing_cycle', 'monthly').lower()
        subscription_id = data.get('subscription_id')
        discount_code = data.get('discount_code')
        
        if plan not in PLAN_PRICING:
            return JsonResponse({'success': False, 'error': 'Invalid plan'}, status=400)
        
        # Get plan price
        plan_price = PLAN_PRICING[plan][billing_cycle]

        # Get or create subscription
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={
                'plan_tier': plan,
                'billing_cycle': billing_cycle,
                'status': 'active',
                'monthly_price': plan_price,
                'discount_code': discount_code,
                'paypal_subscription_id': subscription_id,
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(days=30 if billing_cycle == 'monthly' else 365),
            }
        )
        
        if not created:
            subscription.plan_tier = plan
            subscription.billing_cycle = billing_cycle
            subscription.status = 'active'
            subscription.monthly_price = plan_price
            if discount_code:
                subscription.discount_code = discount_code
            if subscription_id:
                subscription.paypal_subscription_id = subscription_id
            subscription.current_period_start = timezone.now()
            subscription.current_period_end = timezone.now() + timedelta(days=30 if billing_cycle == 'monthly' else 365)
            subscription.save()
        
        logger.info(f"Plan changed to {plan} for user {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'subscription_id': str(subscription.id),
            'plan': plan,
            'billing_cycle': billing_cycle,
            'status': subscription.status
        })
        
    except Exception as e:
        logger.exception(f"Error changing plan: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_current_plan(request):
    """Get user's current subscription plan"""
    try:
        try:
            subscription = Subscription.objects.get(user=request.user)
            return JsonResponse({
                'success': True,
                'data': {
                    'plan': subscription.plan_tier,
                    'billing_cycle': subscription.billing_cycle,
                    'status': subscription.status,
                    'current_period_end': subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                    'is_trial': subscription.is_trial,
                    'paypal_subscription_id': subscription.paypal_subscription_id,
                }
            })
        except Subscription.DoesNotExist:
            return JsonResponse({
                'success': True,
                'data': {
                    'plan': 'free',
                    'billing_cycle': 'monthly',
                    'status': 'active',
                    'current_period_end': None,
                    'is_trial': False,
                    'paypal_subscription_id': None,
                }
            })
    except Exception as e:
        logger.exception(f"Error getting current plan: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_plans_meta(request):
    """Get plan pricing metadata (public endpoint)"""
    try:
        plans_data = {}
        for plan_name, pricing in PLAN_PRICING.items():
            plans_data[plan_name] = {
                'name': plan_name.capitalize(),
                'monthly_price': float(pricing['monthly']),
                'annual_price': float(pricing['annual']),
                'paypal_plan_ids': {
                    'monthly': getattr(settings, f'PAYPAL_PLAN_{plan_name.upper()}_MONTHLY', ''),
                    'annual': getattr(settings, f'PAYPAL_PLAN_{plan_name.upper()}_ANNUAL', ''),
                }
            }
        
        return JsonResponse({
            'success': True,
            'data': {
                'currency': 'USD',
                'plans': plans_data
            }
        })
    except Exception as e:
        logger.exception(f"Error getting plans meta: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_billing_history(request):
    """Get user's billing history"""
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        total = payments.count()
        
        start = (page - 1) * limit
        end = start + limit
        payments_page = payments[start:end]
        
        history = []
        for payment in payments_page:
            history.append({
                'id': str(payment.id),
                'date': payment.created_at.isoformat(),
                'amount': float(payment.amount + payment.tax_amount),
                'status': payment.status,
                'description': f'{payment.plan_tier.capitalize()} Plan - {payment.billing_cycle.capitalize()}',
                'method': 'PayPal',
                'download_url': f'/api/billing/invoices/{payment.id}/download/' if payment.status == 'completed' else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': history,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
    except Exception as e:
        logger.exception(f"Error getting billing history: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_billing_stats(request):
    """Get user's billing statistics"""
    try:
        payments = Payment.objects.filter(user=request.user, status='completed')
        total_spent = sum(p.amount + p.tax_amount for p in payments)
        recent_payments = payments.count()
        
        try:
            subscription = Subscription.objects.get(user=request.user)
            account_status = subscription.status
            next_billing_date = subscription.current_period_end.isoformat() if subscription.current_period_end else None
        except Subscription.DoesNotExist:
            account_status = 'active'
            next_billing_date = None
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_spent': float(total_spent),
                'recent_payments': recent_payments,
                'account_status': account_status,
                'next_billing_date': next_billing_date,
            }
        })
    except Exception as e:
        logger.exception(f"Error getting billing stats: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def apply_discount(request):
    """Validate and apply discount code"""
    try:
        data = json.loads(request.body)
        code = data.get('code', '').upper().strip()
        billing_cycle = data.get('billing_cycle', 'monthly').lower()
        amount = Decimal(str(data.get('amount', 0)))
        
        if not code:
            return JsonResponse({'success': False, 'error': 'Discount code required'}, status=400)
        
        # Check referral codes (50% off first month for monthly plans)
        if code.startswith('REF_') and billing_cycle == 'monthly':
            final_amount = amount * Decimal('0.5')
            return JsonResponse({
                'success': True,
                'applies_discount': True,
                'code': code,
                'final_amount': float(final_amount),
                'original_amount': float(amount),
                'savings_percentage': 50,
                'message': 'Referral discount: 50% off first month'
            })
        
        # Add more discount code logic here
        
        return JsonResponse({
            'success': True,
            'applies_discount': False,
            'message': 'Invalid or expired discount code'
        })
        
    except Exception as e:
        logger.exception(f"Error applying discount: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def verify_paypal_webhook_signature(request):
    """
    Verify PayPal webhook signature for security

    Security: Prevents fake webhook events from malicious actors
    Returns: True if signature is valid, False otherwise
    """
    # Get PayPal signature headers
    transmission_id = request.META.get('HTTP_PAYPAL_TRANSMISSION_ID')
    transmission_time = request.META.get('HTTP_PAYPAL_TRANSMISSION_TIME')
    cert_url = request.META.get('HTTP_PAYPAL_CERT_URL')
    transmission_sig = request.META.get('HTTP_PAYPAL_TRANSMISSION_SIG')
    auth_algo = request.META.get('HTTP_PAYPAL_AUTH_ALGO', 'SHA256withRSA')

    # Check if all required headers are present
    if not all([transmission_id, transmission_time, cert_url, transmission_sig]):
        logger.warning("Missing PayPal webhook signature headers")
        return False

    webhook_id = settings.PAYPAL_WEBHOOK_ID
    if not webhook_id:
        logger.warning("PAYPAL_WEBHOOK_ID not configured in settings")
        return False

    # Verify signature using PayPal API
    # Documentation: https://developer.paypal.com/docs/api/webhooks/v1/#verify-webhook-signature
    try:
        access_token = get_paypal_access_token()
        if not access_token:
            logger.error("Failed to get PayPal access token for webhook verification")
            return False

        base_url = 'https://api-m.paypal.com' if settings.PAYPAL_MODE == 'live' else 'https://api-m.sandbox.paypal.com'
        url = f'{base_url}/v1/notifications/verify-webhook-signature'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        payload = {
            'transmission_id': transmission_id,
            'transmission_time': transmission_time,
            'cert_url': cert_url,
            'auth_algo': auth_algo,
            'transmission_sig': transmission_sig,
            'webhook_id': webhook_id,
            'webhook_event': json.loads(request.body)
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()

        verification_status = result.get('verification_status')
        if verification_status == 'SUCCESS':
            return True
        else:
            logger.warning(f"PayPal webhook signature verification failed: {verification_status}")
            return False

    except Exception as e:
        logger.exception(f"Error verifying PayPal webhook signature: {e}")
        return False


@csrf_exempt
@require_http_methods(["POST"])
def paypal_webhook(request):
    """
    Handle PayPal webhook events

    Security: Verifies webhook signature before processing
    """
    try:
        # Security: Verify webhook signature FIRST
        if not verify_paypal_webhook_signature(request):
            logger.warning(f"Invalid PayPal webhook signature from IP {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({'error': 'Invalid signature'}, status=403)

        payload = json.loads(request.body)
        event_id = payload.get('id')
        event_type = payload.get('event_type')

        # Log webhook event
        webhook_event, created = PayPalWebhookEvent.objects.get_or_create(
            event_id=event_id,
            defaults={
                'event_type': event_type,
                'resource_type': payload.get('resource_type'),
                'payload': payload,
            }
        )

        if not created:
            # Duplicate event, ignore
            return JsonResponse({'status': 'duplicate'})

        # Signature verified - process event
        
        # FIXED: Process PAYMENT.CAPTURE.COMPLETED webhook
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            resource = payload.get('resource', {})
            capture_id = resource.get('id')
            
            if capture_id:
                try:
                    # Find payment by capture_id
                    payment = Payment.objects.get(paypal_capture_id=capture_id)
                    
                    # Ensure subscription is still active
                    if payment.subscription and payment.subscription.status != 'active':
                        payment.subscription.status = 'active'
                        payment.subscription.save()
                        logger.info(f"Subscription reactivated via webhook for payment {payment.id}")
                    
                except Payment.DoesNotExist:
                    logger.warning(f"Payment not found for capture_id: {capture_id}")
                    
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            # Subscription cancelled
            resource = payload.get('resource', {})
            subscription_id = resource.get('id')
            if subscription_id:
                try:
                    sub = Subscription.objects.get(paypal_subscription_id=subscription_id)
                    sub.status = 'cancelled'
                    sub.cancelled_at = timezone.now()
                    sub.save()
                except Subscription.DoesNotExist:
                    pass
        elif event_type == 'BILLING.SUBSCRIPTION.SUSPENDED':
            # Subscription suspended (payment failed)
            resource = payload.get('resource', {})
            subscription_id = resource.get('id')
            if subscription_id:
                try:
                    sub = Subscription.objects.get(paypal_subscription_id=subscription_id)
                    sub.status = 'suspended'
                    sub.save()
                except Subscription.DoesNotExist:
                    pass
        
        webhook_event.processed = True
        webhook_event.processed_at = timezone.now()
        webhook_event.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.exception(f"Error processing webhook: {str(e)}")
        if 'webhook_event' in locals():
            webhook_event.processing_error = str(e)
            webhook_event.save()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
