"""
PayPal webhook signature verification for secure payment processing
"""
import hmac
import hashlib
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def verify_paypal_webhook_signature(request):
    """
    Verify PayPal webhook signature to ensure authenticity.
    
    This prevents attackers from sending fake webhook events to manipulate
    subscriptions, payments, or other critical operations.
    
    Documentation:
    https://developer.paypal.com/docs/api-basics/notifications/webhooks/notification-messages/
    
    Args:
        request: Django request object containing webhook data
        
    Returns:
        Boolean indicating if signature is valid
        
    Example:
        @csrf_exempt
        def paypal_webhook(request):
            if not verify_paypal_webhook_signature(request):
                return JsonResponse({'error': 'Invalid signature'}, status=403)
            # Process webhook...
    """
    try:
        # Get PayPal signature headers
        transmission_id = request.META.get('HTTP_PAYPAL_TRANSMISSION_ID')
        transmission_time = request.META.get('HTTP_PAYPAL_TRANSMISSION_TIME')
        cert_url = request.META.get('HTTP_PAYPAL_CERT_URL')
        transmission_sig = request.META.get('HTTP_PAYPAL_TRANSMISSION_SIG')
        auth_algo = request.META.get('HTTP_PAYPAL_AUTH_ALGO', 'SHA256withRSA')
        
        # Check all required headers are present
        if not all([transmission_id, transmission_time, cert_url, transmission_sig]):
            logger.warning("PayPal webhook missing required headers")
            return False
        
        # Get webhook ID from settings
        webhook_id = settings.PAYPAL_WEBHOOK_ID
        if not webhook_id:
            logger.error("PAYPAL_WEBHOOK_ID not configured in settings")
            return False
        
        # Verify the certificate URL is from PayPal
        if not cert_url.startswith('https://api.paypal.com/') and \
           not cert_url.startswith('https://api.sandbox.paypal.com/'):
            logger.warning(f"Invalid PayPal certificate URL: {cert_url}")
            return False
        
        # Method 1: Use PayPal SDK if available
        try:
            from paypalrestsdk import WebhookEvent
            
            webhook_event = WebhookEvent(json.loads(request.body))
            
            # Verify using PayPal SDK
            if webhook_event.verify(
                transmission_id,
                transmission_time,
                cert_url,
                transmission_sig,
                auth_algo,
                webhook_id
            ):
                logger.info(f"PayPal webhook signature verified: {transmission_id}")
                return True
            else:
                logger.warning(f"PayPal webhook signature verification failed: {transmission_id}")
                return False
                
        except ImportError:
            logger.warning("PayPal SDK not installed, using basic verification")
            
            # Method 2: Basic verification using HMAC
            # Note: This is less secure than full certificate validation
            # Install paypalrestsdk for production use
            
            if not hasattr(settings, 'PAYPAL_SECRET') or not settings.PAYPAL_SECRET:
                logger.error("PAYPAL_SECRET not configured, cannot verify webhook")
                return False
            
            # Construct expected signature payload
            expected_sig_string = f"{transmission_id}|{transmission_time}|{webhook_id}|{hashlib.sha256(request.body).hexdigest()}"
            
            # Create HMAC signature
            expected_sig = hmac.new(
                settings.PAYPAL_SECRET.encode('utf-8'),
                expected_sig_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures (constant time comparison)
            if hmac.compare_digest(expected_sig, transmission_sig):
                logger.info(f"PayPal webhook HMAC verified: {transmission_id}")
                return True
            else:
                logger.warning(f"PayPal webhook HMAC verification failed: {transmission_id}")
                return False
    
    except Exception as e:
        logger.error(f"PayPal webhook verification error: {e}", exc_info=True)
        return False


def verify_stripe_webhook_signature(request):
    """
    Verify Stripe webhook signature (if Stripe is used).
    
    Args:
        request: Django request object
        
    Returns:
        Boolean indicating if signature is valid
    """
    try:
        import stripe
        
        # Get Stripe signature header
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        if not sig_header:
            logger.warning("Stripe webhook missing signature header")
            return False
        
        # Get webhook secret from settings
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        if not webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET not configured")
            return False
        
        # Verify signature
        try:
            event = stripe.Webhook.construct_event(
                request.body,
                sig_header,
                webhook_secret
            )
            logger.info(f"Stripe webhook signature verified: {event['id']}")
            return True
            
        except stripe.error.SignatureVerificationError as e:
            logger.warning(f"Stripe webhook signature verification failed: {e}")
            return False
    
    except ImportError:
        logger.error("Stripe SDK not installed")
        return False
    
    except Exception as e:
        logger.error(f"Stripe webhook verification error: {e}", exc_info=True)
        return False


def log_webhook_event(request, verified: bool, event_type: str = None):
    """
    Log webhook event for auditing and debugging.
    
    Args:
        request: Django request object
        verified: Whether signature was verified
        event_type: Type of webhook event
    """
    from stocks.auth_decorators import get_client_ip
    
    logger.info(
        f"Webhook event | "
        f"Type: {event_type or 'unknown'} | "
        f"Verified: {verified} | "
        f"IP: {get_client_ip(request)} | "
        f"ID: {request.META.get('HTTP_PAYPAL_TRANSMISSION_ID', 'N/A')}"
    )
