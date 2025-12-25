"""
Retention & Habits Service
Handles trading journals, performance reviews, custom indicators, exports, and alerts.
"""

from django.db import transaction
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta, date
import csv
import io

from stocks.models import (
    TradingJournal, PerformanceReview, UserCustomIndicator,
    TradeExport, AlertTemplate, TriggeredAlert,
    PaperTrade, TradingStrategy
)


class TradingJournalService:
    """Service for managing trading journals."""

    @staticmethod
    def create_entry(user, entry_data):
        """
        Create a new journal entry.

        Args:
            user: User object
            entry_data: dict with title, notes, emotion_before, emotion_after, etc.

        Returns:
            dict: {'success': bool, 'entry': TradingJournal}
        """
        entry = TradingJournal.objects.create(
            user=user,
            trade_id=entry_data.get('trade_id'),
            title=entry_data.get('title', ''),
            notes=entry_data.get('notes', ''),
            emotion_before=entry_data.get('emotion_before', ''),
            emotion_after=entry_data.get('emotion_after', ''),
            followed_plan=entry_data.get('followed_plan'),
            mistakes_made=entry_data.get('mistakes_made', ''),
            lessons_learned=entry_data.get('lessons_learned', ''),
            tags=entry_data.get('tags', []),
            chart_screenshot_url=entry_data.get('chart_screenshot_url', '')
        )

        return {
            'success': True,
            'entry': entry
        }

    @staticmethod
    def update_entry(user, entry_id, entry_data):
        """
        Update an existing journal entry.

        Returns:
            dict: {'success': bool, 'entry': TradingJournal}
        """
        try:
            entry = TradingJournal.objects.get(id=entry_id, user=user)
        except TradingJournal.DoesNotExist:
            return {'success': False, 'message': 'Journal entry not found'}

        # Update fields
        allowed_fields = [
            'title', 'notes', 'emotion_before', 'emotion_after',
            'followed_plan', 'mistakes_made', 'lessons_learned',
            'tags', 'chart_screenshot_url'
        ]

        for field in allowed_fields:
            if field in entry_data:
                setattr(entry, field, entry_data[field])

        entry.save()

        return {
            'success': True,
            'entry': entry
        }

    @staticmethod
    def get_user_entries(user, filters=None, limit=50):
        """
        Get user's journal entries with optional filters.

        Args:
            filters: dict with emotion, followed_plan, tags, date_from, date_to

        Returns:
            dict: {'success': bool, 'entries': QuerySet}
        """
        entries = TradingJournal.objects.filter(user=user)

        if filters:
            if 'emotion' in filters:
                entries = entries.filter(
                    Q(emotion_before=filters['emotion']) |
                    Q(emotion_after=filters['emotion'])
                )

            if 'followed_plan' in filters:
                entries = entries.filter(followed_plan=filters['followed_plan'])

            if 'tags' in filters:
                entries = entries.filter(tags__contains=[filters['tags']])

            if 'date_from' in filters:
                entries = entries.filter(created_at__gte=filters['date_from'])

            if 'date_to' in filters:
                entries = entries.filter(created_at__lte=filters['date_to'])

        entries = entries.order_by('-created_at')[:limit]

        return {
            'success': True,
            'entries': entries
        }

    @staticmethod
    def get_emotion_stats(user):
        """
        Get emotional statistics from journal entries.

        Returns:
            dict: {'success': bool, 'stats': dict}
        """
        entries = TradingJournal.objects.filter(user=user)

        emotion_counts = {}
        for entry in entries:
            if entry.emotion_before:
                emotion_counts[entry.emotion_before] = emotion_counts.get(entry.emotion_before, 0) + 1
            if entry.emotion_after:
                emotion_counts[entry.emotion_after] = emotion_counts.get(entry.emotion_after, 0) + 1

        # Calculate plan adherence rate
        total_with_plan_data = entries.filter(followed_plan__isnull=False).count()
        followed_plan_count = entries.filter(followed_plan=True).count()
        adherence_rate = (followed_plan_count / total_with_plan_data * 100) if total_with_plan_data > 0 else 0

        return {
            'success': True,
            'stats': {
                'emotion_distribution': emotion_counts,
                'total_entries': entries.count(),
                'plan_adherence_rate': round(adherence_rate, 2)
            }
        }


