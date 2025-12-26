"""
Billing API Views
Handles subscription management and payment processing
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Subscription, PaymentHistory
from .sales_tax import get_plan_pricing_with_tax, calculate_total_with_tax
from .paypal_integration import PayPalClient, PLAN_DISPLAY_NAMES
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription(request):
    """
    Get current user's subscription details
    """
    try:
        subscription = request.user.subscription
        return Response({
            'plan': subscription.plan,
            'status': subscription.status,
            'billing_cycle': subscription.billing_cycle,
            'started_at': subscription.started_at,
            'expires_at': subscription.expires_at,
            'auto_renew': subscription.auto_renew,
            'next_billing_date': subscription.next_billing_date,
            'is_active': subscription.is_active(),
        })
    except Subscription.DoesNotExist:
        return Response({
            'error': 'No active subscription found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_history(request):
    """
    Get user's payment history
    """
    payments = PaymentHistory.objects.filter(user=request.user)
    payment_data = []

    for payment in payments:
        payment_data.append({
            'id': payment.id,
            'amount': float(payment.amount),
            'currency': payment.currency,
            'payment_method': payment.payment_method,
            'payment_status': payment.payment_status,
            'transaction_id': payment.transaction_id,
            'description': payment.description,
            'created_at': payment.created_at,
        })

    return Response({
        'payments': payment_data,
        'total_payments': len(payment_data),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upgrade_plan(request):
    """
    Upgrade user's subscription plan
    """
    new_plan = request.data.get('plan')

    # Normalize plan name (support both basic/pro and legacy bronze/silver)
    plan_normalized = new_plan.lower()
    if plan_normalized == 'bronze':
        plan_normalized = 'basic'
    elif plan_normalized == 'silver':
        plan_normalized = 'pro'

    if plan_normalized not in ['basic', 'pro']:
        return Response({
            'error': 'Invalid plan selected. Must be "basic" or "pro"'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        subscription = request.user.subscription
        subscription.plan = plan_normalized
        subscription.save()

        logger.info(f"User {request.user.username} upgraded to {plan_normalized}")

        return Response({
            'message': f'Successfully upgraded to {plan_normalized} plan',
            'plan': plan_normalized,
        })
    except Subscription.DoesNotExist:
        return Response({
            'error': 'No active subscription found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """
    Cancel user's subscription (at end of billing period)
    """
    try:
        subscription = request.user.subscription
        subscription.auto_renew = False
        subscription.status = 'cancelled'
        subscription.save()

        logger.info(f"User {request.user.username} cancelled subscription")

        return Response({
            'message': 'Subscription cancelled successfully',
            'expires_at': subscription.expires_at,
        })
    except Subscription.DoesNotExist:
        return Response({
            'error': 'No active subscription found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_pricing(request):
    """
    Get subscription pricing for all plans with sales tax

    Query params:
        - billing_cycle: 'monthly' or 'yearly' (default: 'monthly')
    """
    billing_cycle = request.GET.get('billing_cycle', 'monthly')

    if billing_cycle not in ['monthly', 'yearly']:
        return Response({
            'error': 'Invalid billing cycle. Must be "monthly" or "yearly"'
        }, status=status.HTTP_400_BAD_REQUEST)

    pricing = {
        'basic': get_plan_pricing_with_tax('basic', billing_cycle),
        'pro': get_plan_pricing_with_tax('pro', billing_cycle),
    }

    return Response({
        'pricing': pricing,
        'billing_cycle': billing_cycle,
    })


@api_view(['GET'])
def get_plan_pricing(request, plan):
    """
    Get pricing for a specific plan with sales tax

    Args:
        plan (str): Plan tier ('basic', 'pro')

    Query params:
        - billing_cycle: 'monthly' or 'yearly' (default: 'monthly')
    """
    # Normalize plan name (support both basic/pro and legacy bronze/silver)
    plan_normalized = plan.lower()
    if plan_normalized == 'bronze':
        plan_normalized = 'basic'
    elif plan_normalized == 'silver':
        plan_normalized = 'pro'

    if plan_normalized not in ['basic', 'pro']:
        return Response({
            'error': 'Invalid plan. Must be "basic" or "pro"'
        }, status=status.HTTP_400_BAD_REQUEST)

    billing_cycle = request.GET.get('billing_cycle', 'monthly')

    if billing_cycle not in ['monthly', 'yearly']:
        return Response({
            'error': 'Invalid billing cycle. Must be "monthly" or "yearly"'
        }, status=status.HTTP_400_BAD_REQUEST)

    pricing = get_plan_pricing_with_tax(plan_normalized, billing_cycle)

    if pricing is None:
        return Response({
            'error': 'Failed to calculate pricing'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(pricing)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_paypal_subscription(request):
    """
    Create a PayPal subscription for a user

    Request body:
        - plan: Plan tier ('basic', 'pro')
        - billing_cycle: Billing cycle ('monthly', 'yearly')

    Returns:
        - subscription_id: PayPal subscription ID
        - approval_url: URL to redirect user for PayPal approval
    """
    plan = request.data.get('plan')
    billing_cycle = request.data.get('billing_cycle', 'monthly')

    # Normalize plan name (support both basic/pro and legacy bronze/silver)
    plan_normalized = plan.lower() if plan else ''
    if plan_normalized == 'bronze':
        plan_normalized = 'basic'
    elif plan_normalized == 'silver':
        plan_normalized = 'pro'

    # Validate plan
    if plan_normalized not in ['basic', 'pro']:
        return Response({
            'error': 'Invalid plan. Must be "basic" or "pro"'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate billing cycle
    if billing_cycle not in ['monthly', 'yearly']:
        return Response({
            'error': 'Invalid billing cycle. Must be "monthly" or "yearly"'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get pricing with tax
    pricing = get_plan_pricing_with_tax(plan_normalized, billing_cycle)
    if not pricing:
        return Response({
            'error': 'Failed to calculate pricing'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Get display name for PayPal plan
    plan_display_name = PLAN_DISPLAY_NAMES.get(plan_normalized, plan_normalized.capitalize())

    # Create or get PayPal billing plan
    paypal_client = PayPalClient()
    paypal_plan_id = paypal_client.create_or_get_billing_plan(
        plan_name=plan_display_name,
        plan_price=float(pricing['total']),
        billing_cycle=billing_cycle
    )

    if not paypal_plan_id:
        return Response({
            'error': 'Failed to create or retrieve PayPal billing plan'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Create PayPal subscription
    subscription_data = paypal_client.create_subscription(
        plan_id=paypal_plan_id,
        user_email=request.user.email
    )

    if not subscription_data:
        return Response({
            'error': 'Failed to create PayPal subscription'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Extract approval URL
    approval_url = None
    for link in subscription_data.get('links', []):
        if link.get('rel') == 'approve':
            approval_url = link.get('href')
            break

    if not approval_url:
        return Response({
            'error': 'No approval URL returned from PayPal'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Store subscription info in database
    try:
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={
                'plan': plan_normalized,
                'billing_cycle': billing_cycle,
                'status': 'pending',
            }
        )

        if not created:
            subscription.plan = plan_normalized
            subscription.billing_cycle = billing_cycle
            subscription.status = 'pending'

        subscription.paypal_subscription_id = subscription_data.get('id')
        subscription.save()

        logger.info(f"Created PayPal subscription for {request.user.username}: {subscription_data.get('id')}")

    except Exception as e:
        logger.error(f"Failed to save subscription to database: {e}")

    return Response({
        'subscription_id': subscription_data.get('id'),
        'approval_url': approval_url,
        'plan': plan_normalized,
        'billing_cycle': billing_cycle,
        'status': 'pending_approval',
        'price': pricing['total'],
    })
