"""
Achievement System for TradeScanPro
Gamification badges to increase engagement and encourage sharing
"""
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone


# Achievement Definitions
ACHIEVEMENTS = {
    # Beginner Achievements
    'first_steps': {
        'id': 'first_steps',
        'name': 'First Steps',
        'description': 'Created your first backtest',
        'icon': '🎯',
        'category': 'beginner',
        'points': 10,
        'rarity': 'common',
        'check_fn': 'check_first_backtest'
    },
    'in_the_green': {
        'id': 'in_the_green',
        'name': 'In the Green',
        'description': 'Got your first profitable backtest (>0% return)',
        'icon': '💚',
        'category': 'beginner',
        'points': 25,
        'rarity': 'common',
        'check_fn': 'check_first_profitable'
    },
    'shareholder': {
        'id': 'shareholder',
        'name': 'Shareholder',
        'description': 'Shared a backtest result on social media',
        'icon': '📤',
        'category': 'social',
        'points': 15,
        'rarity': 'common',
        'check_fn': 'check_first_share'
    },

    # Intermediate Achievements
    'grade_a_student': {
        'id': 'grade_a_student',
        'name': 'Grade A Student',
        'description': 'Achieved an A or A+ quality grade',
        'icon': '🌟',
        'category': 'quality',
        'points': 50,
        'rarity': 'uncommon',
        'check_fn': 'check_grade_a'
    },
    'prolific_trader': {
        'id': 'prolific_trader',
        'name': 'Prolific Trader',
        'description': 'Created 10 backtests',
        'icon': '📊',
        'category': 'engagement',
        'points': 50,
        'rarity': 'uncommon',
        'check_fn': 'check_ten_backtests'
    },
    'going_viral': {
        'id': 'going_viral',
        'name': 'Going Viral',
        'description': 'Had a shared backtest viewed 100+ times',
        'icon': '🚀',
        'category': 'social',
        'points': 100,
        'rarity': 'rare',
        'check_fn': 'check_viral_share'
    },

    # Advanced Achievements
    'market_beater': {
        'id': 'market_beater',
        'name': 'Market Beater',
        'description': 'Beat the S&P 500 with 50%+ annual return',
        'icon': '📈',
        'category': 'performance',
        'points': 100,
        'rarity': 'rare',
        'check_fn': 'check_beat_market'
    },
    'sharpe_shooter': {
        'id': 'sharpe_shooter',
        'name': 'Sharpe Shooter',
        'description': 'Achieved Sharpe Ratio above 2.0',
        'icon': '🎯',
        'category': 'performance',
        'points': 75,
        'rarity': 'uncommon',
        'check_fn': 'check_high_sharpe'
    },

    # Expert Achievements
    'consistency_king': {
        'id': 'consistency_king',
        'name': 'Consistency King',
        'description': 'Achieved 5 consecutive profitable backtests',
        'icon': '👑',
        'category': 'consistency',
        'points': 150,
        'rarity': 'epic',
        'check_fn': 'check_five_consecutive_wins'
    },
    'legendary_trader': {
        'id': 'legendary_trader',
        'name': 'Legendary Trader',
        'description': 'Achieved A+ grade with 100%+ return and Sharpe >2.5',
        'icon': '🏆',
        'category': 'legendary',
        'points': 250,
        'rarity': 'legendary',
        'check_fn': 'check_legendary_status'
    },
}


