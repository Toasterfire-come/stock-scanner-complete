"""
Social Trading Service
Handles user profiles, following, copy trading, and strategy sharing.
"""

from django.db import transaction
from django.db.models import Q, Count, Avg
from django.utils import timezone
import secrets
import string

from stocks.models import (
    SocialUserProfile, SocialFollow, CopyTradingRelationship, CopiedTrade,
    StrategyShare, ReferralReward, TradingStrategy, PaperTrade
)


class SocialProfileService:
    """Service for managing user social profiles."""

    @staticmethod
    def get_or_create_profile(user):
        """
        Get or create a user's social profile.

        Returns:
            dict: {'success': bool, 'profile': SocialUserProfile, 'created': bool}
        """
        profile, created = SocialUserProfile.objects.get_or_create(
            user=user,
            defaults={
                'display_name': user.email.split('@')[0],  # Default to username part
                'referral_code': SocialProfileService._generate_referral_code()
            }
        )

        return {
            'success': True,
            'profile': profile,
            'created': created
        }

    @staticmethod
    def update_profile(user, profile_data):
        """
        Update user's profile settings.

        Args:
            user: User object
            profile_data: dict with fields to update

        Returns:
            dict: {'success': bool, 'profile': SocialUserProfile}
        """
        profile = user.social_profile

        # Update allowed fields
        allowed_fields = [
            'display_name', 'bio', 'avatar_url', 'visibility',
            'allow_copy_trading', 'allow_messages', 'show_stats'
        ]

        for field in allowed_fields:
            if field in profile_data:
                setattr(profile, field, profile_data[field])

        profile.save()

        return {
            'success': True,
            'profile': profile
        }

    @staticmethod
    def get_public_profiles(visibility='public', order_by='-followers_count', limit=50):
        """
        Get discoverable public profiles.

        Returns:
            dict: {'success': bool, 'profiles': QuerySet}
        """
        profiles = SocialUserProfile.objects.filter(visibility=visibility)

        if order_by:
            profiles = profiles.order_by(order_by)

        profiles = profiles[:limit]

        return {
            'success': True,
            'profiles': profiles
        }

    @staticmethod
    def search_profiles(query, limit=20):
        """
        Search for profiles by display name.

        Returns:
            dict: {'success': bool, 'profiles': QuerySet}
        """
        profiles = SocialUserProfile.objects.filter(
            Q(display_name__icontains=query) | Q(bio__icontains=query),
            visibility='public'
        ).order_by('-followers_count')[:limit]

        return {
            'success': True,
            'profiles': profiles
        }

    @staticmethod
    def verify_profile(user_id, admin_user):
        """
        Verify a user's profile (admin only).

        Returns:
            dict: {'success': bool, 'profile': SocialUserProfile}
        """
        if not admin_user.is_staff:
            return {'success': False, 'message': 'Admin access required'}

        try:
            profile = SocialUserProfile.objects.get(user_id=user_id)
            profile.is_verified = True
            profile.verification_date = timezone.now()
            profile.save()

            return {
                'success': True,
                'profile': profile
            }
        except SocialUserProfile.DoesNotExist:
            return {'success': False, 'message': 'Profile not found'}

    @staticmethod
    def _generate_referral_code(length=8):
        """Generate a unique referral code."""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(chars) for _ in range(length))
            if not SocialUserProfile.objects.filter(referral_code=code).exists():
                return code


