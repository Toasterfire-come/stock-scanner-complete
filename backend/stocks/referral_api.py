from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
import json
import logging
import secrets
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings

from .models import ReferralAccount, ReferralInvite, ReferralRedemption

logger = logging.getLogger(__name__)


def _gen_code(length: int = 8) -> str:
    return secrets.token_hex(4)[:length]


def _client_user_id(request) -> str:
    # For non-auth flows, allow a client-provided id to link invites
    uid = request.GET.get('user_id') or request.GET.get('uid')
    if not uid and request.method in ['POST', 'PUT', 'PATCH']:
        try:
            data = json.loads(request.body or '{}')
            uid = data.get('inviter_id') or data.get('user_id') or data.get('uid')
        except Exception:
            uid = None
    return str(uid or '')


async def _get_or_create_ref_account(inviter_uid: str, user=None) -> ReferralAccount:
    try:
        account = ReferralAccount.objects.filter(Q(inviter_uid=inviter_uid) | Q(user=user)).first()
        if account:
            return account
        code = _gen_code(8)
        # Ensure uniqueness
        while ReferralAccount.objects.filter(referral_code=code).exists():
            code = _gen_code(8)
        account = ReferralAccount(inviter_uid=inviter_uid, user=user, referral_code=code)
        account.save()
        return account
    except Exception as e:
        logger.error(f"Referral account error: {e}")
        raise


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_referral_link_api(request):
    try:
        inviter_uid = _client_user_id(request)
        if not inviter_uid and not request.user.is_authenticated:
            return JsonResponse({'error': 'user_id required'}, status=400)
        user = request.user if request.user.is_authenticated else None
        account = ReferralAccount.objects.filter(Q(inviter_uid=inviter_uid) | Q(user=user)).first()
        if not account:
            account = ReferralAccount.objects.create(inviter_uid=inviter_uid or (str(getattr(user, 'id', '')) or _gen_code(6)), user=user, referral_code=_gen_code(8))
        base_site = (request.META.get('HTTP_X_APP_BASE') or 'https://retailtradescanner.com').rstrip('/')
        link = f"{base_site}/?ref={account.referral_code}"
        return JsonResponse({'referral_code': account.referral_code, 'referral_link': link})
    except Exception as e:
        logger.error(f"Referral link error: {e}")
        return JsonResponse({'error': 'Failed to get referral link'}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_referral_invite_api(request):
    try:
        data = json.loads(request.body or '{}')
        inviter_uid = str(data.get('inviter_id') or _client_user_id(request) or '').strip()
        invitee_email = str(data.get('invitee_email') or '').strip().lower()
        if not inviter_uid or not invitee_email:
            return JsonResponse({'error': 'inviter_id and invitee_email required'}, status=400)
        user = request.user if request.user.is_authenticated else None
        # Prevent self-referrals if authenticated
        try:
            if user and (user.email or '').lower() == invitee_email:
                return JsonResponse({'error': 'Cannot invite your own email'}, status=400)
        except Exception:
            pass
        # Prevent disposable emails (basic check, extendable via env)
        disposable_domains = set(filter(None, [d.strip().lower() for d in (os.environ.get('DISPOSABLE_EMAIL_DOMAINS') or '').split(',')])) or {
            'mailinator.com','guerrillamail.com','10minutemail.com','tempmail.com','trashmail.com'
        }
        try:
            domain = invitee_email.split('@',1)[1]
            if domain in disposable_domains:
                return JsonResponse({'error': 'Disposable emails are not allowed'}, status=400)
        except Exception:
            pass
        # Rate-limit invites per inviter
        rl_limit = int(os.environ.get('REFERRAL_INVITES_PER_HOUR', '20'))
        rl_key = f"ref_invites:{inviter_uid}:{timezone.now().strftime('%Y%m%d%H')}"
        count = cache.get(rl_key, 0)
        if count >= rl_limit:
            return JsonResponse({'error': 'Invite rate limit exceeded'}, status=429)
        account = ReferralAccount.objects.filter(Q(inviter_uid=inviter_uid) | Q(user=user)).first()
        if not account:
            account = ReferralAccount.objects.create(inviter_uid=inviter_uid, user=user, referral_code=_gen_code(8))
        existing = ReferralInvite.objects.filter(invitee_email=invitee_email).first()
        if existing:
            return JsonResponse({'status': 'exists'})
        inv = ReferralInvite.objects.create(
            inviter=user if user and user.is_authenticated else None,
            inviter_uid=inviter_uid,
            invitee_email=invitee_email,
            referral_code=account.referral_code,
            status='invited'
        )
        try:
            cache.set(rl_key, count + 1, timeout=3600)
        except Exception:
            pass
        return JsonResponse({'status': 'ok', 'id': inv.id})
    except Exception as e:
        logger.error(f"Referral invite error: {e}")
        return JsonResponse({'error': 'Failed to create invite'}, status=500)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def referral_summary_api(request):
    try:
        inviter_uid = _client_user_id(request)
        if not inviter_uid and not request.user.is_authenticated:
            return JsonResponse({'error': 'user_id required'}, status=400)
        user = request.user if request.user.is_authenticated else None
        account = ReferralAccount.objects.filter(Q(inviter_uid=inviter_uid) | Q(user=user)).first()
        if not account:
            account = ReferralAccount.objects.create(inviter_uid=inviter_uid or (str(getattr(user, 'id', '')) or _gen_code(6)), user=user, referral_code=_gen_code(8))
        total_invited = ReferralInvite.objects.filter(inviter_uid=account.inviter_uid).count()
        total_paid = ReferralInvite.objects.filter(inviter_uid=account.inviter_uid, status='paid').count()
        rewards_months_earned = total_paid // 3
        redeemed = int(account.free_months_redeemed or 0)
        pending_rewards_months = max(0, rewards_months_earned - redeemed)
        return JsonResponse({
            'inviter_id': account.inviter_uid,
            'total_invited': total_invited,
            'total_paid': total_paid,
            'rewards_months_earned': rewards_months_earned,
            'rewards_months_granted': int(account.rewards_months_granted or 0),
            'free_months_redeemed': redeemed,
            'pending_rewards_months': pending_rewards_months,
        })
    except Exception as e:
        logger.error(f"Referral summary error: {e}")
        return JsonResponse({'error': 'Failed to get summary'}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def referral_mark_paid_webhook_api(request):
    """
    Generic webhook to mark an invite as paid. Accepts either referral_code or invitee_email.
    Body: { referral_code?: str, invitee_email?: str }
    """
    try:
        data = json.loads(request.body or '{}')
        referral_code = (data.get('referral_code') or '').strip()
        invitee_email = (data.get('invitee_email') or '').strip().lower()
        if not referral_code and not invitee_email:
            return JsonResponse({'error': 'referral_code or invitee_email required'}, status=400)
        query = {}
        if referral_code:
            query['referral_code'] = referral_code
        if invitee_email:
            query['invitee_email'] = invitee_email
        invite = ReferralInvite.objects.filter(**query).first()
        if not invite:
            return JsonResponse({'success': True})
        invite.status = 'paid'
        invite.paid_at = timezone.now()
        invite.save(update_fields=['status', 'paid_at', 'updated_at'])

        # Grant months in ReferralAccount (3 paid = 1 month, unlimited accrual)
        account = ReferralAccount.objects.filter(inviter_uid=invite.inviter_uid).first()
        if account:
            total_paid = ReferralInvite.objects.filter(inviter_uid=account.inviter_uid, status='paid').count()
            earned_months = total_paid // 3
            if earned_months > int(account.rewards_months_granted or 0):
                account.rewards_months_granted = earned_months
                account.save(update_fields=['rewards_months_granted', 'updated_at'])
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Referral mark paid error: {e}")
        return JsonResponse({'error': 'Failed to process webhook'}, status=500)

