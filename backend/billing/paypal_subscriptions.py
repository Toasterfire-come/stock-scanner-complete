"""
PayPal Recurring Subscriptions Implementation
Handles subscription creation, management, and webhook processing
"""

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
import hashlib
import hmac
from datetime import datetime, timedelta

from .models import Subscription, Payment, PayPalWebhookEvent
from .views import get_paypal_access_token, PLAN_PRICING

logger = logging.getLogger(__name__)


def create_paypal_subscription_plan(plan_type, billing_cycle):
    """
    Create a PayPal subscription plan
    This should be run once per plan/cycle combination during setup
    """
    access_token = get_paypal_access_token()
    mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
    base_url = 'https://api-m.paypal.com' if mode == 'live' else 'https://api-m.sandbox.paypal.com'

    # Get pricing
    if plan_type not in PLAN_PRICING or billing_cycle not in PLAN_PRICING[plan_type]:
        raise ValueError(f"Invalid plan_type or billing_cycle: {plan_type}/{billing_cycle}")

    amount = PLAN_PRICING[plan_type][billing_cycle]

    # Plan names
    plan_names = {
        'basic': 'Basic',
        'pro': 'Pro',
        'pay_per_use': 'Pay-Per-Use'
    }

    plan_name = plan_names.get(plan_type, plan_type.capitalize())
    cycle_name = billing_cycle.capitalize()

    # Billing cycle configuration
    if billing_cycle == 'monthly':
        interval_unit = 'MONTH'
        interval_count = 1
    else:  # annual
        interval_unit = 'YEAR'
        interval_count = 1

    plan_data = {
        "product_id": f"PROD_TRADESCANPRO_{plan_type.upper()}",  # You'll need to create products first
        "name": f"TradeScanPro {plan_name} - {cycle_name}",
        "description": f"{plan_name} plan billed {billing_cycle}",
        "status": "ACTIVE",
        "billing_cycles": [
            {
                "frequency": {
                    "interval_unit": interval_unit,
                    "interval_count": interval_count
                },
                "tenure_type": "REGULAR",
                "sequence": 1,
                "total_cycles": 0,  # 0 = infinite
                "pricing_scheme": {
                    "fixed_price": {
                        "value": str(amount),
                        "currency_code": "USD"
                    }
                }
            }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": True,
            "setup_fee": {
                "value": "0",
                "currency_code": "USD"
            },
            "setup_fee_failure_action": "CONTINUE",
            "payment_failure_threshold": 3
        }
    }

    response = requests.post(
        f'{base_url}/v1/billing/plans',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Prefer': 'return=representation'
        },
        json=plan_data,
        timeout=10
    )

    if response.status_code in [200, 201]:
        plan = response.json()
        logger.info(f"Created PayPal plan: {plan['id']} for {plan_type}/{billing_cycle}")
        return plan['id']
    else:
        logger.error(f"Failed to create PayPal plan: {response.status_code} - {response.text[:200]}")
        raise Exception(f"Failed to create PayPal subscription plan: {response.status_code}")


