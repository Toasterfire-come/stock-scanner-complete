"""
PayPal Integration Helper
Handles PayPal subscription and payment processing
"""

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class PayPalClient:
    """
    PayPal API client for subscription management
    """

    def __init__(self):
        self.client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', '')
        self.mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')

        # Set API endpoint based on mode
        if self.mode == 'live':
            self.base_url = 'https://api-m.paypal.com'
        else:
            self.base_url = 'https://api-m.sandbox.paypal.com'

        self.access_token = None

    def get_access_token(self):
        """
        Get OAuth 2.0 access token from PayPal
        """
        if self.access_token:
            return self.access_token

        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = {'grant_type': 'client_credentials'}

        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret)
            )
            response.raise_for_status()
            self.access_token = response.json()['access_token']
            return self.access_token
        except Exception as e:
            logger.error(f"Failed to get PayPal access token: {e}")
            return None

    def create_or_get_product(self):
        """Create or retrieve PayPal product for Trade Scan Pro"""
        token = self.get_access_token()
        if not token:
            return None

        # Check if product ID is in settings
        product_id = getattr(settings, 'PAYPAL_PRODUCT_ID', None)
        if product_id:
            return product_id

        url = f"{self.base_url}/v1/catalogs/products"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }

        payload = {
            'name': 'Trade Scan Pro Subscription',
            'description': 'Real-time stock scanner and trading analytics platform',
            'type': 'SERVICE',
            'category': 'SOFTWARE',
            'image_url': f"{settings.FRONTEND_URL}/logo.png",
            'home_url': settings.FRONTEND_URL,
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            product_data = response.json()
            product_id = product_data.get('id')
            logger.info(f"Created PayPal product: {product_id}")
            return product_id
        except Exception as e:
            logger.error(f"Failed to create PayPal product: {e}")
            # Return a default product ID if creation fails
            return 'PROD-TRADESCANPRO'

    def create_or_get_billing_plan(self, plan_name, plan_price, billing_cycle='monthly'):
        """
        Create or retrieve a PayPal billing plan

        Args:
            plan_name (str): Plan display name (e.g., "Basic", "Pro")
            plan_price (float): Plan price including tax
            billing_cycle (str): 'monthly' or 'yearly'

        Returns:
            str: PayPal Plan ID or None if failed
        """
        token = self.get_access_token()
        if not token:
            return None

        # First, ensure we have a product
        product_id = self.create_or_get_product()
        if not product_id:
            logger.error("Failed to get product ID")
            return None

        # Define billing frequency
        interval_unit = 'MONTH' if billing_cycle == 'monthly' else 'YEAR'
        interval_count = 1

        url = f"{self.base_url}/v1/billing/plans"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }

        plan_description = f"Trade Scan Pro - {plan_name} ({billing_cycle.capitalize()})"

        payload = {
            'product_id': product_id,
            'name': f"{plan_name} - {billing_cycle.capitalize()}",
            'description': plan_description,
            'status': 'ACTIVE',
            'billing_cycles': [
                {
                    'frequency': {
                        'interval_unit': interval_unit,
                        'interval_count': interval_count
                    },
                    'tenure_type': 'REGULAR',
                    'sequence': 1,
                    'total_cycles': 0,  # 0 = infinite
                    'pricing_scheme': {
                        'fixed_price': {
                            'value': str(plan_price),
                            'currency_code': 'USD'
                        }
                    }
                }
            ],
            'payment_preferences': {
                'auto_bill_outstanding': True,
                'setup_fee': {
                    'value': '0',
                    'currency_code': 'USD'
                },
                'setup_fee_failure_action': 'CONTINUE',
                'payment_failure_threshold': 3
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            plan_data = response.json()
            logger.info(f"Created PayPal billing plan: {plan_data.get('id')} for {plan_name} {billing_cycle}")
            return plan_data.get('id')
        except Exception as e:
            logger.error(f"Failed to create PayPal billing plan: {e}")
            # If plan already exists, try to find it
            return self._find_existing_plan(plan_name, billing_cycle)

    def _find_existing_plan(self, plan_name, billing_cycle):
        """Find existing billing plan by name"""
        token = self.get_access_token()
        if not token:
            return None

        url = f"{self.base_url}/v1/billing/plans"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            plans = response.json().get('plans', [])

            # Search for matching plan
            search_name = f"{plan_name} - {billing_cycle.capitalize()}"
            for plan in plans:
                if plan.get('name') == search_name and plan.get('status') == 'ACTIVE':
                    logger.info(f"Found existing PayPal plan: {plan.get('id')}")
                    return plan.get('id')

            return None
        except Exception as e:
            logger.error(f"Failed to find existing PayPal plan: {e}")
            return None

    def create_subscription(self, plan_id, user_email):
        """
        Create a PayPal subscription

        Args:
            plan_id (str): PayPal plan ID
            user_email (str): User's email address

        Returns:
            dict: Subscription details with approval URL
        """
        token = self.get_access_token()
        if not token:
            return None

        url = f"{self.base_url}/v1/billing/subscriptions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }

        payload = {
            'plan_id': plan_id,
            'subscriber': {
                'email_address': user_email,
            },
            'application_context': {
                'brand_name': 'Trade Scan Pro',
                'locale': 'en-US',
                'shipping_preference': 'NO_SHIPPING',
                'user_action': 'SUBSCRIBE_NOW',
                'return_url': getattr(settings, 'PAYPAL_RETURN_URL', f"{settings.FRONTEND_URL}/subscription/success"),
                'cancel_url': getattr(settings, 'PAYPAL_CANCEL_URL', f"{settings.FRONTEND_URL}/subscription/cancel"),
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create PayPal subscription: {e}")
            return None

    def get_subscription(self, subscription_id):
        """
        Get subscription details from PayPal

        Args:
            subscription_id (str): PayPal subscription ID

        Returns:
            dict: Subscription details
        """
        token = self.get_access_token()
        if not token:
            return None

        url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get PayPal subscription: {e}")
            return None

    def cancel_subscription(self, subscription_id, reason="User requested cancellation"):
        """
        Cancel a PayPal subscription

        Args:
            subscription_id (str): PayPal subscription ID
            reason (str): Cancellation reason

        Returns:
            bool: True if successful, False otherwise
        """
        token = self.get_access_token()
        if not token:
            return False

        url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/cancel"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        payload = {'reason': reason}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to cancel PayPal subscription: {e}")
            return False

    def verify_webhook_signature(self, headers, body, webhook_id):
        """
        Verify PayPal webhook signature

        Args:
            headers (dict): Request headers
            body (str): Request body
            webhook_id (str): PayPal webhook ID

        Returns:
            bool: True if signature is valid
        """
        token = self.get_access_token()
        if not token:
            return False

        url = f"{self.base_url}/v1/notifications/verify-webhook-signature"
        headers_req = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }

        payload = {
            'auth_algo': headers.get('PAYPAL-AUTH-ALGO'),
            'cert_url': headers.get('PAYPAL-CERT-URL'),
            'transmission_id': headers.get('PAYPAL-TRANSMISSION-ID'),
            'transmission_sig': headers.get('PAYPAL-TRANSMISSION-SIG'),
            'transmission_time': headers.get('PAYPAL-TRANSMISSION-TIME'),
            'webhook_id': webhook_id,
            'webhook_event': body,
        }

        try:
            response = requests.post(url, headers=headers_req, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get('verification_status') == 'SUCCESS'
        except Exception as e:
            logger.error(f"Failed to verify PayPal webhook: {e}")
            return False


# Plan name mapping: internal -> display
PLAN_DISPLAY_NAMES = {
    'basic': 'Basic',
    'pro': 'Pro',
    # Legacy support
    'bronze': 'Basic',
    'silver': 'Pro',
}
