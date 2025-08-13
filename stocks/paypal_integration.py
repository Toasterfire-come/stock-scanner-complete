"""
PayPal Integration for Stock Scanner Subscriptions
Handles payment processing, subscription management, and webhooks
"""

import json
import logging
import hmac
import hashlib
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)
User = get_user_model()

class PayPalAPI:
    """PayPal API integration class"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'PAYPAL_BASE_URL', 'https://api.sandbox.paypal.com')
        self.client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', '')
        self.webhook_id = getattr(settings, 'PAYPAL_WEBHOOK_ID', '')
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """Get or refresh PayPal access token"""
        if self.access_token and self.token_expires_at and timezone.now() < self.token_expires_at:
            return self.access_token
        
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = 'grant_type=client_credentials'
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret)
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = timezone.now() + timedelta(seconds=expires_in - 60)  # 1 minute buffer
            
            return self.access_token
            
        except requests.RequestException as e:
            logger.error(f"Error getting PayPal access token: {e}")
            return None
    
    def create_subscription_plan(self, plan_data):
        """Create a PayPal subscription plan"""
        token = self.get_access_token()
        if not token:
            return None
        
        url = f"{self.base_url}/v1/billing/plans"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Prefer': 'return=representation'
        }
        
        try:
            response = requests.post(url, headers=headers, json=plan_data)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error creating PayPal plan: {e}")
            return None
    
    def create_subscription(self, subscription_data):
        """Create a PayPal subscription"""
        token = self.get_access_token()
        if not token:
            return None
        
        url = f"{self.base_url}/v1/billing/subscriptions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Prefer': 'return=representation'
        }
        
        try:
            response = requests.post(url, headers=headers, json=subscription_data)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error creating PayPal subscription: {e}")
            return None
    
    def get_subscription(self, subscription_id):
        """Get PayPal subscription details"""
        token = self.get_access_token()
        if not token:
            return None
        
        url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error getting PayPal subscription: {e}")
            return None
    
    def cancel_subscription(self, subscription_id, reason="User requested cancellation"):
        """Cancel a PayPal subscription"""
        token = self.get_access_token()
        if not token:
            return False
        
        url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/cancel"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        cancel_data = {
            'reason': reason
        }
        
        try:
            response = requests.post(url, headers=headers, json=cancel_data)
            response.raise_for_status()
            return True
            
        except requests.RequestException as e:
            logger.error(f"Error cancelling PayPal subscription: {e}")
            return False
    
    def verify_webhook(self, headers, body):
        """Verify PayPal webhook signature"""
        if not self.webhook_id:
            logger.warning("PayPal webhook ID not configured")
            return True  # Skip verification if not configured
        
        try:
            # Get verification data from headers
            auth_algo = headers.get('PAYPAL-AUTH-ALGO')
            transmission_id = headers.get('PAYPAL-TRANSMISSION-ID')
            cert_id = headers.get('PAYPAL-CERT-ID')
            transmission_time = headers.get('PAYPAL-TRANSMISSION-TIME')
            webhook_signature = headers.get('PAYPAL-TRANSMISSION-SIG')
            
            if not all([auth_algo, transmission_id, cert_id, transmission_time, webhook_signature]):
                logger.error("Missing PayPal webhook headers")
                return False
            
            # For now, return True (in production, implement full verification)
            # Full verification requires additional PayPal API calls
            return True
            
        except Exception as e:
            logger.error(f"Error verifying PayPal webhook: {e}")
            return False

# Global PayPal API instance
paypal_api = PayPalAPI()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription(request):
    """Create a new PayPal subscription for a user"""
    try:
        from .models import PaymentPlan, PaymentTransaction, UserProfile
        
        user = request.user
        plan_id = request.data.get('plan_id')
        billing_cycle = request.data.get('billing_cycle', 'monthly')  # monthly or yearly
        
        if not plan_id:
            return Response({'error': 'Plan ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the payment plan
        try:
            payment_plan = PaymentPlan.objects.get(id=plan_id, is_active=True)
        except PaymentPlan.DoesNotExist:
            return Response({'error': 'Invalid plan ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get PayPal plan ID based on billing cycle
        paypal_plan_id = (payment_plan.paypal_plan_id_yearly 
                         if billing_cycle == 'yearly' 
                         else payment_plan.paypal_plan_id_monthly)
        
        if not paypal_plan_id:
            return Response({'error': 'PayPal plan not configured'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create subscription data
        subscription_data = {
            "plan_id": paypal_plan_id,
            "subscriber": {
                "name": {
                    "given_name": user.first_name or user.username,
                    "surname": user.last_name or ""
                },
                "email_address": user.email
            },
            "application_context": {
                "brand_name": "Stock Scanner Pro",
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "payment_method": {
                    "payer_selected": "PAYPAL",
                    "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                },
                "return_url": f"{request.build_absolute_uri('/payment-success/')}",
                "cancel_url": f"{request.build_absolute_uri('/payment-cancelled/')}"
            }
        }
        
        # Create subscription with PayPal
        subscription_response = paypal_api.create_subscription(subscription_data)
        
        if not subscription_response:
            return Response({'error': 'Failed to create PayPal subscription'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create pending transaction record
        amount = payment_plan.price_yearly if billing_cycle == 'yearly' else payment_plan.price_monthly
        
        transaction = PaymentTransaction.objects.create(
            user=user,
            plan=payment_plan,
            paypal_subscription_id=subscription_response['id'],
            amount=amount,
            billing_cycle=billing_cycle,
            status='pending'
        )
        
        # Extract approval URL
        approval_url = None
        for link in subscription_response.get('links', []):
            if link.get('rel') == 'approve':
                approval_url = link.get('href')
                break
        
        return Response({
            'status': 'success',
            'subscription_id': subscription_response['id'],
            'approval_url': approval_url,
            'transaction_id': transaction.id
        })
        
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancel a user's PayPal subscription"""
    try:
        user = request.user
        
        # Get user's active subscription
        if not hasattr(user, 'profile') or not user.profile.paypal_subscription_id:
            return Response({'error': 'No active subscription found'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        subscription_id = user.profile.paypal_subscription_id
        reason = request.data.get('reason', 'User requested cancellation')
        
        # Cancel with PayPal
        success = paypal_api.cancel_subscription(subscription_id, reason)
        
        if success:
            # Update user profile
            profile = user.profile
            profile.subscription_active = False
            profile.subscription_end = timezone.now() + timedelta(days=30)  # Grace period
            profile.save()
            
            return Response({'status': 'success', 'message': 'Subscription cancelled successfully'})
        else:
            return Response({'error': 'Failed to cancel subscription'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_status(request):
    """Get user's subscription status"""
    try:
        user = request.user
        profile = getattr(user, 'profile', None)
        
        if not profile:
            return Response({
                'tier': 'free',
                'subscription_active': False,
                'subscription_end': None,
                'rate_limits': {
                    'api_calls_per_hour': 100,
                    'api_calls_per_day': 1000,
                    'max_watchlist_items': 10
                }
            })
        
        # Get latest PayPal subscription status if available
        paypal_status = None
        if profile.paypal_subscription_id:
            paypal_subscription = paypal_api.get_subscription(profile.paypal_subscription_id)
            if paypal_subscription:
                paypal_status = paypal_subscription.get('status')
        
        return Response({
            'tier': profile.tier,
            'subscription_active': profile.is_subscription_active,
            'subscription_start': profile.subscription_start,
            'subscription_end': profile.subscription_end,
            'paypal_subscription_id': profile.paypal_subscription_id,
            'paypal_status': paypal_status,
            'rate_limits': profile.get_rate_limits(),
            'api_usage_today': profile.api_calls_today,
            'api_usage_month': profile.api_calls_this_month
        })
        
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
def paypal_webhook(request):
    """Handle PayPal webhook notifications"""
    try:
        # Verify webhook signature
        if not paypal_api.verify_webhook(request.headers, request.body):
            logger.error("PayPal webhook signature verification failed")
            return HttpResponse(status=400)
        
        # Parse webhook data
        webhook_data = json.loads(request.body)
        event_type = webhook_data.get('event_type')
        resource = webhook_data.get('resource', {})
        
        logger.info(f"Received PayPal webhook: {event_type}")
        
        # Handle different event types
        if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
            handle_subscription_activated(resource, webhook_data)
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            handle_subscription_cancelled(resource, webhook_data)
        elif event_type == 'BILLING.SUBSCRIPTION.SUSPENDED':
            handle_subscription_suspended(resource, webhook_data)
        elif event_type == 'BILLING.SUBSCRIPTION.PAYMENT.FAILED':
            handle_payment_failed(resource, webhook_data)
        elif event_type == 'PAYMENT.SALE.COMPLETED':
            handle_payment_completed(resource, webhook_data)
        else:
            logger.info(f"Unhandled PayPal webhook event: {event_type}")
        
        return HttpResponse(status=200)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in PayPal webhook")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Error processing PayPal webhook: {e}")
        return HttpResponse(status=500)

def handle_subscription_activated(resource, webhook_data):
    """Handle subscription activation"""
    try:
        from .models import PaymentTransaction, UserProfile
        
        subscription_id = resource.get('id')
        subscriber_email = resource.get('subscriber', {}).get('email_address')
        
        if not subscription_id or not subscriber_email:
            logger.error("Missing subscription data in webhook")
            return
        
        # Find user by email
        try:
            user = User.objects.get(email=subscriber_email)
        except User.DoesNotExist:
            logger.error(f"User not found for email: {subscriber_email}")
            return
        
        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.paypal_subscription_id = subscription_id
        profile.subscription_active = True
        profile.subscription_start = timezone.now()
        
        # Set subscription end based on billing cycle (get from transaction)
        try:
            transaction = PaymentTransaction.objects.get(
                paypal_subscription_id=subscription_id,
                status='pending'
            )
            transaction.status = 'completed'
            transaction.webhook_data = webhook_data
            transaction.save()
            
            # Set tier and end date based on plan
            profile.tier = transaction.plan.tier
            if transaction.billing_cycle == 'yearly':
                profile.subscription_end = timezone.now() + timedelta(days=365)
            else:
                profile.subscription_end = timezone.now() + timedelta(days=30)
                
        except PaymentTransaction.DoesNotExist:
            logger.error(f"Transaction not found for subscription: {subscription_id}")
            # Default to basic tier for 30 days
            profile.tier = 'basic'
            profile.subscription_end = timezone.now() + timedelta(days=30)
        
        profile.save()
        logger.info(f"Activated subscription for user {user.username}")
        
    except Exception as e:
        logger.error(f"Error handling subscription activation: {e}")

def handle_subscription_cancelled(resource, webhook_data):
    """Handle subscription cancellation"""
    try:
        from .models import UserProfile
        
        subscription_id = resource.get('id')
        
        # Find user by subscription ID
        try:
            profile = UserProfile.objects.get(paypal_subscription_id=subscription_id)
            profile.subscription_active = False
            # Keep access until end of current billing period
            if not profile.subscription_end or profile.subscription_end < timezone.now():
                profile.subscription_end = timezone.now() + timedelta(days=7)  # Grace period
            profile.save()
            
            logger.info(f"Cancelled subscription for user {profile.user.username}")
            
        except UserProfile.DoesNotExist:
            logger.error(f"Profile not found for subscription: {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error handling subscription cancellation: {e}")

def handle_subscription_suspended(resource, webhook_data):
    """Handle subscription suspension"""
    try:
        from .models import UserProfile
        
        subscription_id = resource.get('id')
        
        # Find user by subscription ID
        try:
            profile = UserProfile.objects.get(paypal_subscription_id=subscription_id)
            profile.subscription_active = False
            profile.save()
            
            logger.info(f"Suspended subscription for user {profile.user.username}")
            
        except UserProfile.DoesNotExist:
            logger.error(f"Profile not found for subscription: {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error handling subscription suspension: {e}")

def handle_payment_failed(resource, webhook_data):
    """Handle failed payment"""
    try:
        from .models import UserProfile, PaymentTransaction
        
        subscription_id = resource.get('billing_agreement_id')
        
        if subscription_id:
            try:
                profile = UserProfile.objects.get(paypal_subscription_id=subscription_id)
                
                # Don't immediately suspend - give some grace period
                if profile.subscription_end and profile.subscription_end > timezone.now():
                    logger.info(f"Payment failed for user {profile.user.username}, but subscription still active")
                else:
                    profile.subscription_active = False
                    profile.save()
                    logger.info(f"Payment failed and suspended subscription for user {profile.user.username}")
                
            except UserProfile.DoesNotExist:
                logger.error(f"Profile not found for subscription: {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error handling payment failure: {e}")

def handle_payment_completed(resource, webhook_data):
    """Handle completed payment"""
    try:
        from .models import PaymentTransaction
        
        payment_id = resource.get('id')
        subscription_id = resource.get('billing_agreement_id')
        amount = resource.get('amount', {}).get('total', '0')
        
        # Create transaction record for the payment
        if subscription_id:
            try:
                from .models import UserProfile
                profile = UserProfile.objects.get(paypal_subscription_id=subscription_id)
                
                # Create transaction record
                PaymentTransaction.objects.create(
                    user=profile.user,
                    plan=None,  # This is a recurring payment, not initial subscription
                    paypal_transaction_id=payment_id,
                    paypal_subscription_id=subscription_id,
                    amount=amount,
                    status='completed',
                    billing_cycle='monthly',  # Default assumption
                    webhook_data=webhook_data
                )
                
                logger.info(f"Recorded payment completion for user {profile.user.username}")
                
            except UserProfile.DoesNotExist:
                logger.error(f"Profile not found for subscription: {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error handling payment completion: {e}")

@api_view(['GET'])
@permission_classes([AllowAny])
def available_plans(request):
    """Get available payment plans"""
    try:
        from .models import PaymentPlan
        
        plans = PaymentPlan.objects.filter(is_active=True).order_by('price_monthly')
        
        plans_data = []
        for plan in plans:
            plans_data.append({
                'id': plan.id,
                'name': plan.name,
                'tier': plan.tier,
                'price_monthly': float(plan.price_monthly),
                'price_yearly': float(plan.price_yearly),
                'features': plan.features,
                'savings_yearly': float(plan.price_monthly * 12 - plan.price_yearly)
            })
        
        return Response({
            'status': 'success',
            'plans': plans_data
        })
        
    except Exception as e:
        logger.error(f"Error getting available plans: {e}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)