class Achievement(models.Model):
    """Track which achievements users have unlocked"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_id = models.CharField(max_length=50, help_text="Achievement type ID")
    unlocked_at = models.DateTimeField(auto_now_add=True)
    backtest_id = models.IntegerField(null=True, blank=True, help_text="Backtest that triggered this achievement")
    shared_on_social = models.BooleanField(default=False, help_text="Whether user shared this achievement")

    class Meta:
        unique_together = ('user', 'achievement_id')
        ordering = ['-unlocked_at']

    def __str__(self):
        achievement_data = ACHIEVEMENTS.get(self.achievement_id, {})
        return f"{self.user.username} - {achievement_data.get('name', self.achievement_id)}"

    def get_achievement_data(self):
        """Return full achievement details"""
        data = ACHIEVEMENTS.get(self.achievement_id, {})
        return {
            **data,
            'unlocked_at': self.unlocked_at.isoformat(),
            'backtest_id': self.backtest_id,
            'shared_on_social': self.shared_on_social
        }


class AchievementChecker:
    """Service class to check and unlock achievements"""

    @staticmethod
    def check_all_achievements(user, backtest=None):
        """Check all achievements for a user and unlock any new ones"""
        from .models import BacktestRun  # Import here to avoid circular dependency

        newly_unlocked = []

        for achievement_id, achievement_data in ACHIEVEMENTS.items():
            # Skip if already unlocked
            if Achievement.objects.filter(user=user, achievement_id=achievement_id).exists():
                continue

            # Check if achievement should be unlocked
            check_method = getattr(AchievementChecker, achievement_data['check_fn'], None)
            if check_method and check_method(user, backtest):
                achievement = Achievement.objects.create(
                    user=user,
                    achievement_id=achievement_id,
                    backtest_id=backtest.id if backtest else None
                )
                newly_unlocked.append(achievement.get_achievement_data())

        return newly_unlocked

    @staticmethod
    def check_first_backtest(user, backtest):
        """Check if user created their first backtest"""
        from .models import BacktestRun
        return BacktestRun.objects.filter(user=user, status='completed').count() >= 1

    @staticmethod
    def check_first_profitable(user, backtest):
        """Check if user has first profitable backtest"""
        from .models import BacktestRun
        return BacktestRun.objects.filter(
            user=user,
            status='completed',
            total_return__gt=0
        ).exists()

    @staticmethod
    def check_first_share(user, backtest):
        """Check if user shared a backtest (tracked via analytics)"""
        # This will be checked when share event is tracked
        # For now, return False - will be unlocked manually when user shares
        return False

    @staticmethod
    def check_grade_a(user, backtest):
        """Check if user achieved A or A+ grade"""
        if not backtest:
            return False
        return backtest.composite_score >= 80 if backtest.composite_score else False

    @staticmethod
    def check_ten_backtests(user, backtest):
        """Check if user created 10 backtests"""
        from .models import BacktestRun
        return BacktestRun.objects.filter(user=user, status='completed').count() >= 10

    @staticmethod
    def check_viral_share(user, backtest):
        """Check if user had a backtest with 100+ views"""
        # This requires view tracking on public pages (future feature)
        # For now, return False
        return False

    @staticmethod
    def check_beat_market(user, backtest):
        """Check if user beat S&P 500 with 50%+ return"""
        if not backtest:
            return False
        return backtest.annualized_return >= 50 if backtest.annualized_return else False

    @staticmethod
    def check_high_sharpe(user, backtest):
        """Check if user achieved Sharpe > 2.0"""
        if not backtest:
            return False
        return backtest.sharpe_ratio >= 2.0 if backtest.sharpe_ratio else False

    @staticmethod
    def check_five_consecutive_wins(user, backtest):
        """Check if user has 5 consecutive profitable backtests"""
        from .models import BacktestRun
        recent_tests = BacktestRun.objects.filter(
            user=user,
            status='completed'
        ).order_by('-completed_at')[:5]

        if recent_tests.count() < 5:
            return False

        return all(bt.total_return > 0 for bt in recent_tests if bt.total_return is not None)

    @staticmethod
    def check_legendary_status(user, backtest):
        """Check if user achieved legendary status"""
        if not backtest:
            return False

        has_grade = backtest.composite_score >= 90 if backtest.composite_score else False
        has_return = backtest.total_return >= 100 if backtest.total_return else False
        has_sharpe = backtest.sharpe_ratio >= 2.5 if backtest.sharpe_ratio else False

        return has_grade and has_return and has_sharpe


def get_user_achievements(user):
    """Get all achievements for a user with full data"""
    unlocked = Achievement.objects.filter(user=user)
    unlocked_ids = set(a.achievement_id for a in unlocked)

    result = {
        'unlocked': [a.get_achievement_data() for a in unlocked],
        'locked': [],
        'stats': {
            'total_points': sum(ACHIEVEMENTS[a.achievement_id]['points'] for a in unlocked if a.achievement_id in ACHIEVEMENTS),
            'total_unlocked': len(unlocked),
            'total_available': len(ACHIEVEMENTS),
            'completion_percentage': (len(unlocked) / len(ACHIEVEMENTS) * 100) if ACHIEVEMENTS else 0
        }
    }

    # Add locked achievements
    for achievement_id, data in ACHIEVEMENTS.items():
        if achievement_id not in unlocked_ids:
            result['locked'].append({
                **data,
                'unlocked': False
            })

    return result


def mark_achievement_shared(user, achievement_id):
    """Mark an achievement as shared on social media"""
    try:
        achievement = Achievement.objects.get(user=user, achievement_id=achievement_id)
        achievement.shared_on_social = True
        achievement.save()
        return True
    except Achievement.DoesNotExist:
        return False