class SocialFollowService:
    """Service for managing follow relationships."""

    @staticmethod
    def follow_user(follower, following_user_id):
        """
        Follow another user.

        Returns:
            dict: {'success': bool, 'follow': SocialFollow}
        """
        # Can't follow yourself
        if follower.id == following_user_id:
            return {'success': False, 'message': 'Cannot follow yourself'}

        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            following_user = User.objects.get(id=following_user_id)
        except User.DoesNotExist:
            return {'success': False, 'message': 'User not found'}

        # Check if already following
        existing = SocialFollow.objects.filter(
            follower=follower,
            following=following_user
        ).first()

        if existing:
            return {
                'success': False,
                'message': 'Already following this user',
                'follow': existing
            }

        with transaction.atomic():
            # Create follow relationship
            follow = SocialFollow.objects.create(
                follower=follower,
                following=following_user
            )

            # Update counts
            follower_profile = follower.social_profile
            follower_profile.following_count += 1
            follower_profile.save()

            following_profile = following_user.social_profile
            following_profile.followers_count += 1
            following_profile.save()

        return {
            'success': True,
            'follow': follow
        }

    @staticmethod
    def unfollow_user(follower, following_user_id):
        """
        Unfollow a user.

        Returns:
            dict: {'success': bool}
        """
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            following_user = User.objects.get(id=following_user_id)
        except User.DoesNotExist:
            return {'success': False, 'message': 'User not found'}

        try:
            follow = SocialFollow.objects.get(
                follower=follower,
                following=following_user
            )
        except SocialFollow.DoesNotExist:
            return {'success': False, 'message': 'Not following this user'}

        with transaction.atomic():
            # Delete follow relationship
            follow.delete()

            # Update counts
            follower_profile = follower.social_profile
            follower_profile.following_count -= 1
            follower_profile.save()

            following_profile = following_user.social_profile
            following_profile.followers_count -= 1
            following_profile.save()

        return {'success': True}

    @staticmethod
    def get_followers(user, limit=50):
        """
        Get a user's followers.

        Returns:
            dict: {'success': bool, 'followers': QuerySet}
        """
        followers = SocialFollow.objects.filter(
            following=user
        ).select_related('follower__social_profile')[:limit]

        return {
            'success': True,
            'followers': followers
        }

    @staticmethod
    def get_following(user, limit=50):
        """
        Get users that a user is following.

        Returns:
            dict: {'success': bool, 'following': QuerySet}
        """
        following = SocialFollow.objects.filter(
            follower=user
        ).select_related('following__social_profile')[:limit]

        return {
            'success': True,
            'following': following
        }