class PerformanceReviewService:
    """Service for generating and managing performance reviews."""

    @staticmethod
    def generate_review(user, review_period='monthly', period_start=None, period_end=None):
        """
        Generate a performance review for a user.

        Args:
            user: User object
            review_period: 'weekly', 'monthly', 'quarterly', 'yearly'
            period_start: date object (optional, auto-calculated if not provided)
            period_end: date object (optional, auto-calculated if not provided)

        Returns:
            dict: {'success': bool, 'review': PerformanceReview}
        """
        # Auto-calculate period dates if not provided
        if not period_start or not period_end:
            period_end = date.today()
            if review_period == 'weekly':
                period_start = period_end - timedelta(days=7)
            elif review_period == 'monthly':
                period_start = period_end - timedelta(days=30)
            elif review_period == 'quarterly':
                period_start = period_end - timedelta(days=90)
            elif review_period == 'yearly':
                period_start = period_end - timedelta(days=365)

        # Check if review already exists
        existing = PerformanceReview.objects.filter(
            user=user,
            review_period=review_period,
            period_start=period_start,
            period_end=period_end
        ).first()

        if existing:
            return {
                'success': False,
                'message': 'Review already exists for this period',
                'review': existing
            }

        # Get trades in period
        trades = PaperTrade.objects.filter(
            user=user,
            created_at__gte=period_start,
            created_at__lte=period_end,
            is_closed=True
        )

        # Calculate metrics
        total_trades = trades.count()
        winning_trades = trades.filter(profit_loss__gt=0).count()
        losing_trades = trades.filter(profit_loss__lt=0).count()

        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        total_profit_loss = trades.aggregate(Sum('profit_loss'))['profit_loss__sum'] or 0
        avg_win = trades.filter(profit_loss__gt=0).aggregate(Avg('profit_loss'))['profit_loss__avg']
        avg_loss = trades.filter(profit_loss__lt=0).aggregate(Avg('profit_loss'))['profit_loss__avg']

        # Calculate profit factor (total wins / total losses)
        total_wins = trades.filter(profit_loss__gt=0).aggregate(Sum('profit_loss'))['profit_loss__sum'] or 0
        total_losses = abs(trades.filter(profit_loss__lt=0).aggregate(Sum('profit_loss'))['profit_loss__sum'] or 0)
        profit_factor = (total_wins / total_losses) if total_losses > 0 else 0

        # Get emotional insights from journal
        journal_entries = TradingJournal.objects.filter(
            user=user,
            created_at__gte=period_start,
            created_at__lte=period_end
        )

        emotion_counts = {}
        for entry in journal_entries:
            if entry.emotion_before:
                emotion_counts[entry.emotion_before] = emotion_counts.get(entry.emotion_before, 0) + 1

        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None

        # Calculate plan adherence
        total_with_plan = journal_entries.filter(followed_plan__isnull=False).count()
        followed_plan_count = journal_entries.filter(followed_plan=True).count()
        plan_adherence_rate = (followed_plan_count / total_with_plan * 100) if total_with_plan > 0 else None

        # Generate AI summary (placeholder - would use LLM in production)
        summary = PerformanceReviewService._generate_summary(
            total_trades, win_rate, total_profit_loss, most_common_emotion
        )
        recommendations = PerformanceReviewService._generate_recommendations(
            win_rate, plan_adherence_rate, most_common_emotion
        )

        # Create review
        review = PerformanceReview.objects.create(
            user=user,
            review_period=review_period,
            period_start=period_start,
            period_end=period_end,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_profit_loss=total_profit_loss,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            most_common_emotion=most_common_emotion or '',
            plan_adherence_rate=plan_adherence_rate,
            summary=summary,
            recommendations=recommendations,
            is_generated=True
        )

        return {
            'success': True,
            'review': review
        }

    @staticmethod
    def get_user_reviews(user, limit=12):
        """
        Get user's performance reviews.

        Returns:
            dict: {'success': bool, 'reviews': QuerySet}
        """
        reviews = PerformanceReview.objects.filter(user=user).order_by('-period_end')[:limit]

        return {
            'success': True,
            'reviews': reviews
        }

    @staticmethod
    def mark_review_viewed(user, review_id):
        """
        Mark a review as viewed.

        Returns:
            dict: {'success': bool, 'review': PerformanceReview}
        """
        try:
            review = PerformanceReview.objects.get(id=review_id, user=user)
            review.is_viewed = True
            review.viewed_at = timezone.now()
            review.save()

            return {
                'success': True,
                'review': review
            }
        except PerformanceReview.DoesNotExist:
            return {'success': False, 'message': 'Review not found'}

    @staticmethod
    def _generate_summary(total_trades, win_rate, total_pnl, emotion):
        """Generate AI summary (placeholder)."""
        if total_trades == 0:
            return "No trades executed during this period."

        pnl_desc = "profitable" if total_pnl > 0 else "losing"
        emotion_desc = f"Most common emotion: {emotion}." if emotion else ""

        return f"Executed {total_trades} trades with a {win_rate:.1f}% win rate. Overall {pnl_desc} period with ${total_pnl:.2f} P/L. {emotion_desc}"

    @staticmethod
    def _generate_recommendations(win_rate, adherence_rate, emotion):
        """Generate AI recommendations (placeholder)."""
        recs = []

        if win_rate < 50:
            recs.append("Focus on improving trade selection criteria.")

        if adherence_rate and adherence_rate < 70:
            recs.append("Work on following your trading plan more consistently.")

        if emotion in ['anxious', 'fearful', 'impulsive']:
            recs.append("Consider implementing stricter risk management rules to reduce emotional trading.")

        return " ".join(recs) if recs else "Keep up the good work!"


