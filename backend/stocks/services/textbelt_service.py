"""
TextBelt SMS Service
Handles SMS delivery via self-hosted TextBelt instance.
Supports multi-attempt delivery and rate limiting.
"""

import requests
import time
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TextBeltService:
    """Service for sending SMS via TextBelt"""

    @staticmethod
    def send_sms(phone_number, message, user=None):
        """
        Send SMS via TextBelt with multi-attempt retry logic.

        Args:
            phone_number: Phone number in E.164 format (e.g., +1234567890)
            message: SMS message content (max 160 chars recommended)
            user: User instance for quota tracking (optional)

        Returns:
            dict: {
                'success': bool,
                'textbelt_id': str or None,
                'quota': int or None,
                'error': str or None
            }
        """
        from stocks.models import TextBeltConfig, SMSAlertQuota

        # Get TextBelt configuration
        config = TextBeltConfig.get_config()

        if not config.is_enabled:
            return {
                'success': False,
                'textbelt_id': None,
                'quota': None,
                'error': 'TextBelt is currently disabled'
            }

        # Check user quota if user provided
        if user:
            quota, created = SMSAlertQuota.objects.get_or_create(user=user)
            if not quota.can_send_sms():
                return {
                    'success': False,
                    'textbelt_id': None,
                    'quota': quota.monthly_limit - quota.current_usage,
                    'error': f'SMS quota exceeded. Limit: {quota.monthly_limit}/month'
                }

        # Prepare request
        url = config.api_url
        payload = {
            'phone': phone_number,
            'message': message[:160],  # Limit to 160 chars
        }

        # Add API key if configured (for paid plans)
        if config.api_key:
            payload['key'] = config.api_key

        # Multi-attempt delivery
        last_error = None
        for attempt in range(config.max_retries):
            try:
                logger.info(f"TextBelt attempt {attempt + 1}/{config.max_retries} to {phone_number}")

                response = requests.post(
                    url,
                    data=payload,
                    timeout=10
                )

                result = response.json()

                if result.get('success'):
                    # Update config stats
                    config.total_sent += 1
                    config.last_sent_at = timezone.now()
                    config.save()

                    # Update user quota
                    if user:
                        quota.increment_usage()

                    logger.info(f"SMS sent successfully to {phone_number}, ID: {result.get('textId')}")

                    return {
                        'success': True,
                        'textbelt_id': result.get('textId'),
                        'quota': result.get('quotaRemaining'),
                        'error': None
                    }
                else:
                    last_error = result.get('error', 'Unknown TextBelt error')
                    logger.warning(f"TextBelt delivery failed: {last_error}")

                    # Don't retry certain errors
                    if 'quota' in last_error.lower() or 'invalid' in last_error.lower():
                        break

            except requests.exceptions.RequestException as e:
                last_error = f"Network error: {str(e)}"
                logger.error(f"TextBelt request failed: {last_error}")

            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"TextBelt unexpected error: {last_error}")

            # Wait before retry (except on last attempt)
            if attempt < config.max_retries - 1:
                time.sleep(config.retry_delay_seconds)

        # All attempts failed
        config.total_failed += 1
        config.save()

        return {
            'success': False,
            'textbelt_id': None,
            'quota': None,
            'error': last_error or 'All delivery attempts failed'
        }

    @staticmethod
    def send_alert_sms(alert_rule, stock, trigger_data):
        """
        Send SMS for a triggered alert with formatted message.

        Args:
            alert_rule: SMSAlertRule instance
            stock: Stock instance that triggered the alert
            trigger_data: dict with trigger details (price, volume, conditions, etc.)

        Returns:
            dict: Result from send_sms()
        """
        # Format message
        message = TextBeltService.format_alert_message(
            alert_rule=alert_rule,
            stock=stock,
            trigger_data=trigger_data
        )

        # Send SMS
        result = TextBeltService.send_sms(
            phone_number=alert_rule.phone_number,
            message=message,
            user=alert_rule.user
        )

        # Log to history
        from stocks.models import SMSAlertHistory

        history = SMSAlertHistory.objects.create(
            alert_rule=alert_rule,
            stock=stock,
            message=message,
            phone_number=alert_rule.phone_number,
            trigger_price=trigger_data.get('price'),
            trigger_volume=trigger_data.get('volume'),
            condition_values=trigger_data.get('conditions'),
            status='sent' if result['success'] else 'failed',
            textbelt_id=result.get('textbelt_id', ''),
            textbelt_quota=result.get('quota'),
            delivery_attempts=1,
            error_message=result.get('error', ''),
            sent_at=timezone.now() if result['success'] else None
        )

        # Update alert rule
        if result['success']:
            alert_rule.last_triggered_at = timezone.now()
            alert_rule.trigger_count += 1

            # Deactivate if one-time alert
            if alert_rule.is_one_time:
                alert_rule.is_active = False

            alert_rule.save()

        # Send webhook if configured
        if alert_rule.webhook_enabled and alert_rule.webhook_url:
            TextBeltService.send_webhook(
                url=alert_rule.webhook_url,
                alert_rule=alert_rule,
                stock=stock,
                trigger_data=trigger_data,
                history=history
            )

        return result

    @staticmethod
    def format_alert_message(alert_rule, stock, trigger_data):
        """
        Format SMS message for alert.
        Keeps message under 160 chars for standard SMS.

        Args:
            alert_rule: SMSAlertRule instance
            stock: Stock instance
            trigger_data: Trigger details

        Returns:
            str: Formatted message
        """
        ticker = stock.ticker
        price = trigger_data.get('price')
        change_pct = trigger_data.get('change_percent')

        # Basic format
        if alert_rule.is_multi_condition:
            # Multi-condition alert
            conditions_met = len(trigger_data.get('conditions', []))
            message = f"ALERT: {ticker} ${price:.2f}"
            if change_pct:
                message += f" ({change_pct:+.2f}%)"
            message += f" - {conditions_met} conditions met"
        else:
            # Single condition alert
            condition = alert_rule.conditions.first()
            if condition:
                condition_desc = condition.get_condition_type_display()
                message = f"ALERT: {ticker} {condition_desc} ${price:.2f}"
                if change_pct:
                    message += f" ({change_pct:+.2f}%)"
            else:
                message = f"ALERT: {ticker} ${price:.2f}"

        # Add alert name if there's space
        if len(message) < 120:
            message += f" | {alert_rule.name[:30]}"

        return message[:160]

    @staticmethod
    def send_webhook(url, alert_rule, stock, trigger_data, history):
        """
        Send webhook notification for alert.

        Args:
            url: Webhook URL
            alert_rule: SMSAlertRule instance
            stock: Stock instance
            trigger_data: Trigger details
            history: SMSAlertHistory instance

        Returns:
            bool: Success status
        """
        try:
            payload = {
                'alert_id': alert_rule.id,
                'alert_name': alert_rule.name,
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'price': float(trigger_data.get('price', 0)),
                'volume': trigger_data.get('volume'),
                'change_percent': float(trigger_data.get('change_percent', 0)) if trigger_data.get('change_percent') else None,
                'conditions': trigger_data.get('conditions', []),
                'triggered_at': timezone.now().isoformat(),
                'sms_sent': history.status == 'sent',
            }

            response = requests.post(
                url,
                json=payload,
                timeout=5
            )

            history.webhook_sent = True
            history.webhook_response = f"Status: {response.status_code}"
            history.save()

            logger.info(f"Webhook sent to {url} for alert {alert_rule.id}")
            return True

        except Exception as e:
            error_msg = str(e)
            history.webhook_sent = False
            history.webhook_response = f"Error: {error_msg}"
            history.save()

            logger.error(f"Webhook failed for alert {alert_rule.id}: {error_msg}")
            return False

    @staticmethod
    def retry_failed_sms(history_id):
        """
        Retry a failed SMS delivery.

        Args:
            history_id: SMSAlertHistory ID

        Returns:
            dict: Result from send_sms()
        """
        from stocks.models import SMSAlertHistory

        try:
            history = SMSAlertHistory.objects.get(id=history_id)
        except SMSAlertHistory.DoesNotExist:
            return {
                'success': False,
                'error': 'History record not found'
            }

        if not history.should_retry():
            return {
                'success': False,
                'error': f'Cannot retry: status={history.status}, attempts={history.delivery_attempts}/{history.max_attempts}'
            }

        # Retry delivery
        result = TextBeltService.send_sms(
            phone_number=history.phone_number,
            message=history.message,
            user=history.alert_rule.user
        )

        # Update history
        history.delivery_attempts += 1
        history.last_attempt_at = timezone.now()

        if result['success']:
            history.status = 'sent'
            history.sent_at = timezone.now()
            history.textbelt_id = result.get('textbelt_id', '')
            history.textbelt_quota = result.get('quota')
        else:
            history.status = 'retry' if history.should_retry() else 'failed'
            history.error_message = result.get('error', '')

        history.save()

        return result

    @staticmethod
    def get_quota_status(user):
        """
        Get SMS quota status for user.

        Args:
            user: User instance

        Returns:
            dict: Quota information
        """
        from stocks.models import SMSAlertQuota

        quota, created = SMSAlertQuota.objects.get_or_create(user=user)

        # Check if monthly reset needed
        now = timezone.now()
        if (now - quota.last_reset_at).days >= 30:
            quota.current_usage = 0
            quota.last_reset_at = now
            quota.save()

        return {
            'monthly_limit': quota.monthly_limit,
            'current_usage': quota.current_usage,
            'remaining': quota.monthly_limit - quota.current_usage,
            'total_sent': quota.total_sent,
            'is_blocked': quota.is_blocked,
            'block_reason': quota.block_reason,
            'last_reset': quota.last_reset_at.isoformat(),
        }

    @staticmethod
    def update_user_quota_limit(user, new_limit):
        """
        Update user's monthly SMS quota limit (for tier upgrades).

        Args:
            user: User instance
            new_limit: New monthly limit

        Returns:
            SMSAlertQuota: Updated quota instance
        """
        from stocks.models import SMSAlertQuota

        quota, created = SMSAlertQuota.objects.get_or_create(user=user)
        quota.monthly_limit = new_limit
        quota.save()

        logger.info(f"Updated SMS quota for {user.username}: {new_limit}/month")

        return quota

    @staticmethod
    def test_textbelt_connection():
        """
        Test TextBelt server connection.

        Returns:
            dict: Connection test result
        """
        from stocks.models import TextBeltConfig

        config = TextBeltConfig.get_config()

        try:
            # Send test request
            response = requests.get(
                config.api_url.replace('/text', '/status'),
                timeout=5
            )

            return {
                'success': True,
                'status_code': response.status_code,
                'message': 'TextBelt server is reachable',
                'config': {
                    'url': config.api_url,
                    'is_self_hosted': config.is_self_hosted,
                    'total_sent': config.total_sent,
                    'total_failed': config.total_failed,
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'TextBelt server unreachable: {str(e)}',
                'config': {
                    'url': config.api_url,
                    'is_self_hosted': config.is_self_hosted,
                }
            }