class CopyTradingService:
    """Service for copy trading functionality."""

    @staticmethod
    def start_copying(copier, strategy_id, allocation_amount, position_size_multiplier=1.0, risk_settings=None):
        """
        Start copying a strategy.

        Args:
            copier: User who wants to copy
            strategy_id: Strategy ID to copy
            allocation_amount: $ allocated
            position_size_multiplier: Size multiplier (0.5 = half size, 2.0 = double)
            risk_settings: dict with max_daily_loss, stop_loss_pct

        Returns:
            dict: {'success': bool, 'relationship': CopyTradingRelationship}
        """
        try:
            strategy = TradingStrategy.objects.get(id=strategy_id)
        except TradingStrategy.DoesNotExist:
            return {'success': False, 'message': 'Strategy not found'}

        # Check if trader allows copy trading
        trader_profile = strategy.user.social_profile
        if not trader_profile.allow_copy_trading:
            return {'success': False, 'message': 'This trader does not allow copy trading'}

        # Can't copy your own strategy
        if copier.id == strategy.user.id:
            return {'success': False, 'message': 'Cannot copy your own strategy'}

        # Check if already copying
        existing = CopyTradingRelationship.objects.filter(
            copier=copier,
            strategy=strategy
        ).first()

        if existing and existing.status == 'active':
            return {
                'success': False,
                'message': 'Already copying this strategy',
                'relationship': existing
            }

        # Create copy relationship
        risk_settings = risk_settings or {}

        with transaction.atomic():
            relationship = CopyTradingRelationship.objects.create(
                copier=copier,
                trader=strategy.user,
                strategy=strategy,
                status='active',
                allocation_amount=allocation_amount,
                position_size_multiplier=position_size_multiplier,
                max_daily_loss=risk_settings.get('max_daily_loss'),
                stop_loss_pct=risk_settings.get('stop_loss_pct'),
                is_paper_trading=True  # Always start with paper trading
            )

            # Update copier count
            trader_profile.total_copiers += 1
            trader_profile.save()

        return {
            'success': True,
            'relationship': relationship
        }

    @staticmethod
    def pause_copying(copier, relationship_id):
        """
        Pause copy trading.

        Returns:
            dict: {'success': bool}
        """
        try:
            relationship = CopyTradingRelationship.objects.get(
                id=relationship_id,
                copier=copier
            )
        except CopyTradingRelationship.DoesNotExist:
            return {'success': False, 'message': 'Copy relationship not found'}

        relationship.pause()

        return {'success': True, 'relationship': relationship}

    @staticmethod
    def resume_copying(copier, relationship_id):
        """
        Resume copy trading.

        Returns:
            dict: {'success': bool}
        """
        try:
            relationship = CopyTradingRelationship.objects.get(
                id=relationship_id,
                copier=copier
            )
        except CopyTradingRelationship.DoesNotExist:
            return {'success': False, 'message': 'Copy relationship not found'}

        relationship.resume()

        return {'success': True, 'relationship': relationship}

    @staticmethod
    def stop_copying(copier, relationship_id):
        """
        Stop copy trading permanently.

        Returns:
            dict: {'success': bool}
        """
        try:
            relationship = CopyTradingRelationship.objects.get(
                id=relationship_id,
                copier=copier
            )
        except CopyTradingRelationship.DoesNotExist:
            return {'success': False, 'message': 'Copy relationship not found'}

        with transaction.atomic():
            relationship.stop()

            # Update copier count
            trader_profile = relationship.trader.social_profile
            trader_profile.total_copiers -= 1
            trader_profile.save()

        return {'success': True}

    @staticmethod
    def get_user_copy_relationships(user):
        """
        Get all copy relationships for a user (as copier).

        Returns:
            dict: {'success': bool, 'relationships': QuerySet}
        """
        relationships = CopyTradingRelationship.objects.filter(
            copier=user
        ).select_related('strategy', 'trader__social_profile')

        return {
            'success': True,
            'relationships': relationships
        }

    @staticmethod
    def record_copied_trade(copy_relationship_id, original_trade_id, ticker, action, quantity, price):
        """
        Record a trade that was copied.

        Returns:
            dict: {'success': bool, 'copied_trade': CopiedTrade}
        """
        try:
            relationship = CopyTradingRelationship.objects.get(id=copy_relationship_id)
        except CopyTradingRelationship.DoesNotExist:
            return {'success': False, 'message': 'Copy relationship not found'}

        try:
            original_trade = PaperTrade.objects.get(id=original_trade_id) if original_trade_id else None
        except PaperTrade.DoesNotExist:
            original_trade = None

        # Adjust quantity by position size multiplier
        adjusted_quantity = int(quantity * relationship.position_size_multiplier)

        copied_trade = CopiedTrade.objects.create(
            copy_relationship=relationship,
            original_trade=original_trade,
            ticker=ticker,
            action=action,
            quantity=adjusted_quantity,
            price=price
        )

        # Update relationship stats
        relationship.trades_copied += 1
        relationship.save()

        return {
            'success': True,
            'copied_trade': copied_trade
        }


