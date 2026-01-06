"""
Django REST Framework Serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    # Phase 8 - Social & Copy Trading
    SocialUserProfile, SocialFollow, CopyTradingRelationship,
    CopiedTrade, StrategyShare, ReferralReward,
    # Phase 9 - Retention & Habits
    TradingJournal, PerformanceReview, UserCustomIndicator,
    TradeExport, AlertTemplate, TriggeredAlert,
    TradeJournalEntry,
    UserExportJob, UserExportSchedule,
)

User = get_user_model()


# ============================================================================
# Phase 8 - Social & Copy Trading Serializers
# ============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for SocialUserProfile model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = SocialUserProfile
        fields = [
            'id', 'user_email', 'display_name', 'bio', 'avatar_url',
            'visibility', 'followers_count', 'following_count',
            'strategies_shared_count', 'total_copiers', 'is_verified',
            'verification_date', 'showcase_annual_return', 'showcase_sharpe_ratio',
            'showcase_win_rate', 'allow_copy_trading', 'allow_messages',
            'show_stats', 'referral_code', 'referral_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'followers_count', 'following_count',
            'strategies_shared_count', 'total_copiers', 'is_verified',
            'verification_date', 'showcase_annual_return', 'showcase_sharpe_ratio',
            'showcase_win_rate', 'referral_code', 'referral_count',
            'created_at', 'updated_at'
        ]


class SocialFollowSerializer(serializers.ModelSerializer):
    """Serializer for SocialFollow model."""
    follower_email = serializers.EmailField(source='follower.email', read_only=True)
    following_email = serializers.EmailField(source='following.email', read_only=True)
    follower_display_name = serializers.CharField(
        source='follower.social_profile.display_name',
        read_only=True
    )
    following_display_name = serializers.CharField(
        source='following.social_profile.display_name',
        read_only=True
    )

    class Meta:
        model = SocialFollow
        fields = [
            'id', 'follower', 'follower_email', 'follower_display_name',
            'following', 'following_email', 'following_display_name',
            'followed_at', 'notifications_enabled'
        ]
        read_only_fields = ['id', 'followed_at']


class CopyTradingRelationshipSerializer(serializers.ModelSerializer):
    """Serializer for CopyTradingRelationship model."""
    copier_email = serializers.EmailField(source='copier.email', read_only=True)
    trader_email = serializers.EmailField(source='trader.email', read_only=True)
    strategy_name = serializers.CharField(source='strategy.name', read_only=True)

    class Meta:
        model = CopyTradingRelationship
        fields = [
            'id', 'copier', 'copier_email', 'trader', 'trader_email',
            'strategy', 'strategy_name', 'status', 'allocation_amount',
            'position_size_multiplier', 'max_daily_loss', 'stop_loss_pct',
            'is_paper_trading', 'total_profit_loss', 'trades_copied',
            'win_rate', 'started_at', 'paused_at', 'stopped_at'
        ]
        read_only_fields = [
            'id', 'copier_email', 'trader_email', 'strategy_name',
            'total_profit_loss', 'trades_copied', 'win_rate',
            'started_at', 'paused_at', 'stopped_at'
        ]


class CopiedTradeSerializer(serializers.ModelSerializer):
    """Serializer for CopiedTrade model."""
    class Meta:
        model = CopiedTrade
        fields = [
            'id', 'copy_relationship', 'original_trade', 'ticker',
            'action', 'quantity', 'price', 'profit_loss', 'is_closed',
            'executed_at', 'closed_at'
        ]
        read_only_fields = ['id', 'executed_at', 'closed_at']


class StrategyShareSerializer(serializers.ModelSerializer):
    """Serializer for StrategyShare model."""
    strategy_name = serializers.CharField(source='strategy.name', read_only=True)
    shared_by_email = serializers.EmailField(source='shared_by.email', read_only=True)

    class Meta:
        model = StrategyShare
        fields = [
            'id', 'strategy', 'strategy_name', 'shared_by', 'shared_by_email',
            'share_type', 'share_token', 'view_count', 'clone_count',
            'copy_count', 'allow_cloning', 'allow_copying', 'shared_at',
            'expires_at'
        ]
        read_only_fields = [
            'id', 'strategy_name', 'shared_by_email', 'share_token',
            'view_count', 'clone_count', 'copy_count', 'shared_at'
        ]


class ReferralRewardSerializer(serializers.ModelSerializer):
    """Serializer for ReferralReward model."""
    referrer_email = serializers.EmailField(source='referrer.email', read_only=True)
    referred_user_email = serializers.EmailField(source='referred_user.email', read_only=True)

    class Meta:
        model = ReferralReward
        fields = [
            'id', 'referrer', 'referrer_email', 'referred_user',
            'referred_user_email', 'reward_type', 'amount', 'is_paid',
            'paid_at', 'earned_at'
        ]
        read_only_fields = ['id', 'earned_at', 'paid_at']


# ============================================================================
# Phase 9 - Retention & Habits Serializers
# ============================================================================

class TradingJournalSerializer(serializers.ModelSerializer):
    """Serializer for TradingJournal model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TradingJournal
        fields = [
            'id', 'user', 'user_email', 'trade', 'title', 'notes',
            'emotion_before', 'emotion_after', 'followed_plan',
            'mistakes_made', 'lessons_learned', 'tags',
            'chart_screenshot_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_email', 'created_at', 'updated_at']