class UserCustomIndicatorService:
    """Service for managing custom indicators."""

    @staticmethod
    def create_indicator(user, indicator_data):
        """
        Create a custom indicator.

        Returns:
            dict: {'success': bool, 'indicator': UserCustomIndicator}
        """
        indicator = UserCustomIndicator.objects.create(
            user=user,
            name=indicator_data.get('name'),
            description=indicator_data.get('description', ''),
            indicator_type=indicator_data.get('indicator_type'),
            formula=indicator_data.get('formula'),
            parameters=indicator_data.get('parameters', {}),
            visibility=indicator_data.get('visibility', 'private')
        )

        return {
            'success': True,
            'indicator': indicator
        }

    @staticmethod
    def get_user_indicators(user):
        """
        Get user's custom indicators.

        Returns:
            dict: {'success': bool, 'indicators': QuerySet}
        """
        indicators = UserCustomIndicator.objects.filter(user=user)

        return {
            'success': True,
            'indicators': indicators
        }

    @staticmethod
    def get_public_indicators(limit=50):
        """
        Get public custom indicators.

        Returns:
            dict: {'success': bool, 'indicators': QuerySet}
        """
        indicators = UserCustomIndicator.objects.filter(
            visibility='public'
        ).order_by('-clone_count')[:limit]

        return {
            'success': True,
            'indicators': indicators
        }


class TradeExportService:
    """Service for exporting trade data."""

    @staticmethod
    def request_export(user, export_data):
        """
        Request a trade data export.

        Args:
            export_data: dict with export_format, date_from, date_to, filters

        Returns:
            dict: {'success': bool, 'export': TradeExport}
        """
        export = TradeExport.objects.create(
            user=user,
            export_format=export_data.get('export_format', 'csv'),
            date_from=export_data.get('date_from'),
            date_to=export_data.get('date_to'),
            include_paper_trades=export_data.get('include_paper_trades', True),
            include_live_trades=export_data.get('include_live_trades', False),
            strategy_filter_id=export_data.get('strategy_filter_id')
        )

        # Generate export asynchronously (would use Celery in production)
        # For now, generate synchronously
        result = TradeExportService._generate_export(export)

        if result['success']:
            export.is_generated = True
            export.generated_at = timezone.now()
            export.file_url = result['file_url']
            export.file_size_bytes = result['file_size']
            export.save()

        return {
            'success': True,
            'export': export
        }

    @staticmethod
    def get_user_exports(user):
        """
        Get user's export history.

        Returns:
            dict: {'success': bool, 'exports': QuerySet}
        """
        exports = TradeExport.objects.filter(user=user).order_by('-requested_at')

        return {
            'success': True,
            'exports': exports
        }

    @staticmethod
    def _generate_export(export):
        """
        Generate the export file (placeholder).

        In production, this would:
        1. Query trades based on filters
        2. Format data according to export_format
        3. Upload to S3
        4. Return download URL
        """
        # Get trades
        trades = PaperTrade.objects.filter(
            user=export.user,
            created_at__gte=export.date_from,
            created_at__lte=export.date_to
        )

        if export.strategy_filter:
            trades = trades.filter(strategy=export.strategy_filter)

        # Generate CSV (placeholder)
        if export.export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Date', 'Ticker', 'Action', 'Quantity', 'Price', 'P/L'])

            for trade in trades:
                writer.writerow([
                    trade.created_at.strftime('%Y-%m-%d'),
                    trade.ticker,
                    trade.action,
                    trade.quantity,
                    trade.price,
                    trade.profit_loss or 0
                ])

            # In production, upload to S3
            file_url = f"/exports/{export.id}.csv"
            file_size = len(output.getvalue().encode('utf-8'))

            return {
                'success': True,
                'file_url': file_url,
                'file_size': file_size
            }

        return {'success': False, 'message': 'Export format not implemented'}


