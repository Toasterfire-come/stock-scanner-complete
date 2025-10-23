"""
Billing and Notification Management API Views
Provides comprehensive billing history, payment management, and notification endpoints
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpResponse
import os
import base64
import requests
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Q, Sum
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4
import os
from decimal import Decimal

from .models import BillingHistory, NotificationSettings, UserProfile, UsageStats, UserPortfolio, UserWatchlist, Screener, StockAlert
from .plan_limits import get_limits_for_user
from django.conf import settings
from .security_utils import secure_api_endpoint
from .authentication import CsrfExemptSessionAuthentication, BearerSessionAuthentication
from .services.discount_service import DiscountService
from .models import DiscountCode
import hmac
import hashlib
from django.conf import settings as django_settings
from django.views.decorators.cache import never_cache

# Dynamic permission that allows all in testing mode
AuthPerm = AllowAny if getattr(django_settings, 'TESTING_DISABLE_AUTH', False) else IsAuthenticated

def _effective_user(request):
    try:
        testing = getattr(django_settings, 'TESTING_DISABLE_AUTH', False)
    except Exception:
        testing = False
    if testing:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
                return request.user
            user, _ = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'carter.kiefer2010@outlook.com', 'is_active': True}
            )
            return user
        except Exception:
            pass
    return getattr(request, 'user', None)
@csrf_exempt
@api_view(['POST'])
def paypal_webhook_api(request):
    """
    Minimal PayPal webhook receiver for PAYMENT.CAPTURE.COMPLETED events.
    Verifies event type and records payment; activates plan if metadata present.
    """
    try:
        data = json.loads(request.body) if request.body else {}
        event_type = (data.get('event_type') or data.get('eventType') or '').upper()
        resource = data.get('resource') or {}
        custom_id = resource.get('custom_id') or resource.get('customId') or ''
        amount_info = (resource.get('amount') or {})
        value = amount_info.get('value') or '0'
        final_amount = Decimal(str(value))

        # Parse custom_id if it matches our format: plan_billing_ts_userid_optional
        plan_type = None
        billing_cycle = None
        user_id = None
        try:
            parts = custom_id.split('_') if custom_id else []
            if len(parts) >= 3:
                plan_type, billing_cycle, _ts = parts[:3]
            if len(parts) >= 4:
                user_id = int(parts[3])
        except Exception:
            pass

        # Optional signature verification (if webhook ID/headers configured)
        try:
            webhook_id = getattr(settings, 'PAYPAL_WEBHOOK_ID', '')
            tr_id = request.META.get('HTTP_PAYPAL_TRANSMISSION_ID')
            tr_sig = request.META.get('HTTP_PAYPAL_TRANSMISSION_SIG')
            tr_time = request.META.get('HTTP_PAYPAL_TRANSMISSION_TIME')
            cert_url = request.META.get('HTTP_PAYPAL_CERT_URL')
            algo = request.META.get('HTTP_PAYPAL_AUTH_ALGO')
            # If configured, call PayPal verify endpoint
            if webhook_id and tr_id and tr_sig and tr_time:
                token = _paypal_get_access_token()
                headers = { 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json' }
                verify_payload = {
                    'transmission_id': tr_id,
                    'transmission_time': tr_time,
                    'cert_url': cert_url,
                    'auth_algo': algo,
                    'transmission_sig': tr_sig,
                    'webhook_id': webhook_id,
                    'webhook_event': data,
                }
                v = requests.post(f"{_paypal_base_url()}/v1/notifications/verify-webhook-signature", headers=headers, json=verify_payload, timeout=15)
                v.raise_for_status()
                if (v.json() or {}).get('verification_status') != 'SUCCESS':
                    return JsonResponse({'success': False, 'error': 'Invalid webhook signature'}, status=400)
        except Exception as _sig_err:
            logger.warning(f"PayPal webhook signature verification skipped/failed: {_sig_err}")

        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # Record revenue without requiring auth context
            discount_obj = None
            try:
                # We could store discount in custom fields if provided
                discount_code = (resource.get('discount_code') or '').strip()
                if discount_code:
                    discount_obj = DiscountCode.objects.get(code=discount_code.upper(), is_active=True)
            except DiscountCode.DoesNotExist:
                discount_obj = None

            # Resolve user
            user = None
            if user_id:
                from django.contrib.auth.models import User
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                try:
                    DiscountService.record_payment(
                        user=user,
                        original_amount=final_amount,
                        discount_code=discount_obj,
                        payment_date=timezone.now()
                    )
                except Exception as e:
                    logger.error(f"Webhook record_payment failed: {e}")

                # Activate plan if plan info available
                try:
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    if plan_type:
                        profile.plan_type = plan_type
                        profile.is_premium = plan_type not in ['free','basic']
                    if billing_cycle in ['monthly','annual']:
                        profile.billing_cycle = billing_cycle
                    days = 30 if profile.billing_cycle == 'monthly' else 365
                    profile.next_billing_date = timezone.now() + timedelta(days=days)
                    plan_limits = {
                        'free': 100,
                        'basic': 1000,
                        'bronze': 1500,
                        'silver': 5000,
                        'gold': 100000,
                        'enterprise': 100000
                    }
                    profile.api_calls_limit = plan_limits.get(profile.plan_type or 'basic', 1000)
                    profile.save()
                except Exception as e:
                    logger.error(f"Webhook plan activation failed: {e}")

        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"PayPal webhook error: {e}")
        return JsonResponse({'success': False, 'error': 'Webhook processing failed'}, status=500)

logger = logging.getLogger(__name__)

# PayPal order creation (discount-aware)
def _paypal_base_url():
    # Use live by default; set PAYPAL_ENV=sandbox to use sandbox
    env = getattr(settings, 'PAYPAL_ENV', None) or str(os.environ.get('PAYPAL_ENV') or os.environ.get('PAYPAL_MODE') or '').lower()
    return 'https://api-m.sandbox.paypal.com' if env == 'sandbox' else 'https://api-m.paypal.com'

def _paypal_get_access_token():
    client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
    secret = getattr(settings, 'PAYPAL_SECRET', '')
    if not client_id or not secret:
        raise ValueError('Missing PayPal credentials')
    auth = base64.b64encode(f"{client_id}:{secret}".encode('utf-8')).decode('utf-8')
    url = f"{_paypal_base_url()}/v1/oauth2/token"
    headers = { 'Authorization': f"Basic {auth}", 'Content-Type': 'application/x-www-form-urlencoded' }
    resp = requests.post(url, headers=headers, data={ 'grant_type': 'client_credentials' }, timeout=15)
    resp.raise_for_status()
    return resp.json().get('access_token')

# Generate PayPal client token for Advanced Cards/Hosted Fields
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def paypal_client_token_api(request):
    try:
        token = _paypal_get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        url = f"{_paypal_base_url()}/v1/identity/generate-token"
        r = requests.post(url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json() or {}
        client_token = data.get('client_token') or data.get('clientToken')
        return JsonResponse({'success': True, 'client_token': client_token})
    except Exception as e:
        logger.error(f"PayPal client token error: {e}")
        return JsonResponse({'success': False, 'error': 'Failed to generate client token'}, status=500)

# Public pricing/config for checkout (plan names, prices, PayPal plan IDs)
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def paypal_plans_meta_api(request):
    try:
        PRICES = {
            'bronze': { 'monthly': Decimal('24.99'), 'annual': Decimal('299.99') },
            'silver': { 'monthly': Decimal('49.99'), 'annual': Decimal('599.99') },
            'gold':   { 'monthly': Decimal('79.99'), 'annual': Decimal('959.99') },
        }

        # Apply standard 15% annual discount for displayed final annual amount
        def annual_final(plan_key):
            return (PRICES[plan_key]['annual'] * Decimal('0.85')).quantize(Decimal('0.01'))

        def env(name, default=''):
            return os.environ.get(name, default)

        data = {
            'currency': 'USD',
            'discounts': { 'annual_percent': 15 },
            'plans': {
                'bronze': {
                    'name': 'Bronze',
                    'monthly_price': float(PRICES['bronze']['monthly']),
                    'annual_list_price': float(PRICES['bronze']['annual']),
                    'annual_final_price': float(annual_final('bronze')),
                    'paypal_plan_ids': {
                        'monthly': env('PAYPAL_PLAN_BRONZE_MONTHLY', ''),
                        'annual': env('PAYPAL_PLAN_BRONZE_ANNUAL', ''),
                    },
                },
                'silver': {
                    'name': 'Silver',
                    'monthly_price': float(PRICES['silver']['monthly']),
                    'annual_list_price': float(PRICES['silver']['annual']),
                    'annual_final_price': float(annual_final('silver')),
                    'paypal_plan_ids': {
                        'monthly': env('PAYPAL_PLAN_SILVER_MONTHLY', ''),
                        'annual': env('PAYPAL_PLAN_SILVER_ANNUAL', ''),
                    },
                },
                'gold': {
                    'name': 'Gold',
                    'monthly_price': float(PRICES['gold']['monthly']),
                    'annual_list_price': float(PRICES['gold']['annual']),
                    'annual_final_price': float(annual_final('gold')),
                    'paypal_plan_ids': {
                        'monthly': env('PAYPAL_PLAN_GOLD_MONTHLY', ''),
                        'annual': env('PAYPAL_PLAN_GOLD_ANNUAL', ''),
                    },
                },
            }
        }
        return JsonResponse({ 'success': True, 'data': data })
    except Exception as e:
        logger.error(f"PayPal plans meta error: {e}")
        return JsonResponse({ 'success': False, 'error': 'Failed to load plans' }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def create_paypal_order_api(request):
    """
    Create a PayPal order (stub integration)
    POST /api/billing/create-paypal-order
    Body: { plan_type, billing_cycle, discount_code }
    """
    try:
        # Prefer DRF parsed data, fallback to raw JSON only once
        data = getattr(request, 'data', None)
        if data is None or data == {}:
            data = json.loads(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else (request.body or '{}'))

        # Support common aliases used by clients
        requested_plan = (data.get('plan') or data.get('plan_type') or 'bronze').strip().lower()
        billing_cycle = (data.get('billing_cycle') or data.get('interval') or 'monthly').strip().lower()
        discount_code_str = (data.get('discount_code') or data.get('coupon') or '').strip()
        currency = 'USD'

        # Rate-limit checkout attempts per user/IP (velocity limits)
        def _client_ip(req):
            xff = req.META.get('HTTP_X_FORWARDED_FOR')
            if xff:
                return xff.split(',')[0].strip()
            return req.META.get('REMOTE_ADDR') or 'unknown'

        rl_id = str(getattr(request.user, 'id', 'anon')) if request.user.is_authenticated else f"ip:{_client_ip(request)}"
        rl_key = f"checkout_attempts:{rl_id}"
        attempts = cache.get(rl_key, 0)
        if attempts >= 10:
            return JsonResponse({
                'success': False,
                'error': 'Too many checkout attempts. Please try again later.',
                'error_code': 'RATE_LIMIT'
            }, status=429)
        cache.set(rl_key, attempts + 1, timeout=10 * 60)

        # Optional reCAPTCHA validation when configured
        recaptcha_token = (data.get('recaptcha_token') or '').strip()
        if getattr(settings, 'RECAPTCHA_SECRET', '') and recaptcha_token:
            try:
                rr = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                    'secret': settings.RECAPTCHA_SECRET,
                    'response': recaptcha_token
                }, timeout=8)
                if not (rr.ok and (rr.json() or {}).get('success') is True):
                    return JsonResponse({'success': False, 'error': 'reCAPTCHA validation failed', 'error_code': 'RECAPTCHA_FAILED'}, status=400)
            except Exception:
                # Fail open: do not block checkout if Google is unreachable
                pass

        # Pricing table (align with frontend)
        PRICES = {
            'bronze': { 'monthly': Decimal('24.99'), 'annual': Decimal('299.99') },
            'silver': { 'monthly': Decimal('49.99'), 'annual': Decimal('599.99') },
            'gold':   { 'monthly': Decimal('79.99'), 'annual': Decimal('959.99') },
            # Accept common synonyms
            'basic':  { 'monthly': Decimal('24.99'), 'annual': Decimal('299.99') },
            'pro':    { 'monthly': Decimal('49.99'), 'annual': Decimal('599.99') },
            'premium':{ 'monthly': Decimal('79.99'), 'annual': Decimal('959.99') },
        }

        # Normalize requested plan to one we price
        plan_type = requested_plan

        if plan_type not in PRICES:
            return JsonResponse({
                'success': False,
                'error': 'Invalid plan_type',
                'error_code': 'INVALID_PLAN'
            }, status=400)
        if billing_cycle not in ['monthly', 'annual']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid billing_cycle',
                'error_code': 'INVALID_BILLING_CYCLE'
            }, status=400)

        original_amount = PRICES[plan_type][billing_cycle]

        # Apply standard 15% annual discount before any code-based discounts
        if billing_cycle == 'annual':
            original_amount = (original_amount * Decimal('0.85')).quantize(Decimal('0.01'))

        # Ensure discount codes exist (idempotent)
        try:
            DiscountService.initialize_ref50_code()
            DiscountService.initialize_trial_code()
        except Exception:
            pass

        final_amount = original_amount
        discount_applied = None
        discount_obj = None
        # Auto-create referral code (50% first payment) and apply
        if discount_code_str:
            try:
                # Create or normalize referral discount if not exists
                ref_obj, _ = DiscountService.get_or_create_referral_code(discount_code_str)
                discount_obj = ref_obj
            except Exception:
                discount_obj = None
        if discount_obj and request.user.is_authenticated:
            validation = DiscountService.validate_discount_code(discount_obj.code, request.user, billing_cycle=billing_cycle)
            if validation.get('valid'):
                if validation.get('applies_discount'):
                    if validation['discount'].code.upper() == 'TRIAL':
                        final_amount = Decimal('1.00') if original_amount > Decimal('1.00') else original_amount
                        discount_applied = {
                            'code': 'TRIAL',
                            'type': 'trial',
                            'description': '7-day $1 trial',
                            'original_amount': float(original_amount),
                            'final_amount': float(final_amount)
                        }
                    else:
                        calc = DiscountService.calculate_discounted_price(original_amount, validation['discount_amount'])
                        final_amount = calc['final_amount']
                        discount_applied = {
                            'code': validation['discount'].code,
                            'type': 'percentage',
                            'percentage': float(validation['discount_amount']),
                            'original_amount': float(original_amount),
                            'final_amount': float(final_amount)
                        }

        # Safety: amounts must be >= 0.50 for PayPal sandbox, but allow $1 trial
        if final_amount <= 0:
            final_amount = Decimal('0.50')

        # Prepare order payload (token retrieval moved into try block below for graceful fallback)
        purchase_unit = {
            'amount': { 'value': f"{final_amount:.2f}", 'currency_code': currency },
            'description': f"Trade Scan Pro {plan_type.title()} Plan - {billing_cycle}",
        }
        # Attach metadata to custom_id if possible
        custom_parts = [plan_type, billing_cycle, str(int(timezone.now().timestamp()))]
        if request.user.is_authenticated:
            custom_parts.append(str(request.user.id))
        purchase_unit['custom_id'] = '_'.join(custom_parts)

        payload = {
            'intent': 'CAPTURE',
            'purchase_units': [purchase_unit],
            'application_context': {
                'brand_name': 'Trade Scan Pro',
                'user_action': 'PAY_NOW',
                # Optional return/cancel if you want to use server redirects
            }
        }
        try:
            # Obtain token and create order with PayPal
            token = _paypal_get_access_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            # Idempotency
            headers['PayPal-Request-Id'] = f"create-{uuid4().hex}"
            resp = requests.post(f"{_paypal_base_url()}/v2/checkout/orders", headers=headers, json=payload, timeout=20)
            resp.raise_for_status()
            order = resp.json()
            approval_url = next((l.get('href') for l in order.get('links', []) if l.get('rel') in ['approve','payer-action']), None)
            return JsonResponse({
                'success': True,
                'order_id': order.get('id'),
                'approval_url': approval_url,
                'currency': currency,
                'plan_type': plan_type,
                'billing_cycle': billing_cycle,
                'discount_applied': discount_applied,
                'amount': float(original_amount),
                'final_amount': float(final_amount)
            }, status=201)
        except Exception as _paypal_err:
            logger.error(f"PayPal create order failed: {_paypal_err}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to create PayPal order',
                'error_code': 'PAYPAL_CREATE_FAILED'
            }, status=502)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Create PayPal order error: {str(e)}")
        # If this was due to request parsing, return 400
        msg = str(e)
        if 'data stream' in msg or 'read' in msg.lower():
            return JsonResponse({
                'success': False,
                'error': 'Invalid request body',
                'error_code': 'INVALID_REQUEST_BODY'
            }, status=400)
        return JsonResponse({
            'success': False,
            'error': 'Failed to create PayPal order',
            'error_code': 'PAYPAL_CREATE_ERROR'
        }, status=500)


# PayPal capture (record payment)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def capture_paypal_order_api(request):
    """
    Capture a PayPal order (stub integration)
    POST /api/billing/capture-paypal-order
    Body: { order_id, plan_type, billing_cycle, discount_code, amount, final_amount }
    """
    try:
        # Prefer DRF parsed data, fallback to raw JSON only once
        data = getattr(request, 'data', None)
        if data is None or data == {}:
            data = json.loads(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else (request.body or '{}'))

        # Support common aliases from frontend
        order_id = (data.get('order_id') or data.get('paypal_order_id') or data.get('token') or '').strip()
        if not order_id:
            return JsonResponse({
                'success': False,
                'error': 'order_id is required',
                'error_code': 'MISSING_ORDER_ID'
            }, status=400)

        # Extract optional plan/discount data for revenue tracking
        plan_type = (data.get('plan_type') or data.get('plan') or 'bronze').strip().lower()
        billing_cycle = (data.get('billing_cycle') or data.get('interval') or 'monthly').strip().lower()
        discount_code_str = (data.get('discount_code') or data.get('coupon') or '').strip()
        amount = data.get('amount')
        final_amount = data.get('final_amount')

        capture_json = {}
        # Capture via PayPal REST v2
        token = _paypal_get_access_token()
        headers = { 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json' }
        headers['PayPal-Request-Id'] = f"capture-{order_id}-{uuid4().hex}"
        resp = requests.post(f"{_paypal_base_url()}/v2/checkout/orders/{order_id}/capture", headers=headers, json={}, timeout=20)
        try:
            resp.raise_for_status()
        except Exception:
            # Return upstream error, if any
            return JsonResponse({ 'success': False, 'error': 'PayPal capture failed', 'details': resp.text }, status=502)
        capture_json = resp.json() or {}

        # Attempt to record payment if authenticated or if custom_id had a user id
        try:
            resource = capture_json
            if resource.get('purchase_units'):
                resource = resource['purchase_units'][0]
            custom_id = resource.get('custom_id') or ''
            inferred_user = None
            if request.user.is_authenticated:
                inferred_user = request.user
            else:
                try:
                    parts = custom_id.split('_') if custom_id else []
                    if len(parts) >= 4:
                        uid = int(parts[3])
                        from django.contrib.auth.models import User
                        inferred_user = User.objects.get(id=uid)
                except Exception:
                    inferred_user = None

            discount_obj = None
            if discount_code_str:
                try:
                    discount_obj = DiscountCode.objects.get(code=discount_code_str.upper(), is_active=True)
                except DiscountCode.DoesNotExist:
                    discount_obj = None

            if inferred_user is not None:
                # Determine final amount from PayPal capture if not provided
                if final_amount is None:
                    try:
                        cap = resource.get('payments', {}).get('captures', [])[0]
                        val = cap.get('amount', {}).get('value')
                        final_amount = Decimal(str(val)) if val else None
                    except Exception:
                        pass
                if final_amount is None and amount is not None:
                    final_amount = Decimal(str(amount))

                if final_amount is not None:
                    DiscountService.record_payment(
                        user=inferred_user,
                        original_amount=Decimal(str(final_amount)),
                        discount_code=discount_obj,
                        payment_date=timezone.now(),
                        billing_cycle=billing_cycle
                    )
        except Exception as rec_err:
            logger.error(f"Failed to record payment for order {order_id}: {rec_err}")

        # Activate user's plan upon successful capture (if we know the user)
        try:
            user = request.user if request.user.is_authenticated else inferred_user
            if not user:
                raise ValueError('No user context for plan activation')
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if plan_type in ['free','basic','bronze','silver','gold','enterprise']:
                profile.plan_type = plan_type
                profile.is_premium = plan_type not in ['free', 'basic']
                profile.billing_cycle = billing_cycle if billing_cycle in ['monthly','annual'] else 'monthly'
                # Set next billing date: monthly +30d, annual +365d, trial handled elsewhere
                days = 30 if profile.billing_cycle == 'monthly' else 365
                profile.next_billing_date = timezone.now() + timedelta(days=days)
                # Set sensible API limits
                plan_limits = {
                    'free': 100,
                    'basic': 1000,
                    'bronze': 1500,
                    'silver': 5000,
                    'gold': 100000,
                    'enterprise': 100000
                }
                profile.api_calls_limit = plan_limits.get(plan_type, 1000)
                profile.save()
        except Exception as e:
            logger.error(f"Failed to activate plan after capture: {e}")

        # Fake capture result
        return JsonResponse({
            'success': True,
            'message': 'Payment captured successfully',
            'order_id': order_id,
            'status': 'COMPLETED',
            'plan_type': plan_type,
            'billing_cycle': billing_cycle
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Capture PayPal order error: {str(e)}")
        msg = str(e)
        if 'data stream' in msg or 'read' in msg.lower():
            return JsonResponse({
                'success': False,
                'error': 'Invalid request body',
                'error_code': 'INVALID_REQUEST_BODY'
            }, status=400)
        return JsonResponse({
            'success': False,
            'error': 'Failed to capture PayPal order',
            'error_code': 'PAYPAL_CAPTURE_ERROR'
        }, status=500)


# PayPal status/configuration endpoint (authenticated users)
@csrf_exempt
@api_view(['GET'])
@permission_classes([AuthPerm])
def paypal_status_api(request):
    try:
        client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
        webhook_url = getattr(settings, 'PAYPAL_WEBHOOK_URL', '')
        webhook_id = getattr(settings, 'PAYPAL_WEBHOOK_ID', '')
        env = (os.environ.get('PAYPAL_ENV') or os.environ.get('PAYPAL_MODE') or 'live').lower()
        data = {
            'environment': 'sandbox' if env == 'sandbox' else 'live',
            'client_configured': bool(client_id),
            'webhook_configured': bool(webhook_url or webhook_id),
            'base_url': _paypal_base_url(),
        }
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"PayPal status error: {e}")
        return JsonResponse({'success': False, 'error': 'Failed to fetch PayPal status'}, status=500)

# Billing endpoints
@csrf_exempt
@api_view(['POST'])
@permission_classes([AuthPerm])
def update_payment_method_api(request):
    """
    Update user payment method
    POST /api/user/update-payment
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        user = _effective_user(request)
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Update payment method information
        payment_method = data.get('payment_method', {})
        
        if 'card_last_four' in payment_method:
            profile.card_last_four = payment_method['card_last_four']
        if 'card_type' in payment_method:
            profile.card_type = payment_method['card_type']
        if 'billing_address' in payment_method:
            profile.billing_address = json.dumps(payment_method['billing_address'])
        
        profile.payment_updated_at = timezone.now()
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Payment method updated successfully',
            'data': {
                'card_type': getattr(profile, 'card_type', ''),
                'card_last_four': getattr(profile, 'card_last_four', ''),
                'updated_at': profile.payment_updated_at.isoformat() if hasattr(profile, 'payment_updated_at') else None
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Update payment method error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to update payment method',
            'error_code': 'PAYMENT_UPDATE_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AuthPerm])
def billing_history_api(request):
    """
    Get user billing history
    GET /api/user/billing-history
    GET /api/billing/history
    """
    try:
        user = _effective_user(request)
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        
        # Get billing history records
        billing_records = BillingHistory.objects.filter(user=user).order_by('-created_at')
        
        # Paginate results
        paginator = Paginator(billing_records, limit)
        page_obj = paginator.get_page(page)
        
        billing_data = []
        for record in page_obj:
            billing_data.append({
                'id': record.invoice_id if hasattr(record, 'invoice_id') else f"INV-{record.id}",
                'date': record.created_at.strftime('%Y-%m-%d'),
                'description': getattr(record, 'description', f"Subscription Payment - {record.created_at.strftime('%B %Y')}"),
                'amount': float(record.amount) if hasattr(record, 'amount') else 49.99,
                'status': getattr(record, 'status', 'Paid'),
                'method': getattr(record, 'payment_method', 'Credit Card'),
                'download_url': f"/api/billing/download/{record.invoice_id if hasattr(record, 'invoice_id') else record.id}"
            })
        
        return JsonResponse({
            'success': True,
            'data': billing_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_records': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
        
    except Exception as e:
        logger.error(f"Billing history error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve billing history',
            'error_code': 'BILLING_HISTORY_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AuthPerm])
def cancel_subscription_api(request):
    """
    Cancel auto-renew for the current user. Keeps access until end of current period.
    POST /api/billing/cancel
    """
    try:
        user = _effective_user(request)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.auto_renew = False
        profile.subscription_status = 'canceled'
        profile.save()
        return JsonResponse({'success': True, 'message': 'Subscription will not auto-renew', 'next_billing_date': getattr(profile, 'next_billing_date', None)})
    except Exception as e:
        logger.error(f"Cancel subscription error: {e}")
        return JsonResponse({'success': False, 'error': 'Failed to cancel subscription'}, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AuthPerm])
def download_invoice_api(request, invoice_id):
    """
    Download invoice PDF
    GET /api/billing/download/{invoice_id}
    """
    try:
        user = _effective_user(request)
        
        # Get billing record
        try:
            if invoice_id.startswith('INV-'):
                billing_record = BillingHistory.objects.get(invoice_id=invoice_id, user=user)
            else:
                billing_record = BillingHistory.objects.get(id=invoice_id, user=user)
        except BillingHistory.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invoice not found',
                'error_code': 'INVOICE_NOT_FOUND'
            }, status=404)
        
        # Generate PDF content (simplified for demo)
        pdf_content = f"""
        INVOICE {invoice_id}
        
        Date: {billing_record.created_at.strftime('%Y-%m-%d')}
        Amount: ${getattr(billing_record, 'amount', 49.99):.2f}
        Status: {getattr(billing_record, 'status', 'Paid')}
        
        Thank you for your business!
        """
        
        response = HttpResponse(pdf_content.encode('utf-8'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_id}.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Download invoice error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to download invoice',
            'error_code': 'DOWNLOAD_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AuthPerm])
def current_plan_api(request):
    """
    Get current subscription plan
    GET /api/billing/current-plan
    """
    try:
        user = _effective_user(request)
        profile, created = UserProfile.objects.get_or_create(user=user)

        # Forced plan override by email (highest precedence)
        user_email = (getattr(user, 'email', '') or '').lower()
        forced_map = getattr(settings, 'FORCED_PLAN_BY_EMAIL', {})
        forced_plan = forced_map.get(user_email)
        if forced_plan in ['free','basic','pro','bronze','silver','gold','enterprise']:
            profile.plan_type = forced_plan
            profile.plan_name = forced_plan.title()
            profile.is_premium = forced_plan not in ['free', 'basic']
            plan_limits = {
                'free': 100,
                'basic': 1000,
                'bronze': 1500,
                'silver': 5000,
                'gold': 100000,
                'enterprise': 100000
            }
            profile.api_calls_limit = plan_limits.get(forced_plan, 1000)
            profile.save()
        else:
            # Enterprise email whitelist override
            enterprise_emails = set(email.lower() for email in getattr(settings, 'ENTERPRISE_EMAIL_WHITELIST', []))
            if user_email and user_email in enterprise_emails:
                profile.plan_type = 'enterprise'
                profile.plan_name = 'Enterprise'
                profile.is_premium = True
                profile.api_calls_limit = max(getattr(profile, 'api_calls_limit', 100000), 100000)
                profile.save()
        
        return JsonResponse({
            'success': True,
            'data': {
                'plan_name': getattr(profile, 'plan_name', 'Free'),
                'plan_type': getattr(profile, 'plan_type', 'free'),
                'is_premium': getattr(profile, 'is_premium', False),
                'billing_cycle': getattr(profile, 'billing_cycle', 'monthly'),
                'next_billing_date': getattr(profile, 'next_billing_date', None),
                'features': {
                    'api_calls_limit': getattr(profile, 'api_calls_limit', 100),
                    'real_time_data': getattr(profile, 'is_premium', False),
                    'portfolio_tracking': True,
                    'alerts': getattr(profile, 'is_premium', False),
                    'advanced_analytics': getattr(profile, 'is_premium', False)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Current plan error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve current plan',
            'error_code': 'CURRENT_PLAN_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AuthPerm])
def change_plan_api(request):
    """
    Change subscription plan
    POST /api/billing/change-plan
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        user = _effective_user(request)
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        new_plan = data.get('plan_type')
        user_email = (getattr(user, 'email', '') or '').lower()
        # Forced plan by email takes precedence over everything
        forced_map = getattr(settings, 'FORCED_PLAN_BY_EMAIL', {})
        forced_plan = forced_map.get(user_email)
        if forced_plan:
            new_plan = forced_plan
        else:
            # Enterprise email whitelist stays on enterprise regardless of request
            enterprise_emails = set(email.lower() for email in getattr(settings, 'ENTERPRISE_EMAIL_WHITELIST', []))
            if user_email and user_email in enterprise_emails:
                new_plan = 'enterprise'
        billing_cycle = data.get('billing_cycle', 'monthly')
        
        if new_plan not in ['free', 'basic', 'pro', 'enterprise']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid plan type',
                'error_code': 'INVALID_PLAN'
            }, status=400)
        
        # Update plan
        profile.plan_type = new_plan
        profile.billing_cycle = billing_cycle
        profile.is_premium = new_plan != 'free'
        profile.plan_changed_at = timezone.now()
        
        # Set API limits based on plan
        plan_limits = {
            'free': 100,
            'basic': 1000,
            'pro': 10000,
            'enterprise': 100000
        }
        profile.api_calls_limit = plan_limits.get(new_plan, 100)
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Plan changed to {new_plan} successfully',
            'data': {
                'plan_type': profile.plan_type,
                'billing_cycle': profile.billing_cycle,
                'is_premium': profile.is_premium,
                'api_calls_limit': profile.api_calls_limit
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Change plan error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to change plan',
            'error_code': 'PLAN_CHANGE_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AuthPerm])
def billing_stats_api(request):
    """
    Get billing statistics
    GET /api/billing/stats
    """
    try:
        user = _effective_user(request)
        
        # Calculate billing statistics
        total_spent = BillingHistory.objects.filter(user=user).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        recent_payments = BillingHistory.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=90)
        ).count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_spent': float(total_spent),
                'recent_payments': recent_payments,
                'account_status': 'Active',
                'next_billing_date': (timezone.now() + timedelta(days=30)).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Billing stats error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve billing stats',
            'error_code': 'BILLING_STATS_ERROR'
        }, status=500)

# Notification endpoints
@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AuthPerm])
def notification_settings_api(request):
    """
    Get or update notification settings
    GET/POST /api/user/notification-settings
    GET/POST /api/notifications/settings
    """
    try:
        user = _effective_user(request)
        settings, created = NotificationSettings.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            return JsonResponse({
                'success': True,
                'data': {
                    'trading': {
                        'price_alerts': getattr(settings, 'price_alerts', True),
                        'volume_alerts': getattr(settings, 'volume_alerts', True),
                        'market_hours': getattr(settings, 'market_hours', False)
                    },
                    'portfolio': {
                        'daily_summary': getattr(settings, 'daily_summary', True),
                        'weekly_report': getattr(settings, 'weekly_report', True),
                        'milestone_alerts': getattr(settings, 'milestone_alerts', True)
                    },
                    'news': {
                        'breaking_news': getattr(settings, 'breaking_news', True),
                        'earnings_alerts': getattr(settings, 'earnings_alerts', False),
                        'analyst_ratings': getattr(settings, 'analyst_ratings', False)
                    },
                    'security': {
                        'login_alerts': getattr(settings, 'login_alerts', True),
                        'billing_updates': getattr(settings, 'billing_updates', True),
                        'plan_updates': getattr(settings, 'plan_updates', True)
                    },
                    'sms': {
                        'enabled': getattr(settings, 'sms_enabled', False),
                        'verified': getattr(settings, 'sms_verified', False),
                        'price_alerts': getattr(settings, 'sms_price_alerts', False),
                        'breaking_news': getattr(settings, 'sms_breaking_news', False),
                        'milestone_alerts': getattr(settings, 'sms_milestone_alerts', False),
                    }
                }
            })
        
        elif request.method == 'POST':
            data = json.loads(request.body) if request.body else {}
            
            # Update trading notifications
            if 'trading' in data:
                trading = data['trading']
                if 'price_alerts' in trading:
                    settings.price_alerts = trading['price_alerts']
                if 'volume_alerts' in trading:
                    settings.volume_alerts = trading['volume_alerts']
                if 'market_hours' in trading:
                    settings.market_hours = trading['market_hours']
            
            # Update portfolio notifications
            if 'portfolio' in data:
                portfolio = data['portfolio']
                if 'daily_summary' in portfolio:
                    settings.daily_summary = portfolio['daily_summary']
                if 'weekly_report' in portfolio:
                    settings.weekly_report = portfolio['weekly_report']
                if 'milestone_alerts' in portfolio:
                    settings.milestone_alerts = portfolio['milestone_alerts']
            
            # Update news notifications
            if 'news' in data:
                news = data['news']
                if 'breaking_news' in news:
                    settings.breaking_news = news['breaking_news']
                if 'earnings_alerts' in news:
                    settings.earnings_alerts = news['earnings_alerts']
                if 'analyst_ratings' in news:
                    settings.analyst_ratings = news['analyst_ratings']
            
            # Update security notifications
            if 'security' in data:
                security = data['security']
                if 'login_alerts' in security:
                    settings.login_alerts = security['login_alerts']
                if 'billing_updates' in security:
                    settings.billing_updates = security['billing_updates']
                if 'plan_updates' in security:
                    settings.plan_updates = security['plan_updates']

            # Update SMS prefs (no external provider)
            if 'sms' in data:
                sms = data['sms']
                if 'enabled' in sms:
                    try:
                        settings.sms_enabled = bool(sms['enabled'])
                    except Exception:
                        pass
                if 'price_alerts' in sms:
                    try:
                        settings.sms_price_alerts = bool(sms['price_alerts'])
                    except Exception:
                        pass
                if 'breaking_news' in sms:
                    try:
                        settings.sms_breaking_news = bool(sms['breaking_news'])
                    except Exception:
                        pass
                if 'milestone_alerts' in sms:
                    try:
                        settings.sms_milestone_alerts = bool(sms['milestone_alerts'])
                    except Exception:
                        pass
            
            settings.updated_at = timezone.now()
            settings.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Notification settings updated successfully'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Notification settings error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to manage notification settings',
            'error_code': 'NOTIFICATION_ERROR'
        }, status=500)

# Usage statistics endpoint
@csrf_exempt
@api_view(['GET'])
@permission_classes([AuthPerm])
def usage_stats_api(request):
    """
    Get user usage statistics
    GET /api/usage-stats
    """
    try:
        user = _effective_user(request)
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Calculate usage statistics
        today = timezone.now().date()
        this_month = timezone.now().replace(day=1).date()
        
        # Get usage stats if the model exists
        try:
            daily_usage = UsageStats.objects.filter(
                user=user,
                date=today
            ).first()
            
            monthly_usage = UsageStats.objects.filter(
                user=user,
                date__gte=this_month
            ).aggregate(
                total_api_calls=Sum('api_calls'),
                total_requests=Sum('requests')
            )
        except:
            # Fallback if UsageStats model doesn't exist
            daily_usage = None
            monthly_usage = {'total_api_calls': 0, 'total_requests': 0}
        
        return JsonResponse({
            'success': True,
            'data': {
                'daily': {
                    'api_calls': daily_usage.api_calls if daily_usage else 0,
                    'requests': daily_usage.requests if daily_usage else 0,
                    'date': today.isoformat()
                },
                'monthly': {
                    'api_calls': monthly_usage['total_api_calls'] or 0,
                    'requests': monthly_usage['total_requests'] or 0,
                    'limit': getattr(profile, 'api_calls_limit', 100),
                    'remaining': max(0, getattr(profile, 'api_calls_limit', 100) - (monthly_usage['total_api_calls'] or 0))
                },
                'account': {
                    'plan_type': getattr(profile, 'plan_type', 'free'),
                    'is_premium': getattr(profile, 'is_premium', False),
                    'member_since': user.date_joined.isoformat()
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Usage stats error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve usage statistics',
            'error_code': 'USAGE_STATS_ERROR'
        }, status=500)


# Developer usage stats (explicit path expected by frontend)
@csrf_exempt
@api_view(['GET'])
@permission_classes([AuthPerm])
def developer_usage_stats_api(request):
    """
    Returns daily.api_calls, monthly.api_calls, and usage_history[] for developer dashboard.
    GET /api/developer/usage-stats/
    """
    try:
        user = _effective_user(request)
        profile, _ = UserProfile.objects.get_or_create(user=user)

        today = timezone.now().date()
        month_start = timezone.now().replace(day=1).date()

        # Fetch daily and monthly aggregates
        daily = UsageStats.objects.filter(user=user, date=today).first()
        monthly_qs = UsageStats.objects.filter(user=user, date__gte=month_start)
        monthly_api_calls = monthly_qs.aggregate(total=Sum('api_calls'))['total'] or 0
        monthly_requests = monthly_qs.aggregate(total=Sum('requests'))['total'] or 0

        # Build 30-day history (fallback to zeros if none)
        last_30 = [today - timedelta(days=i) for i in range(29, -1, -1)]
        stats_map = {
            s.date: {'api_calls': int(s.api_calls or 0), 'requests': int(s.requests or 0)}
            for s in UsageStats.objects.filter(user=user, date__gte=today - timedelta(days=30))
        }
        usage_history = [
            {
                'date': d.isoformat(),
                'api_calls': int((stats_map.get(d) or {}).get('api_calls', 0)),
                'requests': int((stats_map.get(d) or {}).get('requests', 0))
            }
            for d in last_30
        ]

        return JsonResponse({
            'success': True,
            'data': {
                'daily': {
                    'api_calls': int(getattr(daily, 'api_calls', 0)),
                    'requests': int(getattr(daily, 'requests', 0)),
                    'date': today.isoformat()
                },
                'monthly': {
                    'api_calls': int(monthly_api_calls),
                    'requests': int(monthly_requests),
                    'limit': int(getattr(profile, 'api_calls_limit', 100)),
                    'remaining': max(0, int(getattr(profile, 'api_calls_limit', 100)) - int(monthly_api_calls))
                },
                'usage_history': usage_history
            }
        })
    except Exception as e:
        logger.error(f"Developer usage stats error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve developer usage statistics',
            'error_code': 'DEV_USAGE_STATS_ERROR'
        }, status=500)


# Additional usage endpoints to satisfy frontend expectations
@csrf_exempt
@api_view(['GET'])
@permission_classes([AuthPerm])
def usage_summary_api(request):
    """
    Frontend-friendly usage summary
    GET /api/usage/
    """
    try:
        user = _effective_user(request)
        from django.utils import timezone
        today = timezone.now().date()
        month_start = timezone.now().replace(day=1).date()

        daily = UsageStats.objects.filter(user=user, date=today).first()
        monthly_qs = UsageStats.objects.filter(user=user, date__gte=month_start)
        total_api_calls = monthly_qs.aggregate(total=Sum('api_calls'))['total'] or 0
        total_requests = monthly_qs.aggregate(total=Sum('requests'))['total'] or 0

        profile, _ = UserProfile.objects.get_or_create(user=user)
        # Category counts and plan caps
        counts = {
            'alerts': StockAlert.objects.filter(user=user).count(),
            'watchlists': UserWatchlist.objects.filter(user=user).count(),
            'portfolios': UserPortfolio.objects.filter(user=user).count(),
            'screeners': Screener.objects.filter(user=user).count(),
        }
        limits = get_limits_for_user(user)

        return JsonResponse({
            'success': True,
            'data': {
                'daily': {
                    'api_calls': getattr(daily, 'api_calls', 0),
                    'requests': getattr(daily, 'requests', 0),
                    'date': today.isoformat()
                },
                'monthly': {
                    'api_calls': total_api_calls,
                    'requests': total_requests,
                    'limit': getattr(profile, 'api_calls_limit', 100),
                    'remaining': max(0, getattr(profile, 'api_calls_limit', 100) - total_api_calls)
                },
                'categories': {
                    'alerts': {
                        'count': counts['alerts'],
                        'limit': limits.get('alerts')
                    },
                    'watchlists': {
                        'count': counts['watchlists'],
                        'limit': limits.get('watchlists')
                    },
                    'portfolios': {
                        'count': counts['portfolios'],
                        'limit': limits.get('portfolios')
                    },
                    'screeners': {
                        'count': counts['screeners'],
                        'limit': limits.get('screeners')
                    }
                }
            }
        })
    except Exception as e:
        logger.error(f"Usage summary error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve usage summary',
            'error_code': 'USAGE_SUMMARY_ERROR'
        }, status=500)


@csrf_exempt
@never_cache
@api_view(['POST'])
@permission_classes([AuthPerm])
def usage_reconcile_api(request):
    """
    Reconcile frontend-reported monthly usage with server records by taking the max
    and updating the lower one so both match. Returns the reconciled counts.
    POST /api/usage/reconcile/
    Body: { monthly_api_calls: number, monthly_requests: number }
    """
    try:
        user = _effective_user(request)
        data = getattr(request, 'data', None)
        if data is None or data == {}:
            data = json.loads(request.body) if request.body else {}

        client_api = int(max(0, int(data.get('monthly_api_calls', 0))))
        client_req = int(max(0, int(data.get('monthly_requests', 0))))

        month_start = timezone.now().replace(day=1).date()
        today = timezone.now().date()

        # Calculate server totals for the month
        monthly_qs = UsageStats.objects.filter(user=user, date__gte=month_start)
        server_api = monthly_qs.aggregate(total=Sum('api_calls'))['total'] or 0
        server_req = monthly_qs.aggregate(total=Sum('requests'))['total'] or 0

        # Choose the higher counts as source of truth
        recon_api = max(server_api, client_api)
        recon_req = max(server_req, client_req)

        # If server is behind, top up today's row so monthly equals reconciled max
        if recon_api > server_api or recon_req > server_req:
            todays, _ = UsageStats.objects.get_or_create(user=user, date=today)
            api_delta = recon_api - server_api
            req_delta = recon_req - server_req
            if api_delta > 0:
                todays.api_calls = (todays.api_calls or 0) + api_delta
            if req_delta > 0:
                todays.requests = (todays.requests or 0) + req_delta
            todays.save()

        return JsonResponse({
            'success': True,
            'data': {
                'monthly': {
                    'api_calls': recon_api,
                    'requests': recon_req
                }
            }
        })
    except Exception as e:
        logger.error(f"Usage reconcile error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to reconcile usage',
            'error_code': 'USAGE_RECONCILE_ERROR'
        }, status=500)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AuthPerm])
def usage_history_api(request):
    """
    Usage history with simple pagination
    GET /api/usage/history
    """
    try:
        user = _effective_user(request)
        limit = int(request.GET.get('limit', 30))
        items = UsageStats.objects.filter(user=user).order_by('-date')[:limit]
        history = [
            {
                'date': item.date.isoformat(),
                'api_calls': item.api_calls,
                'requests': item.requests
            } for item in items
        ]
        return JsonResponse({'success': True, 'data': history})
    except Exception as e:
        logger.error(f"Usage history error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve usage history',
            'error_code': 'USAGE_HISTORY_ERROR'
        }, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def usage_track_api(request):
    """
    Track a single API usage event
    POST /api/usage/track/
    """
    try:
        # Parse JSON safely; accept empty body
        data = getattr(request, 'data', None)
        if data is None or data == {}:
            data = json.loads(request.body) if request.body else {}
        endpoint = (data.get('endpoint') or '').strip()
        method = (data.get('method') or 'GET').upper()

        from django.utils import timezone
        today = timezone.now().date()

        # Count stock, market, news, alerts, portfolio, screener endpoints toward usage numbers
        stock_prefixes = getattr(settings, 'STOCK_DATA_ENDPOINT_PREFIXES', [
            '/api/stocks/', '/api/stock/', '/api/search/', '/api/trending/', '/api/realtime/', '/api/filter/', '/api/market-stats/'
        ])
        extra_prefixes = ['/api/market-data/', '/api/news/', '/api/alerts/', '/api/portfolio/', '/api/screeners/']
        count_prefixes = list(dict.fromkeys([*stock_prefixes, *extra_prefixes]))
        free_prefixes = [
            '/health/', '/api/health/', '/health/detailed/', '/health/ready/', '/health/live/',
            '/docs/', '/api/docs/', '/endpoint-status/', '/api/endpoint-status/', '/api/auth/', '/static/', '/media/'
        ]
        should_count = endpoint and any(endpoint.startswith(p) for p in count_prefixes) and not any(endpoint.startswith(p) for p in free_prefixes)

        # Track only for authenticated users; avoid undefined stats when unauthenticated
        stats_api_calls = 0
        stats_requests = 0
        if request.user.is_authenticated:
            stats, _ = UsageStats.objects.get_or_create(user=request.user, date=today)
            if should_count:
                stats.api_calls = (stats.api_calls or 0) + 1
                stats.requests = (stats.requests or 0) + 1
            stats.save()
            stats_api_calls = stats.api_calls or 0
            stats_requests = stats.requests or 0

        return JsonResponse({
            'success': True,
            'message': 'Usage recorded',
            'data': {
                'endpoint': endpoint,
                'method': method,
                'date': today.isoformat(),
                'counted': bool(should_count),
                'daily': {
                    'api_calls': stats_api_calls,
                    'requests': stats_requests
                }
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Usage track error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to track usage',
            'error_code': 'USAGE_TRACK_ERROR'
        }, status=500)