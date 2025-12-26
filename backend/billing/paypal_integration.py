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

    def create_subscription(self, plan_id, user_email):
        """
        Create a PayPal subscription

        Args:
            plan_id (str): PayPal plan ID (bronze/silver/gold)
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
                'return_url': f"{settings.FRONTEND_URL}/subscription/success",
                'cancel_url': f"{settings.FRONTEND_URL}/subscription/cancel",
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


# PayPal Plan IDs (set these in your environment variables or settings)
PAYPAL_PLAN_IDS = {
    'bronze': getattr(settings, 'PAYPAL_PLAN_ID_BRONZE', ''),
    'silver': getattr(settings, 'PAYPAL_PLAN_ID_SILVER', ''),
    'gold': getattr(settings, 'PAYPAL_PLAN_ID_GOLD', ''),
}