class AlertService:
    """Service for managing custom alerts."""

    @staticmethod
    def create_alert(user, alert_data):
        """
        Create a custom alert template.

        Args:
            alert_data: dict with name, description, conditions, notification settings

        Returns:
            dict: {'success': bool, 'alert': AlertTemplate}
        """
        alert = AlertTemplate.objects.create(
            user=user,
            name=alert_data.get('name'),
            description=alert_data.get('description', ''),
            conditions=alert_data.get('conditions', []),
            notify_sms=alert_data.get('notify_sms', False),
            notify_email=alert_data.get('notify_email', False),
            notify_push=alert_data.get('notify_push', True),
            is_active=alert_data.get('is_active', True)
        )

        return {
            'success': True,
            'alert': alert
        }

    @staticmethod
    def update_alert(user, alert_id, alert_data):
        """
        Update an alert template.

        Returns:
            dict: {'success': bool, 'alert': AlertTemplate}
        """
        try:
            alert = AlertTemplate.objects.get(id=alert_id, user=user)
        except AlertTemplate.DoesNotExist:
            return {'success': False, 'message': 'Alert not found'}

        # Update fields
        allowed_fields = [
            'name', 'description', 'conditions',
            'notify_sms', 'notify_email', 'notify_push', 'is_active'
        ]

        for field in allowed_fields:
            if field in alert_data:
                setattr(alert, field, alert_data[field])

        alert.save()

        return {
            'success': True,
            'alert': alert
        }

    @staticmethod
    def get_user_alerts(user):
        """
        Get user's alert templates.

        Returns:
            dict: {'success': bool, 'alerts': QuerySet}
        """
        alerts = AlertTemplate.objects.filter(user=user)

        return {
            'success': True,
            'alerts': alerts
        }

    @staticmethod
    def trigger_alert(alert_id, ticker, triggered_conditions, market_data):
        """
        Record an alert trigger.

        Returns:
            dict: {'success': bool, 'trigger': TriggeredAlert}
        """
        try:
            alert = AlertTemplate.objects.get(id=alert_id, is_active=True)
        except AlertTemplate.DoesNotExist:
            return {'success': False, 'message': 'Alert not found or inactive'}

        trigger = TriggeredAlert.objects.create(
            alert_template=alert,
            ticker=ticker,
            triggered_conditions=triggered_conditions,
            market_data=market_data,
            sms_sent=False,  # Would send notifications here
            email_sent=False,
            push_sent=True
        )

        # Update alert stats
        alert.times_triggered += 1
        alert.last_triggered_at = timezone.now()
        alert.save()

        return {
            'success': True,
            'trigger': trigger
        }

    @staticmethod
    def get_triggered_alerts(user, is_acknowledged=None, limit=50):
        """
        Get triggered alerts for user's alert templates.

        Returns:
            dict: {'success': bool, 'triggers': QuerySet}
        """
        triggers = TriggeredAlert.objects.filter(
            alert_template__user=user
        ).select_related('alert_template')

        if is_acknowledged is not None:
            triggers = triggers.filter(is_acknowledged=is_acknowledged)

        triggers = triggers.order_by('-triggered_at')[:limit]

        return {
            'success': True,
            'triggers': triggers
        }

    @staticmethod
    def acknowledge_alert(user, trigger_id):
        """
        Acknowledge a triggered alert.

        Returns:
            dict: {'success': bool, 'trigger': TriggeredAlert}
        """
        try:
            trigger = TriggeredAlert.objects.get(
                id=trigger_id,
                alert_template__user=user
            )
        except TriggeredAlert.DoesNotExist:
            return {'success': False, 'message': 'Triggered alert not found'}

        trigger.is_acknowledged = True
        trigger.acknowledged_at = timezone.now()
        trigger.save()

        return {
            'success': True,
            'trigger': trigger
        }
