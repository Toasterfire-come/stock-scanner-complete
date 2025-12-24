"""
Alert Evaluation Service
Evaluates alert conditions against real-time market data.
Supports single and multi-condition alerts.
"""

from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class AlertEvaluationService:
    """Service for evaluating alert conditions"""

    @staticmethod
    def evaluate_alert_rule(alert_rule):
        """
        Evaluate an alert rule against current market data.

        Args:
            alert_rule: SMSAlertRule instance

        Returns:
            tuple: (triggered: bool, stocks: list, trigger_data: dict)
        """
        # Determine which stocks to check
        if alert_rule.stock:
            stocks = [alert_rule.stock]
        elif alert_rule.watchlist:
            from stocks.models import WatchlistItem
            watchlist_items = WatchlistItem.objects.filter(
                watchlist=alert_rule.watchlist
            ).select_related('stock')
            stocks = [item.stock for item in watchlist_items]
        else:
            logger.warning(f"Alert {alert_rule.id} has no stock or watchlist")
            return False, [], {}

        # Check each stock
        triggered_stocks = []
        for stock in stocks:
            is_triggered, trigger_data = AlertEvaluationService.evaluate_stock_conditions(
                alert_rule, stock
            )
            if is_triggered:
                triggered_stocks.append((stock, trigger_data))

        # Update last checked time
        alert_rule.last_checked_at = timezone.now()
        alert_rule.save(update_fields=['last_checked_at'])

        return len(triggered_stocks) > 0, triggered_stocks, {}

    @staticmethod
    def evaluate_stock_conditions(alert_rule, stock):
        """
        Evaluate all conditions for a stock.

        Args:
            alert_rule: SMSAlertRule instance
            stock: Stock instance

        Returns:
            tuple: (triggered: bool, trigger_data: dict)
        """
        conditions = alert_rule.conditions.all()

        if not conditions.exists():
            logger.warning(f"Alert {alert_rule.id} has no conditions")
            return False, {}

        # Evaluate each condition
        results = []
        condition_values = []

        for condition in conditions:
            is_met, value = AlertEvaluationService.evaluate_single_condition(
                condition, stock
            )
            results.append(is_met)
            condition_values.append({
                'type': condition.condition_type,
                'target': float(condition.target_value),
                'actual': value,
                'met': is_met
            })

        # Combine results based on operator
        if alert_rule.is_multi_condition:
            if alert_rule.condition_operator == 'and':
                triggered = all(results)
            else:  # 'or'
                triggered = any(results)
        else:
            # Single condition
            triggered = results[0] if results else False

        # Prepare trigger data
        trigger_data = {
            'price': float(stock.current_price) if stock.current_price else None,
            'volume': stock.volume,
            'change_percent': float(stock.change_percent) if stock.change_percent else None,
            'conditions': condition_values,
            'operator': alert_rule.condition_operator if alert_rule.is_multi_condition else None
        }

        return triggered, trigger_data

    @staticmethod
    def evaluate_single_condition(condition, stock):
        """
        Evaluate a single alert condition.

        Args:
            condition: SMSAlertCondition instance
            stock: Stock instance

        Returns:
            tuple: (is_met: bool, current_value: float or None)
        """
        condition_type = condition.condition_type
        target = condition.target_value
        current_price = stock.current_price or Decimal('0')
        current_volume = stock.volume or 0

        # Price-based conditions
        if condition_type == 'price_above':
            return current_price > target, float(current_price)

        elif condition_type == 'price_below':
            return current_price < target, float(current_price)

        elif condition_type == 'price_crosses_above':
            # Check if price crossed above target
            previous = condition.previous_value or Decimal('0')
            crossed = previous <= target < current_price
            # Update previous value
            condition.previous_value = current_price
            condition.save(update_fields=['previous_value'])
            return crossed, float(current_price)

        elif condition_type == 'price_crosses_below':
            # Check if price crossed below target
            previous = condition.previous_value or Decimal('999999')
            crossed = previous >= target > current_price
            # Update previous value
            condition.previous_value = current_price
            condition.save(update_fields=['previous_value'])
            return crossed, float(current_price)

        elif condition_type == 'price_change_percent':
            # Price change % vs target
            change_pct = stock.change_percent or Decimal('0')
            if target > 0:
                # Positive change (gain)
                return change_pct >= target, float(change_pct)
            else:
                # Negative change (loss)
                return change_pct <= target, float(change_pct)

        # Volume-based conditions
        elif condition_type == 'volume_above':
            return current_volume > target, float(current_volume)

        elif condition_type == 'volume_surge':
            # Volume surge: current volume > target% of avg volume
            avg_volume = stock.avg_volume_3mon or 1
            surge_ratio = (current_volume / avg_volume) * 100 if avg_volume > 0 else 0
            return surge_ratio >= float(target), surge_ratio

        # Gap conditions
        elif condition_type == 'gap_up':
            # Gap up: opening price higher than previous close by target%
            # Simplified: use current price vs day low
            days_low = stock.days_low or current_price
            if days_low > 0:
                gap_pct = ((current_price - days_low) / days_low) * 100
                return gap_pct >= float(target), float(gap_pct)
            return False, 0.0

        elif condition_type == 'gap_down':
            # Gap down: opening price lower than previous close by target%
            days_high = stock.days_high or current_price
            if days_high > 0:
                gap_pct = ((days_high - current_price) / days_high) * 100
                return gap_pct >= float(target), float(gap_pct)
            return False, 0.0

        # Technical indicator conditions (require valuation_json data)
        elif condition_type == 'rsi_above':
            rsi = AlertEvaluationService.get_rsi(stock, condition.indicator_period or 14)
            if rsi is not None:
                return rsi > float(target), rsi
            return False, None

        elif condition_type == 'rsi_below':
            rsi = AlertEvaluationService.get_rsi(stock, condition.indicator_period or 14)
            if rsi is not None:
                return rsi < float(target), rsi
            return False, None

        elif condition_type == 'macd_cross_bullish':
            # MACD line crosses above signal line
            macd, signal = AlertEvaluationService.get_macd(stock)
            if macd is not None and signal is not None:
                # Check previous values for cross
                was_below = (condition.previous_value or 0) <= 0
                is_above = macd > signal
                crossed = was_below and is_above
                # Store MACD - Signal difference
                condition.previous_value = Decimal(str(macd - signal))
                condition.save(update_fields=['previous_value'])
                return crossed, macd
            return False, None

        elif condition_type == 'macd_cross_bearish':
            # MACD line crosses below signal line
            macd, signal = AlertEvaluationService.get_macd(stock)
            if macd is not None and signal is not None:
                # Check previous values for cross
                was_above = (condition.previous_value or 0) >= 0
                is_below = macd < signal
                crossed = was_above and is_below
                # Store MACD - Signal difference
                condition.previous_value = Decimal(str(macd - signal))
                condition.save(update_fields=['previous_value'])
                return crossed, macd
            return False, None

        elif condition_type == 'sma_cross_above':
            # Faster SMA crosses above slower SMA
            period1 = condition.indicator_period or 50
            period2 = condition.comparison_period or 200
            sma_fast = AlertEvaluationService.get_sma(stock, period1)
            sma_slow = AlertEvaluationService.get_sma(stock, period2)
            if sma_fast is not None and sma_slow is not None:
                was_below = (condition.previous_value or 0) <= 0
                is_above = sma_fast > sma_slow
                crossed = was_below and is_above
                # Store difference
                condition.previous_value = Decimal(str(sma_fast - sma_slow))
                condition.save(update_fields=['previous_value'])
                return crossed, sma_fast
            return False, None

        elif condition_type == 'sma_cross_below':
            # Faster SMA crosses below slower SMA
            period1 = condition.indicator_period or 50
            period2 = condition.comparison_period or 200
            sma_fast = AlertEvaluationService.get_sma(stock, period1)
            sma_slow = AlertEvaluationService.get_sma(stock, period2)
            if sma_fast is not None and sma_slow is not None:
                was_above = (condition.previous_value or 0) >= 0
                is_below = sma_fast < sma_slow
                crossed = was_above and is_below
                # Store difference
                condition.previous_value = Decimal(str(sma_fast - sma_slow))
                condition.save(update_fields=['previous_value'])
                return crossed, sma_fast
            return False, None

        logger.warning(f"Unknown condition type: {condition_type}")
        return False, None

    @staticmethod
    def get_rsi(stock, period=14):
        """Get RSI from stock valuation_json"""
        if not stock.valuation_json:
            return None
        return stock.valuation_json.get('technical', {}).get(f'rsi_{period}')

    @staticmethod
    def get_macd(stock):
        """Get MACD and Signal from stock valuation_json"""
        if not stock.valuation_json:
            return None, None
        technical = stock.valuation_json.get('technical', {})
        return technical.get('macd'), technical.get('macd_signal')

    @staticmethod
    def get_sma(stock, period):
        """Get SMA from stock valuation_json"""
        if not stock.valuation_json:
            return None
        return stock.valuation_json.get('technical', {}).get(f'sma_{period}')

    @staticmethod
    def check_all_active_alerts():
        """
        Check all active alerts and trigger SMS for matches.
        Should be called periodically (e.g., every minute).

        Returns:
            dict: Summary of alerts checked and triggered
        """
        from stocks.models import SMSAlertRule
        from stocks.services.textbelt_service import TextBeltService

        active_alerts = SMSAlertRule.objects.filter(is_active=True)

        stats = {
            'total_checked': 0,
            'total_triggered': 0,
            'sms_sent': 0,
            'sms_failed': 0,
            'quota_exceeded': 0
        }

        for alert_rule in active_alerts:
            stats['total_checked'] += 1

            # Check if can trigger today
            if not alert_rule.can_trigger_today():
                logger.info(f"Alert {alert_rule.id} hit daily trigger limit")
                continue

            # Evaluate alert
            triggered, triggered_stocks, _ = AlertEvaluationService.evaluate_alert_rule(alert_rule)

            if triggered:
                stats['total_triggered'] += 1

                # Send SMS for each triggered stock
                for stock, trigger_data in triggered_stocks:
                    result = TextBeltService.send_alert_sms(
                        alert_rule=alert_rule,
                        stock=stock,
                        trigger_data=trigger_data
                    )

                    if result['success']:
                        stats['sms_sent'] += 1
                        logger.info(f"Alert {alert_rule.id} triggered for {stock.ticker}")
                    else:
                        if 'quota' in result.get('error', '').lower():
                            stats['quota_exceeded'] += 1
                        else:
                            stats['sms_failed'] += 1
                        logger.error(f"Failed to send SMS for alert {alert_rule.id}: {result.get('error')}")

        return stats

    @staticmethod
    def get_user_alert_summary(user):
        """
        Get summary of user's alerts.

        Args:
            user: User instance

        Returns:
            dict: Alert summary
        """
        from stocks.models import SMSAlertRule

        alerts = SMSAlertRule.objects.filter(user=user)

        return {
            'total_alerts': alerts.count(),
            'active_alerts': alerts.filter(is_active=True).count(),
            'inactive_alerts': alerts.filter(is_active=False).count(),
            'multi_condition_alerts': alerts.filter(is_multi_condition=True).count(),
            'total_triggers': sum(alert.trigger_count for alert in alerts),
            'alerts': [
                {
                    'id': alert.id,
                    'name': alert.name,
                    'ticker': alert.stock.ticker if alert.stock else None,
                    'watchlist': alert.watchlist.name if alert.watchlist else None,
                    'is_active': alert.is_active,
                    'is_multi_condition': alert.is_multi_condition,
                    'trigger_count': alert.trigger_count,
                    'last_triggered': alert.last_triggered_at.isoformat() if alert.last_triggered_at else None,
                    'conditions_count': alert.conditions.count(),
                }
                for alert in alerts.order_by('-created_at')
            ]
        }
