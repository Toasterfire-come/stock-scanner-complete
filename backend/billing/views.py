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

    if new_plan not in ['bronze', 'silver', 'gold']:
        return Response({
            'error': 'Invalid plan selected'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        subscription = request.user.subscription
        subscription.plan = new_plan
        subscription.save()

        logger.info(f"User {request.user.username} upgraded to {new_plan}")

        return Response({
            'message': f'Successfully upgraded to {new_plan} plan',
            'plan': new_plan,
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
        'bronze': get_plan_pricing_with_tax('bronze', billing_cycle),
        'silver': get_plan_pricing_with_tax('silver', billing_cycle),
        'gold': get_plan_pricing_with_tax('gold', billing_cycle),
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
        plan (str): Plan tier ('bronze', 'silver', 'gold')

    Query params:
        - billing_cycle: 'monthly' or 'yearly' (default: 'monthly')
    """
    if plan not in ['bronze', 'silver', 'gold']:
        return Response({
            'error': 'Invalid plan. Must be "bronze", "silver", or "gold"'
        }, status=status.HTTP_400_BAD_REQUEST)

    billing_cycle = request.GET.get('billing_cycle', 'monthly')

    if billing_cycle not in ['monthly', 'yearly']:
        return Response({
            'error': 'Invalid billing cycle. Must be "monthly" or "yearly"'
        }, status=status.HTTP_400_BAD_REQUEST)

    pricing = get_plan_pricing_with_tax(plan, billing_cycle)

    if pricing is None:
        return Response({
            'error': 'Failed to calculate pricing'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(pricing)
