"""
Payment service for Stripe integration
"""
import os
import stripe
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

class PaymentService:
    """
    Production-ready Stripe payment integration
    """
    
    # Plan configuration
    PLANS = {
        'free': {
            'name': 'Free Plan',
            'price': 0,
            'stripe_price_id': None,
            'features': {
                'api_calls': 100,
                'storage_mb': 100,
                'watchlist_items': 5,
                'real_time_data': False,
                'priority_support': False
            }
        },
        'basic': {
            'name': 'Basic Plan',
            'price': 15,
            'stripe_price_id': os.getenv('STRIPE_BASIC_PRICE_ID'),
            'features': {
                'api_calls': 1000,
                'storage_mb': 1000,
                'watchlist_items': -1,  # Unlimited
                'real_time_data': False,
                'priority_support': False
            }
        },
        'pro': {
            'name': 'Pro Plan',
            'price': 30,
            'stripe_price_id': os.getenv('STRIPE_PRO_PRICE_ID'),
            'features': {
                'api_calls': 10000,
                'storage_mb': 10000,
                'watchlist_items': -1,
                'real_time_data': True,
                'priority_support': True
            }
        },
        'enterprise': {
            'name': 'Enterprise Plan',
            'price': 100,
            'stripe_price_id': os.getenv('STRIPE_ENTERPRISE_PRICE_ID'),
            'features': {
                'api_calls': -1,  # Unlimited
                'storage_mb': -1,
                'watchlist_items': -1,
                'real_time_data': True,
                'priority_support': True
            }
        }
    }
    
    @classmethod
    async def create_customer(
        cls,
        email: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a Stripe customer
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
            raise
    
    @classmethod
    async def create_checkout_session(
        cls,
        customer_id: str,
        plan: str,
        success_url: str,
        cancel_url: str,
        trial_days: int = 0
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for subscription
        """
        if plan not in cls.PLANS or plan == 'free':
            raise ValueError(f"Invalid plan: {plan}")
        
        plan_config = cls.PLANS[plan]
        
        if not plan_config['stripe_price_id']:
            raise ValueError(f"Stripe price ID not configured for plan: {plan}")
        
        try:
            session_params = {
                'payment_method_types': ['card'],
                'mode': 'subscription',
                'customer': customer_id,
                'line_items': [{
                    'price': plan_config['stripe_price_id'],
                    'quantity': 1
                }],
                'success_url': success_url,
                'cancel_url': cancel_url,
                'metadata': {
                    'plan': plan
                }
            }
            
            # Add trial period if specified
            if trial_days > 0:
                session_params['subscription_data'] = {
                    'trial_period_days': trial_days
                }
            
            session = stripe.checkout.Session.create(**session_params)
            
            logger.info(f"Created checkout session: {session.id}")
            return {
                'session_id': session.id,
                'url': session.url
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {str(e)}")
            raise
    
    @classmethod
    async def create_portal_session(
        cls,
        customer_id: str,
        return_url: str
    ) -> str:
        """
        Create a Stripe customer portal session for subscription management
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create portal session: {str(e)}")
            raise
    
    @classmethod
    async def cancel_subscription(
        cls,
        subscription_id: str,
        cancel_at_period_end: bool = True
    ) -> Dict[str, Any]:
        """
        Cancel a subscription
        """
        try:
            if cancel_at_period_end:
                # Cancel at the end of the current billing period
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                # Cancel immediately
                subscription = stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Cancelled subscription: {subscription_id}")
            return {
                'status': subscription.status,
                'cancel_at': subscription.cancel_at,
                'canceled_at': subscription.canceled_at
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            raise
    
    @classmethod
    async def update_subscription(
        cls,
        subscription_id: str,
        new_plan: str
    ) -> Dict[str, Any]:
        """
        Update subscription to a different plan
        """
        if new_plan not in cls.PLANS or new_plan == 'free':
            raise ValueError(f"Invalid plan: {new_plan}")
        
        plan_config = cls.PLANS[new_plan]
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Update the subscription
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': plan_config['stripe_price_id']
                }],
                proration_behavior='always_invoice'  # Prorate the change
            )
            
            logger.info(f"Updated subscription {subscription_id} to plan {new_plan}")
            return {
                'status': updated_subscription.status,
                'plan': new_plan,
                'current_period_end': updated_subscription.current_period_end
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update subscription: {str(e)}")
            raise
    
    @classmethod
    async def get_subscription_details(
        cls,
        subscription_id: str
    ) -> Dict[str, Any]:
        """
        Get subscription details
        """
        try:
            subscription = stripe.Subscription.retrieve(
                subscription_id,
                expand=['latest_invoice.payment_intent']
            )
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': datetime.fromtimestamp(subscription.current_period_start),
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end),
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'canceled_at': datetime.fromtimestamp(subscription.canceled_at) if subscription.canceled_at else None,
                'trial_end': datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else None
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscription details: {str(e)}")
            raise
    
    @classmethod
    async def handle_webhook(
        cls,
        payload: bytes,
        signature: str
    ) -> Dict[str, Any]:
        """
        Handle Stripe webhook events
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            logger.error("Invalid webhook payload")
            raise
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            raise
        
        # Handle different event types
        event_handlers = {
            'checkout.session.completed': cls._handle_checkout_completed,
            'customer.subscription.created': cls._handle_subscription_created,
            'customer.subscription.updated': cls._handle_subscription_updated,
            'customer.subscription.deleted': cls._handle_subscription_deleted,
            'invoice.payment_succeeded': cls._handle_payment_succeeded,
            'invoice.payment_failed': cls._handle_payment_failed
        }
        
        handler = event_handlers.get(event['type'])
        if handler:
            return await handler(event)
        
        logger.info(f"Unhandled webhook event type: {event['type']}")
        return {'status': 'unhandled'}
    
    @classmethod
    async def _handle_checkout_completed(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle successful checkout
        """
        session = event['data']['object']
        
        return {
            'event': 'checkout_completed',
            'customer_id': session['customer'],
            'subscription_id': session['subscription'],
            'plan': session['metadata'].get('plan')
        }
    
    @classmethod
    async def _handle_subscription_created(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle new subscription creation
        """
        subscription = event['data']['object']
        
        return {
            'event': 'subscription_created',
            'subscription_id': subscription['id'],
            'customer_id': subscription['customer'],
            'status': subscription['status']
        }
    
    @classmethod
    async def _handle_subscription_updated(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle subscription update
        """
        subscription = event['data']['object']
        
        return {
            'event': 'subscription_updated',
            'subscription_id': subscription['id'],
            'customer_id': subscription['customer'],
            'status': subscription['status']
        }
    
    @classmethod
    async def _handle_subscription_deleted(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle subscription cancellation
        """
        subscription = event['data']['object']
        
        return {
            'event': 'subscription_deleted',
            'subscription_id': subscription['id'],
            'customer_id': subscription['customer']
        }
    
    @classmethod
    async def _handle_payment_succeeded(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle successful payment
        """
        invoice = event['data']['object']
        
        return {
            'event': 'payment_succeeded',
            'invoice_id': invoice['id'],
            'customer_id': invoice['customer'],
            'amount': invoice['amount_paid'] / 100,  # Convert from cents
            'subscription_id': invoice['subscription']
        }
    
    @classmethod
    async def _handle_payment_failed(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle failed payment
        """
        invoice = event['data']['object']
        
        return {
            'event': 'payment_failed',
            'invoice_id': invoice['id'],
            'customer_id': invoice['customer'],
            'subscription_id': invoice['subscription']
        }
    
    @classmethod
    async def get_payment_methods(cls, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get customer's payment methods
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            
            return [{
                'id': pm.id,
                'brand': pm.card.brand,
                'last4': pm.card.last4,
                'exp_month': pm.card.exp_month,
                'exp_year': pm.card.exp_year,
                'is_default': pm.id == payment_methods.data[0].id if payment_methods.data else False
            } for pm in payment_methods.data]
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get payment methods: {str(e)}")
            raise
    
    @classmethod
    async def get_invoices(
        cls,
        customer_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get customer's invoices
        """
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            
            return [{
                'id': invoice.id,
                'number': invoice.number,
                'amount': invoice.amount_paid / 100,
                'currency': invoice.currency.upper(),
                'status': invoice.status,
                'created': datetime.fromtimestamp(invoice.created),
                'pdf_url': invoice.invoice_pdf,
                'hosted_url': invoice.hosted_invoice_url
            } for invoice in invoices.data]
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get invoices: {str(e)}")
            raise