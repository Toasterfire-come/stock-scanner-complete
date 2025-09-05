"""
Billing API Views for PayPal Integration
Handles subscription management and billing
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import json
import logging
import os
import paypalrestsdk

from .models import UserProfile, BillingHistory

logger = logging.getLogger(__name__)

# Configure PayPal
paypalrestsdk.configure({
    "mode": os.environ.get('PAYPAL_MODE', 'live'),
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET')
})

def get_plan_pricing():
    """Get pricing information for all plans"""
    return {
        'bronze': {'monthly': 24.99, 'annual': 249.99, 'trial': 1.00},
        'silver': {'monthly': 39.99, 'annual': 399.99, 'trial': 1.00},
        'gold': {'monthly': 89.99, 'annual': 899.99, 'trial': 1.00}
    }

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def create_paypal_order_api(request):
    """
    Create PayPal order for subscription
    URL: /api/billing/create-paypal-order/
    """
    try:
        data = json.loads(request.body)
        
        plan_type = data.get('plan_type')
        billing_cycle = data.get('billing_cycle', 'monthly')
        discount_code = data.get('discount_code')
        
        # Validate plan type
        valid_plans = ['bronze', 'silver', 'gold']
        if plan_type not in valid_plans:
            return Response({
                'success': False,
                'error': f'Invalid plan type. Must be one of: {valid_plans}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate billing cycle
        if billing_cycle not in ['monthly', 'annual']:
            return Response({
                'success': False,
                'error': 'Billing cycle must be monthly or annual'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get pricing
        pricing = get_plan_pricing()
        plan_pricing = pricing[plan_type]
        
        # Determine amount (use trial price for first-time users)
        user = getattr(request, 'user', None)
        amount = plan_pricing['trial']  # Default to trial price
        
        if user and user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.trial_used:
                    amount = plan_pricing[billing_cycle]
            except UserProfile.DoesNotExist:
                pass
        
        # Apply discount if provided
        # (You can add discount logic here)
        
        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "https://api.retailtradescanner.com/api/billing/paypal-success/",
                "cancel_url": "https://api.retailtradescanner.com/api/billing/paypal-cancel/"
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": "USD"
                },
                "description": f"Stock Scanner {plan_type.title()} Plan - {billing_cycle.title()}",
                "item_list": {
                    "items": [{
                        "name": f"Stock Scanner {plan_type.title()} Plan",
                        "sku": f"stockscanner-{plan_type}-{billing_cycle}",
                        "price": str(amount),
                        "currency": "USD",
                        "quantity": 1
                    }]
                }
            }]
        })
        
        if payment.create():
            # Save billing record
            if user and user.is_authenticated:
                BillingHistory.objects.create(
                    user=user,
                    plan_type=plan_type,
                    billing_cycle=billing_cycle,
                    amount=amount,
                    paypal_order_id=payment.id,
                    discount_code=discount_code or '',
                    status='pending'
                )
            
            # Get approval URL
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            
            return Response({
                'success': True,
                'order_id': payment.id,
                'approval_url': approval_url,
                'status': 'created',
                'amount': str(amount),
                'plan': plan_type,
                'billing_cycle': billing_cycle
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"PayPal payment creation failed: {payment.error}")
            return Response({
                'success': False,
                'error': 'Failed to create PayPal order',
                'details': payment.error
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"PayPal order creation error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Failed to create PayPal order'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def capture_paypal_order_api(request):
    """
    Capture PayPal payment and activate subscription
    URL: /api/billing/capture-paypal-order/
    """
    try:
        data = json.loads(request.body)
        
        order_id = data.get('order_id')
        payment_data = data.get('payment_data', {})
        
        if not order_id:
            return Response({
                'success': False,
                'error': 'Order ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get PayPal payment
        payment = paypalrestsdk.Payment.find(order_id)
        
        if not payment:
            return Response({
                'success': False,
                'error': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Execute payment
        if payment.execute({"payer_id": payment_data.get('PayerID')}):
            # Update billing record
            try:
                with transaction.atomic():
                    billing_record = BillingHistory.objects.get(paypal_order_id=order_id)
                    billing_record.status = 'completed'
                    billing_record.paypal_payment_id = payment.id
                    billing_record.save()
                    
                    # Update user profile
                    profile, created = UserProfile.objects.get_or_create(
                        user=billing_record.user,
                        defaults={'plan': 'free', 'is_premium': False}
                    )
                    
                    # Activate subscription
                    profile.plan = billing_record.plan_type
                    profile.is_premium = True
                    profile.subscription_active = True
                    
                    # Set subscription end date
                    if billing_record.billing_cycle == 'monthly':
                        profile.subscription_end_date = timezone.now() + timedelta(days=30)
                    else:  # annual
                        profile.subscription_end_date = timezone.now() + timedelta(days=365)
                    
                    # Mark trial as used if this was a trial payment
                    if billing_record.amount == 1.00:
                        profile.trial_used = True
                    
                    profile.save()
                
                return Response({
                    'success': True,
                    'status': 'completed',
                    'payment_id': payment.id,
                    'amount': str(billing_record.amount),
                    'currency': 'USD',
                    'plan': billing_record.plan_type,
                    'message': 'Payment successful and subscription activated'
                })
                
            except BillingHistory.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Billing record not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            logger.error(f"PayPal payment execution failed: {payment.error}")
            return Response({
                'success': False,
                'error': 'Payment execution failed',
                'details': payment.error
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"PayPal capture error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Payment capture failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def current_plan_api(request):
    """
    Get current user's plan information
    URL: /api/billing/current-plan/
    """
    try:
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'plan': 'free', 'is_premium': False}
        )
        
        pricing = get_plan_pricing()
        plan_pricing = pricing.get(profile.plan, {})
        
        return Response({
            'success': True,
            'data': {
                'current_plan': profile.plan,
                'is_premium': profile.is_premium,
                'subscription_active': profile.subscription_active,
                'subscription_end_date': profile.subscription_end_date.isoformat() if profile.subscription_end_date else None,
                'trial_used': profile.trial_used,
                'limits': profile.get_plan_limits(),
                'pricing': plan_pricing
            }
        })
        
    except Exception as e:
        logger.error(f"Current plan API error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Failed to get plan information'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def change_plan_api(request):
    """
    Change user's subscription plan
    URL: /api/billing/change-plan/
    """
    try:
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        data = json.loads(request.body)
        new_plan = data.get('plan')
        
        if new_plan not in ['free', 'bronze', 'silver', 'gold']:
            return Response({
                'success': False,
                'error': 'Invalid plan type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'plan': 'free', 'is_premium': False}
        )
        
        # For now, just update the plan (full subscription management would require more PayPal integration)
        profile.plan = new_plan
        profile.is_premium = new_plan != 'free'
        profile.save()
        
        return Response({
            'success': True,
            'message': f'Plan changed to {new_plan}',
            'data': {
                'new_plan': new_plan,
                'limits': profile.get_plan_limits()
            }
        })
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Change plan error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Plan change failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def billing_history_api(request):
    """
    Get user's billing history
    URL: /api/billing/history/
    """
    try:
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        billing_records = BillingHistory.objects.filter(user=user).order_by('-created_at')
        
        history = []
        for record in billing_records:
            history.append({
                'id': record.id,
                'plan_type': record.plan_type,
                'billing_cycle': record.billing_cycle,
                'amount': str(record.amount),
                'status': record.status,
                'paypal_order_id': record.paypal_order_id,
                'created_at': record.created_at.isoformat(),
                'updated_at': record.updated_at.isoformat()
            })
        
        return Response({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        logger.error(f"Billing history error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Failed to get billing history'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def billing_stats_api(request):
    """
    Get billing statistics
    URL: /api/billing/stats/
    """
    try:
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'plan': 'free', 'is_premium': False}
        )
        
        billing_records = BillingHistory.objects.filter(user=user)
        total_spent = sum(record.amount for record in billing_records if record.status == 'completed')
        
        return Response({
            'success': True,
            'data': {
                'total_transactions': billing_records.count(),
                'total_spent': str(total_spent),
                'current_plan': profile.plan,
                'subscription_active': profile.subscription_active,
                'next_billing_date': profile.subscription_end_date.isoformat() if profile.subscription_end_date else None
            }
        })
        
    except Exception as e:
        logger.error(f"Billing stats error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Failed to get billing stats'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)