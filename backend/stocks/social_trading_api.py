"""
Social Trading API Endpoints (Phase 8 - MVP2 v3.4)
Handles user profiles, following, copy trading, and strategy sharing.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import SocialUserProfile, SocialFollow, CopyTradingRelationship, StrategyShare
from .services.social_trading_service import (
    SocialProfileService, SocialFollowService,
    CopyTradingService, StrategyShareService, ReferralService
)
from .serializers import (
    UserProfileSerializer, SocialFollowSerializer,
    CopyTradingRelationshipSerializer, StrategyShareSerializer
)


# ============================================================================
# User Profile Endpoints
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_profile(request):
    """Get or create the authenticated user's profile."""
    result = SocialProfileService.get_or_create_profile(request.user)

    serializer = UserProfileSerializer(result['profile'])

    return Response({
        'success': True,
        'profile': serializer.data,
        'created': result['created']
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_my_profile(request):
    """Update the authenticated user's profile."""
    result = SocialProfileService.update_profile(request.user, request.data)

    if not result['success']:
        return Response(result, status=400)

    serializer = UserProfileSerializer(result['profile'])

    return Response({
        'success': True,
        'profile': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_profiles(request):
    """Get public/discoverable profiles."""
    visibility = request.GET.get('visibility', 'public')
    order_by = request.GET.get('order_by', '-followers_count')
    limit = int(request.GET.get('limit', 50))

    result = SocialProfileService.get_public_profiles(
        visibility=visibility,
        order_by=order_by,
        limit=limit
    )

    serializer = UserProfileSerializer(result['profiles'], many=True)

    return Response({
        'success': True,
        'profiles': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def search_profiles(request):
    """Search for profiles by name."""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 20))

    if not query:
        return Response({
            'success': False,
            'message': 'Search query required'
        }, status=400)

    result = SocialProfileService.search_profiles(query, limit)

    serializer = UserProfileSerializer(result['profiles'], many=True)

    return Response({
        'success': True,
        'profiles': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile_by_id(request, user_id):
    """Get a specific user's profile by user ID."""
    try:
        profile = UserProfile.objects.get(user_id=user_id)

        # Check visibility
        if profile.visibility == 'private' and (not request.user.is_authenticated or request.user.id != user_id):
            return Response({
                'success': False,
                'message': 'Profile is private'
            }, status=403)

        serializer = UserProfileSerializer(profile)

        return Response({
            'success': True,
            'profile': serializer.data
        })
    except UserProfile.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Profile not found'
        }, status=404)


# ============================================================================
# Follow Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    """Follow another user."""
    result = SocialFollowService.follow_user(request.user, user_id)

    if not result['success']:
        return Response(result, status=400)

    serializer = SocialFollowSerializer(result['follow'])

    return Response({
        'success': True,
        'follow': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, user_id):
    """Unfollow a user."""
    result = SocialFollowService.unfollow_user(request.user, user_id)

    if not result['success']:
        return Response(result, status=400)

    return Response({
        'success': True,
        'message': 'Unfollowed successfully'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_followers(request):
    """Get users following the authenticated user."""
    limit = int(request.GET.get('limit', 50))

    result = SocialFollowService.get_followers(request.user, limit)

    serializer = SocialFollowSerializer(result['followers'], many=True)

    return Response({
        'success': True,
        'followers': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_following(request):
    """Get users that the authenticated user is following."""
    limit = int(request.GET.get('limit', 50))

    result = SocialFollowService.get_following(request.user, limit)

    serializer = SocialFollowSerializer(result['following'], many=True)

    return Response({
        'success': True,
        'following': serializer.data,
        'count': len(serializer.data)
    })


# ============================================================================
# Copy Trading Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_copy_trading(request):
    """Start copying a strategy."""
    strategy_id = request.data.get('strategy_id')
    allocation_amount = request.data.get('allocation_amount')
    position_size_multiplier = request.data.get('position_size_multiplier', 1.0)
    risk_settings = request.data.get('risk_settings', {})

    if not strategy_id or not allocation_amount:
        return Response({
            'success': False,
            'message': 'strategy_id and allocation_amount required'
        }, status=400)

    result = CopyTradingService.start_copying(
        request.user,
        strategy_id,
        allocation_amount,
        position_size_multiplier,
        risk_settings
    )

    if not result['success']:
        return Response(result, status=400)

    serializer = CopyTradingRelationshipSerializer(result['relationship'])

    return Response({
        'success': True,
        'relationship': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pause_copy_trading(request, relationship_id):
    """Pause copy trading."""
    result = CopyTradingService.pause_copying(request.user, relationship_id)

    if not result['success']:
        return Response(result, status=400)

    serializer = CopyTradingRelationshipSerializer(result['relationship'])

    return Response({
        'success': True,
        'relationship': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resume_copy_trading(request, relationship_id):
    """Resume copy trading."""
    result = CopyTradingService.resume_copying(request.user, relationship_id)

    if not result['success']:
        return Response(result, status=400)

    serializer = CopyTradingRelationshipSerializer(result['relationship'])

    return Response({
        'success': True,
        'relationship': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_copy_trading(request, relationship_id):
    """Stop copy trading permanently."""
    result = CopyTradingService.stop_copying(request.user, relationship_id)

    if not result['success']:
        return Response(result, status=400)

    return Response({
        'success': True,
        'message': 'Copy trading stopped'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_copy_relationships(request):
    """Get all copy relationships for authenticated user."""
    result = CopyTradingService.get_user_copy_relationships(request.user)

    serializer = CopyTradingRelationshipSerializer(result['relationships'], many=True)

    return Response({
        'success': True,
        'relationships': serializer.data,
        'count': len(serializer.data)
    })


# ============================================================================
# Strategy Sharing Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_strategy(request):
    """Create a share link for a strategy."""
    strategy_id = request.data.get('strategy_id')
    share_type = request.data.get('share_type', 'unlisted')
    settings = request.data.get('settings', {})

    if not strategy_id:
        return Response({
            'success': False,
            'message': 'strategy_id required'
        }, status=400)

    result = StrategyShareService.share_strategy(
        strategy_id,
        request.user,
        share_type,
        settings
    )

    if not result['success']:
        return Response(result, status=400)

    serializer = StrategyShareSerializer(result['share'])

    return Response({
        'success': True,
        'share': serializer.data,
        'share_url': result['share_url']
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_shared_strategy(request, share_token):
    """Get a strategy by share token."""
    result = StrategyShareService.get_shared_strategy(share_token)

    if not result['success']:
        return Response(result, status=404)

    serializer = StrategyShareSerializer(result['share'])

    return Response({
        'success': True,
        'share': serializer.data,
        'strategy': {
            'id': result['strategy'].id,
            'name': result['strategy'].name,
            'description': result['strategy'].description,
            'annual_return': str(result['strategy'].annual_return) if result['strategy'].annual_return else None,
            'sharpe_ratio': str(result['strategy'].sharpe_ratio) if result['strategy'].sharpe_ratio else None,
            'win_rate': str(result['strategy'].win_rate) if result['strategy'].win_rate else None,
        }
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def revoke_share(request, share_id):
    """Revoke/delete a share link."""
    result = StrategyShareService.revoke_share(share_id, request.user)

    if not result['success']:
        return Response(result, status=400)

    return Response({
        'success': True,
        'message': 'Share link revoked'
    })


# ============================================================================
# Referral Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_referral_code(request):
    """Apply a referral code (usually done during signup)."""
    referral_code = request.data.get('referral_code', '').strip()

    if not referral_code:
        return Response({
            'success': False,
            'message': 'Referral code required'
        }, status=400)

    result = ReferralService.apply_referral_code(request.user, referral_code)

    if not result['success']:
        return Response(result, status=400)

    return Response({
        'success': True,
        'message': 'Referral code applied',
        'referrer_email': result['referrer'].email
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_referral_stats(request):
    """Get referral statistics for authenticated user."""
    result = ReferralService.get_referral_stats(request.user)

    return Response({
        'success': True,
        'stats': result['stats']
    })