@require_http_methods(["POST"])
@login_required
def create_subscription(request):
    """
    Create a PayPal subscription for the user
    Returns the subscription ID and approval URL
    """
    try:
        data = json.loads(request.body)
        plan_type = data.get('plan_type', '').lower()
        billing_cycle = data.get('billing_cycle', 'monthly').lower()

        # Validate plan
        if plan_type not in PLAN_PRICING:
            return JsonResponse({'success': False, 'error': 'Invalid plan type'}, status=400)

        if billing_cycle not in ['monthly', 'annual']:
            return JsonResponse({'success': False, 'error': 'Invalid billing cycle'}, status=400)

        # Check if user already has an active subscription
        existing = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).first()

        if existing:
            return JsonResponse({
                'success': False,
                'error': 'You already have an active subscription. Please cancel it first to change plans.'
            }, status=400)

        # Get PayPal plan ID from environment or create it
        # Format: PAYPAL_PLAN_{PLAN_TYPE}_{BILLING_CYCLE}
        env_var_name = f'PAYPAL_PLAN_{plan_type.upper()}_{billing_cycle.upper()}'
        paypal_plan_id = getattr(settings, env_var_name, None)

        if not paypal_plan_id:
            return JsonResponse({
                'success': False,
                'error': f'PayPal plan not configured: {env_var_name}',
                'error_code': 'PLAN_NOT_CONFIGURED'
            }, status=500)

        # Create PayPal subscription
        access_token = get_paypal_access_token()
        mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
        base_url = 'https://api-m.paypal.com' if mode == 'live' else 'https://api-m.sandbox.paypal.com'

        subscription_data = {
            "plan_id": paypal_plan_id,
            "start_time": (datetime.utcnow() + timedelta(minutes=5)).isoformat() + 'Z',
            "subscriber": {
                "name": {
                    "given_name": request.user.first_name or "User",
                    "surname": request.user.last_name or "User"
                },
                "email_address": request.user.email
            },
            "application_context": {
                "brand_name": "TradeScanPro",
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "payment_method": {
                    "payer_selected": "PAYPAL",
                    "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                },
                "return_url": f"{settings.FRONTEND_URL}/subscription/success",
                "cancel_url": f"{settings.FRONTEND_URL}/subscription/cancel"
            },
            "custom_id": f"{request.user.id}:{plan_type}:{billing_cycle}"
        }

        response = requests.post(
            f'{base_url}/v1/billing/subscriptions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'Prefer': 'return=representation'
            },
            json=subscription_data,
            timeout=10
        )

        if response.status_code in [200, 201]:
            subscription_response = response.json()
            subscription_id = subscription_response['id']

            # Get approval URL
            approval_url = None
            for link in subscription_response.get('links', []):
                if link.get('rel') == 'approve':
                    approval_url = link.get('href')
                    break

            # Create local subscription record (pending approval)
            Subscription.objects.create(
                user=request.user,
                plan_tier=plan_type,
                billing_cycle=billing_cycle,
                paypal_subscription_id=subscription_id,
                paypal_plan_id=paypal_plan_id,
                status='pending',  # Will be activated by webhook
                monthly_price=PLAN_PRICING[plan_type][billing_cycle],
                start_date=timezone.now()
            )

            logger.info(f"PayPal subscription created: {subscription_id} for user {request.user.id}")

            return JsonResponse({
                'success': True,
                'subscription_id': subscription_id,
                'approval_url': approval_url,
                'plan_type': plan_type,
                'billing_cycle': billing_cycle
            })
        else:
            logger.error(f"PayPal subscription creation failed: {response.status_code} - {response.text[:200]}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to create PayPal subscription',
                'error_code': 'PAYPAL_SUBSCRIPTION_FAILED'
            }, status=500)

    except Exception as e:
        logger.exception(f"Error creating subscription: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def cancel_subscription(request):
    """Cancel user's active subscription"""
    try:
        subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).first()

        if not subscription or not subscription.paypal_subscription_id:
            return JsonResponse({
                'success': False,
                'error': 'No active subscription found'
            }, status=404)

        # Cancel subscription in PayPal
        access_token = get_paypal_access_token()
        mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
        base_url = 'https://api-m.paypal.com' if mode == 'live' else 'https://api-m.sandbox.paypal.com'

        response = requests.post(
            f'{base_url}/v1/billing/subscriptions/{subscription.paypal_subscription_id}/cancel',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            },
            json={"reason": "User requested cancellation"},
            timeout=10
        )

        if response.status_code == 204:
            # Update local record
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()

            logger.info(f"Subscription cancelled: {subscription.id} for user {request.user.id}")

            return JsonResponse({
                'success': True,
                'message': 'Subscription cancelled successfully'
            })
        else:
            logger.error(f"PayPal cancellation failed: {response.status_code}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to cancel subscription with PayPal'
            }, status=500)

    except Exception as e:
        logger.exception(f"Error cancelling subscription: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_subscription_status(request):
    """Get user's subscription status"""
    try:
        subscription = Subscription.objects.filter(user=request.user).first()

        if not subscription:
            return JsonResponse({
                'success': True,
                'has_subscription': False,
                'plan_tier': 'free'
            })

        return JsonResponse({
            'success': True,
            'has_subscription': True,
            'plan_tier': subscription.plan_tier,
            'billing_cycle': subscription.billing_cycle,
            'status': subscription.status,
            'current_period_end': subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            'is_trial': subscription.is_trial,
            'monthly_price': float(subscription.monthly_price),
            'cancelled_at': subscription.cancelled_at.isoformat() if subscription.cancelled_at else None
        })

    except Exception as e:
        logger.exception(f"Error getting subscription status: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def paypal_webhook(request):
    """
    Handle PayPal webhooks for subscription events
    Events: BILLING.SUBSCRIPTION.ACTIVATED, BILLING.SUBSCRIPTION.CANCELLED,
            PAYMENT.SALE.COMPLETED, etc.
    """
    try:
        # Verify webhook signature
        webhook_id = getattr(settings, 'PAYPAL_WEBHOOK_ID', None)
        if webhook_id:
            if not verify_paypal_webhook(request, webhook_id):
                logger.warning("Invalid PayPal webhook signature")
                return JsonResponse({'error': 'Invalid signature'}, status=400)

        # Parse webhook data
        webhook_data = json.loads(request.body)
        event_type = webhook_data.get('event_type')
        resource = webhook_data.get('resource', {})

        # Store webhook event
        PayPalWebhookEvent.objects.create(
            event_type=event_type,
            event_data=webhook_data,
            processed=False
        )

        # Handle different event types
        if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
            handle_subscription_activated(resource)
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            handle_subscription_cancelled(resource)
        elif event_type == 'BILLING.SUBSCRIPTION.SUSPENDED':
            handle_subscription_suspended(resource)
        elif event_type == 'BILLING.SUBSCRIPTION.EXPIRED':
            handle_subscription_expired(resource)
        elif event_type == 'PAYMENT.SALE.COMPLETED':
            handle_payment_completed(resource)
        elif event_type == 'PAYMENT.SALE.REFUNDED':
            handle_payment_refunded(resource)

        return JsonResponse({'success': True}, status=200)

    except Exception as e:
        logger.exception(f"Error processing PayPal webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def verify_paypal_webhook(request, webhook_id):
    """Verify PayPal webhook signature"""
    try:
        # Get headers
        transmission_id = request.META.get('HTTP_PAYPAL_TRANSMISSION_ID')
        transmission_time = request.META.get('HTTP_PAYPAL_TRANSMISSION_TIME')
        cert_url = request.META.get('HTTP_PAYPAL_CERT_URL')
        auth_algo = request.META.get('HTTP_PAYPAL_AUTH_ALGO')
        transmission_sig = request.META.get('HTTP_PAYPAL_TRANSMISSION_SIG')

        # Verify with PayPal
        access_token = get_paypal_access_token()
        mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
        base_url = 'https://api-m.paypal.com' if mode == 'live' else 'https://api-m.sandbox.paypal.com'

        verify_data = {
            "transmission_id": transmission_id,
            "transmission_time": transmission_time,
            "cert_url": cert_url,
            "auth_algo": auth_algo,
            "transmission_sig": transmission_sig,
            "webhook_id": webhook_id,
            "webhook_event": json.loads(request.body)
        }

        response = requests.post(
            f'{base_url}/v1/notifications/verify-webhook-signature',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            },
            json=verify_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('verification_status') == 'SUCCESS'

        return False
    except Exception as e:
        logger.exception(f"Webhook verification error: {str(e)}")
        return False


def handle_subscription_activated(resource):
    """Handle BILLING.SUBSCRIPTION.ACTIVATED event"""
    subscription_id = resource.get('id')
    custom_id = resource.get('custom_id', '')

    try:
        # Parse custom_id: user_id:plan_type:billing_cycle
        parts = custom_id.split(':')
        if len(parts) >= 3:
            user_id = int(parts[0])
            plan_type = parts[1]
            billing_cycle = parts[2]

            # Update subscription status
            subscription = Subscription.objects.filter(
                paypal_subscription_id=subscription_id
            ).first()

            if subscription:
                subscription.status = 'active'
                subscription.current_period_start = timezone.now()
                # Calculate next billing date
                if billing_cycle == 'monthly':
                    subscription.current_period_end = timezone.now() + timedelta(days=30)
                else:
                    subscription.current_period_end = timezone.now() + timedelta(days=365)
                subscription.save()

                logger.info(f"Subscription activated: {subscription_id}")
            else:
                logger.warning(f"Subscription not found for activation: {subscription_id}")
    except Exception as e:
        logger.exception(f"Error handling subscription activation: {str(e)}")


def handle_subscription_cancelled(resource):
    """Handle BILLING.SUBSCRIPTION.CANCELLED event"""
    subscription_id = resource.get('id')

    try:
        subscription = Subscription.objects.filter(
            paypal_subscription_id=subscription_id
        ).first()

        if subscription:
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()

            logger.info(f"Subscription cancelled: {subscription_id}")
    except Exception as e:
        logger.exception(f"Error handling subscription cancellation: {str(e)}")


def handle_subscription_suspended(resource):
    """Handle BILLING.SUBSCRIPTION.SUSPENDED event"""
    subscription_id = resource.get('id')

    try:
        subscription = Subscription.objects.filter(
            paypal_subscription_id=subscription_id
        ).first()

        if subscription:
            subscription.status = 'suspended'
            subscription.save()

            logger.info(f"Subscription suspended: {subscription_id}")
    except Exception as e:
        logger.exception(f"Error handling subscription suspension: {str(e)}")


def handle_subscription_expired(resource):
    """Handle BILLING.SUBSCRIPTION.EXPIRED event"""
    subscription_id = resource.get('id')

    try:
        subscription = Subscription.objects.filter(
            paypal_subscription_id=subscription_id
        ).first()

        if subscription:
            subscription.status = 'expired'
            subscription.save()

            logger.info(f"Subscription expired: {subscription_id}")
    except Exception as e:
        logger.exception(f"Error handling subscription expiration: {str(e)}")


def handle_payment_completed(resource):
    """Handle PAYMENT.SALE.COMPLETED event"""
    try:
        # Extract payment details
        billing_agreement_id = resource.get('billing_agreement_id')
        amount = Decimal(resource.get('amount', {}).get('total', '0'))
        currency = resource.get('amount', {}).get('currency', 'USD')
        sale_id = resource.get('id')

        # Find subscription
        subscription = Subscription.objects.filter(
            paypal_subscription_id=billing_agreement_id
        ).first()

        if subscription:
            # Create payment record
            Payment.objects.create(
                user=subscription.user,
                subscription=subscription,
                paypal_order_id=sale_id,
                paypal_capture_id=sale_id,
                amount=amount,
                currency=currency,
                status='completed',
                plan_tier=subscription.plan_tier,
                billing_cycle=subscription.billing_cycle
            )

            logger.info(f"Payment completed: {sale_id} for subscription {billing_agreement_id}")
    except Exception as e:
        logger.exception(f"Error handling payment completion: {str(e)}")


def handle_payment_refunded(resource):
    """Handle PAYMENT.SALE.REFUNDED event"""
    try:
        sale_id = resource.get('sale_id')

        # Find and update payment
        payment = Payment.objects.filter(paypal_capture_id=sale_id).first()
        if payment:
            payment.status = 'refunded'
            payment.save()

            logger.info(f"Payment refunded: {sale_id}")
    except Exception as e:
        logger.exception(f"Error handling payment refund: {str(e)}")