class StrategyShareService:
    """Service for strategy sharing."""

    @staticmethod
    def share_strategy(strategy_id, shared_by, share_type='unlisted', settings=None):
        """
        Create a share link for a strategy.

        Args:
            strategy_id: Strategy to share
            shared_by: User sharing
            share_type: 'public', 'unlisted', 'private_share'
            settings: dict with allow_cloning, allow_copying, expires_at

        Returns:
            dict: {'success': bool, 'share': StrategyShare, 'share_url': str}
        """
        try:
            strategy = TradingStrategy.objects.get(id=strategy_id, user=shared_by)
        except TradingStrategy.DoesNotExist:
            return {'success': False, 'message': 'Strategy not found or not owned by user'}

        settings = settings or {}

        # Generate unique share token
        share_token = secrets.token_urlsafe(24)

        share = StrategyShare.objects.create(
            strategy=strategy,
            shared_by=shared_by,
            share_type=share_type,
            share_token=share_token,
            allow_cloning=settings.get('allow_cloning', True),
            allow_copying=settings.get('allow_copying', False),
            expires_at=settings.get('expires_at')
        )

        # Update profile stats
        profile = shared_by.social_profile
        profile.strategies_shared_count += 1
        profile.save()

        # Construct share URL (would be real domain in production)
        share_url = f"/strategies/shared/{share_token}"

        return {
            'success': True,
            'share': share,
            'share_url': share_url
        }

    @staticmethod
    def get_shared_strategy(share_token):
        """
        Get a strategy by share token.

        Returns:
            dict: {'success': bool, 'share': StrategyShare, 'strategy': TradingStrategy}
        """
        try:
            share = StrategyShare.objects.get(share_token=share_token)
        except StrategyShare.DoesNotExist:
            return {'success': False, 'message': 'Share link not found'}

        if not share.is_active():
            return {'success': False, 'message': 'Share link has expired'}

        # Increment view count
        share.view_count += 1
        share.save()

        return {
            'success': True,
            'share': share,
            'strategy': share.strategy
        }

    @staticmethod
    def revoke_share(share_id, user):
        """
        Revoke/delete a share link.

        Returns:
            dict: {'success': bool}
        """
        try:
            share = StrategyShare.objects.get(id=share_id, shared_by=user)
            share.delete()

            return {'success': True}
        except StrategyShare.DoesNotExist:
            return {'success': False, 'message': 'Share not found'}


class ReferralService:
    """Service for referral tracking and rewards."""

    @staticmethod
    def apply_referral_code(new_user, referral_code):
        """
        Apply a referral code when a new user signs up.

        Returns:
            dict: {'success': bool, 'referrer': User}
        """
        try:
            referrer_profile = SocialUserProfile.objects.get(referral_code=referral_code)
        except SocialUserProfile.DoesNotExist:
            return {'success': False, 'message': 'Invalid referral code'}

        # Link referral relationship
        new_user_profile = new_user.social_profile
        new_user_profile.referred_by = referrer_profile
        new_user_profile.save()

        # Update referrer count
        referrer_profile.referral_count += 1
        referrer_profile.save()

        # Create signup reward
        ReferralReward.objects.create(
            referrer=referrer_profile.user,
            referred_user=new_user,
            reward_type='signup',
            amount=10.00  # $10 signup bonus
        )

        return {
            'success': True,
            'referrer': referrer_profile.user
        }

    @staticmethod
    def record_referral_reward(referrer, referred_user, reward_type, amount):
        """
        Record a referral reward.

        Returns:
            dict: {'success': bool, 'reward': ReferralReward}
        """
        reward = ReferralReward.objects.create(
            referrer=referrer,
            referred_user=referred_user,
            reward_type=reward_type,
            amount=amount
        )

        return {
            'success': True,
            'reward': reward
        }

    @staticmethod
    def get_referral_stats(user):
        """
        Get referral statistics for a user.

        Returns:
            dict: {'success': bool, 'stats': dict}
        """
        profile = user.social_profile

        total_rewards = ReferralReward.objects.filter(referrer=user).aggregate(
            total=Count('id'),
            total_earned=Avg('amount')
        )

        paid_rewards = ReferralReward.objects.filter(
            referrer=user,
            is_paid=True
        ).aggregate(
            paid_count=Count('id'),
            paid_amount=Avg('amount')
        )

        return {
            'success': True,
            'stats': {
                'referral_code': profile.referral_code,
                'total_referrals': profile.referral_count,
                'total_rewards': total_rewards['total'] or 0,
                'total_earned': float(total_rewards['total_earned'] or 0),
                'paid_rewards': paid_rewards['paid_count'] or 0,
                'paid_amount': float(paid_rewards['paid_amount'] or 0)
            }
        }