class TradeJournalEntrySerializer(serializers.ModelSerializer):
    """Serializer for TradeJournalEntry (trade log)."""
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TradeJournalEntry
        fields = [
            'id', 'user', 'user_email', 'date', 'symbol', 'type',
            'entry_price', 'exit_price', 'shares',
            'strategy', 'setup', 'notes', 'emotions', 'lessons',
            'tags', 'status', 'screenshot_url',
            'pnl', 'pnl_percent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_email', 'created_at', 'updated_at']


class UserExportJobSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserExportJob
        fields = [
            "id", "user", "user_email", "name", "type", "format", "status",
            "error", "payload", "content_type", "filename",
            "created_at", "completed_at", "download_count",
        ]
        read_only_fields = ["id", "user", "user_email", "created_at", "completed_at", "download_count", "content_type", "filename"]


class UserExportScheduleSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserExportSchedule
        fields = [
            "id", "user", "user_email",
            "name", "description", "export_type", "format", "frequency", "time", "timezone",
            "enabled", "retention_days", "sms_notifications", "sms_recipients",
            "last_run_at", "next_run_at", "run_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "user_email", "last_run_at", "next_run_at", "run_count", "created_at", "updated_at"]


class PerformanceReviewSerializer(serializers.ModelSerializer):
    """Serializer for PerformanceReview model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = PerformanceReview
        fields = [
            'id', 'user', 'user_email', 'review_period', 'period_start',
            'period_end', 'total_trades', 'winning_trades', 'losing_trades',
            'win_rate', 'total_profit_loss', 'avg_win', 'avg_loss',
            'profit_factor', 'max_drawdown', 'sharpe_ratio',
            'most_common_emotion', 'plan_adherence_rate', 'summary',
            'recommendations', 'is_generated', 'is_viewed', 'viewed_at',
            'generated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'total_trades', 'winning_trades',
            'losing_trades', 'win_rate', 'total_profit_loss', 'avg_win',
            'avg_loss', 'profit_factor', 'max_drawdown', 'sharpe_ratio',
            'most_common_emotion', 'plan_adherence_rate', 'summary',
            'recommendations', 'is_generated', 'viewed_at', 'generated_at'
        ]


class UserCustomIndicatorSerializer(serializers.ModelSerializer):
    """Serializer for UserCustomIndicator model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserCustomIndicator
        fields = [
            'id', 'user', 'user_email', 'name', 'description',
            'indicator_type', 'formula', 'parameters', 'visibility',
            'usage_count', 'clone_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'usage_count', 'clone_count',
            'created_at', 'updated_at'
        ]


class TradeExportSerializer(serializers.ModelSerializer):
    """Serializer for TradeExport model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    strategy_name = serializers.CharField(source='strategy_filter.name', read_only=True)

    class Meta:
        model = TradeExport
        fields = [
            'id', 'user', 'user_email', 'export_format', 'date_from',
            'date_to', 'include_paper_trades', 'include_live_trades',
            'strategy_filter', 'strategy_name', 'file_url', 'file_size_bytes',
            'is_generated', 'error_message', 'requested_at', 'generated_at',
            'expires_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'strategy_name', 'file_url',
            'file_size_bytes', 'is_generated', 'error_message',
            'requested_at', 'generated_at'
        ]


class AlertTemplateSerializer(serializers.ModelSerializer):
    """Serializer for AlertTemplate model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = AlertTemplate
        fields = [
            'id', 'user', 'user_email', 'name', 'description', 'conditions',
            'notify_sms', 'notify_email', 'notify_push', 'is_active',
            'times_triggered', 'last_triggered_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'times_triggered', 'last_triggered_at',
            'created_at', 'updated_at'
        ]


class TriggeredAlertSerializer(serializers.ModelSerializer):
    """Serializer for TriggeredAlert model."""
    alert_name = serializers.CharField(source='alert_template.name', read_only=True)

    class Meta:
        model = TriggeredAlert
        fields = [
            'id', 'alert_template', 'alert_name', 'ticker',
            'triggered_conditions', 'market_data', 'sms_sent',
            'email_sent', 'push_sent', 'is_acknowledged',
            'acknowledged_at', 'triggered_at'
        ]
        read_only_fields = [
            'id', 'alert_name', 'triggered_conditions', 'market_data',
            'sms_sent', 'email_sent', 'push_sent', 'triggered_at'
        ]


# ============================================================================
# Phase 10 & 11 Serializers
# ============================================================================

from .models import (
    UserDashboard, ChartPreset, FeatureFlag, SystemHealthCheck
)

class UserDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDashboard
        fields = ['id', 'name', 'layout', 'is_default', 'visibility', 'created_at', 'updated_at']

class ChartPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartPreset
        fields = ['id', 'name', 'description', 'chart_type', 'timeframe', 'indicators', 'drawing_tools', 'color_scheme', 'is_public', 'clone_count']

class FeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlag
        fields = ['name', 'description', 'is_enabled', 'rollout_strategy', 'rollout_percentage']

class SystemHealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemHealthCheck
        fields = ['check_type', 'status', 'response_time_ms', 'checked_at']
