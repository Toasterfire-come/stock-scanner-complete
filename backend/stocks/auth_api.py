"""
Authentication and User Management API Views
Provides comprehensive user authentication, profile management, and billing endpoints
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import ParseError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import json
import logging
from datetime import datetime, timedelta
import os
from django.db import transaction, IntegrityError
from django.shortcuts import redirect
from urllib.parse import urlencode
import base64
import requests

from .models import UserProfile, BillingHistory, NotificationSettings, DiscountCode, UserDiscountUsage
from .models import ReferralTrialEvent
from .services.discount_service import DiscountService
from .security_utils import secure_api_endpoint, validate_user_input
from .authentication import BearerSessionAuthentication, CsrfExemptSessionAuthentication

logger = logging.getLogger(__name__)

def _active_ref_codes():
    """Return an uppercase set of allowed referral codes from env/settings.
    If none configured, return an empty set (meaning allow any valid ref).
    Example env: REF_ACTIVE="KAVA!,AEJ12"
    """
    try:
        raw = os.environ.get('REF_ACTIVE') or getattr(settings, 'REF_ACTIVE', '') or ''
    except Exception:
        raw = ''
    codes = {c.strip().upper() for c in raw.split(',') if c and c.strip()}
    return codes

def _login_user_and_response(request, user: User):
    login(request, user)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    # Auto-grant staff/admin for specific email per request
    try:
      if (user.email or '').lower().strip() == 'carter.kiefer2010@outlook.com':
          if not user.is_staff:
              user.is_staff = True
              user.save(update_fields=['is_staff'])
    except Exception:
      pass
    try:
        if not request.session.session_key:
            request.session.save()
    except Exception:
        pass
    resp = JsonResponse({
        'success': True,
        'data': {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_premium': getattr(profile, 'is_premium', False),
            'api_token': request.session.session_key,
        }
    })
    try:
        csrf_token = get_token(request)
        resp.set_cookie(
            key=getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken'),
            value=csrf_token,
            secure=getattr(settings, 'CSRF_COOKIE_SECURE', True),
            samesite=getattr(settings, 'CSRF_COOKIE_SAMESITE', 'None'),
            httponly=False,
        )
    except Exception:
        pass
    return resp

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def google_login_redirect(request):
    """Redirect user to Google OAuth login (server-side flow)."""
    try:
        client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', None) or os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
        redirect_uri = getattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', None) or os.environ.get('GOOGLE_OAUTH_REDIRECT_URI')
        scope = 'openid email profile'
        if not client_id or not redirect_uri:
            return JsonResponse({'success': False, 'error': 'Google OAuth not configured'}, status=400)
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'prompt': 'select_account',
        }
        # Redirect user agent to Google OAuth
        return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")
    except Exception as e:
        logger.error(f"google_login_redirect error: {e}")
        return JsonResponse({'success': False}, status=500)

@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def google_oauth_callback(request):
    """
    Handle Google OAuth authorization code flow.
    Expects JSON { code, state } or query params.
    Exchanges code for id_token at Google and logs the user in by email.
    """
    try:
        data = request.data if hasattr(request, 'data') and request.data else None
        code = (data.get('code') if isinstance(data, dict) else None) or request.GET.get('code')
        if not code:
            return JsonResponse({'success': False, 'error': 'Missing authorization code'}, status=400)

        # Minimal exchange using tokeninfo when possible (One Tap returns id_token directly).
        # For web OAuth code flow, proper exchange requires client_secret; we support a backend-only
        # verification path by asking client to hit /auth/google/onetap when available.
        # Here, accept code as an opaque token if front-end already verified and forwarded id_token.
        # Fallback: treat 'code' as id_token and verify via tokeninfo.
        token_res = requests.get('https://oauth2.googleapis.com/tokeninfo', params={'id_token': code}, timeout=10)
        if token_res.status_code != 200:
            return JsonResponse({'success': False, 'error': 'OAuth exchange failed'}, status=401)
        payload = token_res.json()
        email = (payload.get('email') or '').lower().strip()
        sub = payload.get('sub')
        if not email or not sub:
            return JsonResponse({'success': False, 'error': 'Incomplete Google profile'}, status=400)

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            base_username = email.split('@')[0][:20]
            candidate = base_username
            idx = 1
            while User.objects.filter(username__iexact=candidate).exists():
                candidate = f"{base_username[:18]}{idx:02d}"
                idx += 1
            user = User.objects.create_user(username=candidate, email=email, password=User.objects.make_random_password())

            # VIP AUTO-UPGRADE: Check if this is a VIP email that should get Plus unlimited
            VIP_EMAILS = ['hamzashehata3000@gmail.com', 'carter.kiefer2010@outlook.com']
            if email.lower() in [e.lower() for e in VIP_EMAILS]:
                try:
                    from billing.models import Subscription, PlanTier, BillingCycle
                    from decimal import Decimal
                    from datetime import timedelta

                    Subscription.objects.create(
                        user=user,
                        plan_tier=PlanTier.PLUS,
                        billing_cycle=BillingCycle.ANNUAL,
                        status='active',
                        monthly_price=Decimal('0.00'),
                        current_period_start=timezone.now(),
                        current_period_end=timezone.now() + timedelta(days=3650)
                    )
                    logger.info(f"VIP account created via Google OAuth with Plus unlimited: {email}")
                except Exception as e_vip:
                    logger.error(f"Failed to create VIP subscription for {email}: {str(e_vip)}")
        return _login_user_and_response(request, user)
    except Exception as e:
        logger.error(f"google_oauth_callback error: {e}")
        return JsonResponse({'success': False, 'error': 'Google OAuth failed'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def google_config_api(request):
    """Expose minimal Google config to frontend without hardcoding REACT_APP_GOOGLE_CLIENT_ID."""
    try:
        client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', None) or os.environ.get('GOOGLE_OAUTH_CLIENT_ID') or ''
        redirect_uri = getattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', None) or os.environ.get('GOOGLE_OAUTH_REDIRECT_URI') or ''
        return JsonResponse({'success': True, 'client_id': client_id, 'redirect_uri': redirect_uri})
    except Exception as e:
        logger.error(f"google_config_api error: {e}")
        return JsonResponse({'success': False}, status=500)
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def google_onetap_exchange(request):
    """Exchange Google One Tap credential JWT for user login.
    GET /api/auth/google/onetap?credential=...
    """
    try:
        credential = request.GET.get('credential')
        if not credential:
            return JsonResponse({'success': False, 'error': 'Missing credential'}, status=400)
        # Verify via Google tokeninfo (simple server-side verification). For production, verify signature with google-auth lib.
        r = requests.get('https://oauth2.googleapis.com/tokeninfo', params={'id_token': credential}, timeout=10)
        if r.status_code != 200:
            return JsonResponse({'success': False, 'error': 'Invalid Google credential'}, status=401)
        payload = r.json()
        email = (payload.get('email') or '').lower().strip()
        sub = payload.get('sub')
        if not email or not sub:
            return JsonResponse({'success': False, 'error': 'Incomplete Google profile'}, status=400)
        # Find or create user
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            base_username = email.split('@')[0][:20]
            candidate = base_username
            idx = 1
            while User.objects.filter(username__iexact=candidate).exists():
                candidate = f"{base_username[:18]}{idx:02d}"
                idx += 1
            user = User.objects.create_user(username=candidate, email=email, password=User.objects.make_random_password())

            # VIP AUTO-UPGRADE: Check if this is a VIP email that should get Plus unlimited
            VIP_EMAILS = ['hamzashehata3000@gmail.com', 'carter.kiefer2010@outlook.com']
            if email.lower() in [e.lower() for e in VIP_EMAILS]:
                try:
                    from billing.models import Subscription, PlanTier, BillingCycle
                    from decimal import Decimal
                    from datetime import timedelta

                    Subscription.objects.create(
                        user=user,
                        plan_tier=PlanTier.PLUS,
                        billing_cycle=BillingCycle.ANNUAL,
                        status='active',
                        monthly_price=Decimal('0.00'),
                        current_period_start=timezone.now(),
                        current_period_end=timezone.now() + timedelta(days=3650)
                    )
                    logger.info(f"VIP account created via Google One Tap with Plus unlimited: {email}")
                except Exception as e_vip:
                    logger.error(f"Failed to create VIP subscription for {email}: {str(e_vip)}")
        return _login_user_and_response(request, user)
    except Exception as e:
        logger.error(f"google_onetap_exchange error: {e}")
        return JsonResponse({'success': False, 'error': 'Google login failed'}, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def apple_login_redirect(request):
    """Redirect to Sign in with Apple. Assumes configured service."""
    try:
        redirect_uri = getattr(settings, 'APPLE_REDIRECT_URI', None) or os.environ.get('APPLE_REDIRECT_URI')
        client_id = getattr(settings, 'APPLE_CLIENT_ID', None) or os.environ.get('APPLE_CLIENT_ID')
        if not redirect_uri or not client_id:
            return JsonResponse({'success': False, 'error': 'Apple OAuth not configured'}, status=400)
        params = {
            'response_type': 'code id_token',
            'response_mode': 'form_post',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'name email',
        }
        return Response({'url': f"https://appleid.apple.com/auth/authorize?{urlencode(params)}"})
    except Exception as e:
        logger.error(f"apple_login_redirect error: {e}")
        return JsonResponse({'success': False}, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def apple_callback(request):
    """Handle Apple callback (form_post). Extract email if present, create/login user."""
    try:
        data = request.data or {}
        email = (data.get('email') or '').lower().strip()
        # If email absent (often for returning users), derive from id_token
        if not email:
            id_token = data.get('id_token')
            if id_token and '.' in id_token:
                try:
                    payload_b64 = id_token.split('.')[1] + '=='
                    payload_json = base64.urlsafe_b64decode(payload_b64)
                    email = json.loads(payload_json).get('email', '').lower().strip()
                except Exception:
                    pass
        if not email:
            return JsonResponse({'success': False, 'error': 'No email from Apple'}, status=400)
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            base_username = email.split('@')[0][:20]
            candidate = base_username
            idx = 1
            while User.objects.filter(username__iexact=candidate).exists():
                candidate = f"{base_username[:18]}{idx:02d}"
                idx += 1
            user = User.objects.create_user(username=candidate, email=email, password=User.objects.make_random_password())

            # VIP AUTO-UPGRADE: Check if this is a VIP email that should get Plus unlimited
            VIP_EMAILS = ['hamzashehata3000@gmail.com', 'carter.kiefer2010@outlook.com']
            if email.lower() in [e.lower() for e in VIP_EMAILS]:
                try:
                    from billing.models import Subscription, PlanTier, BillingCycle
                    from decimal import Decimal
                    from datetime import timedelta

                    Subscription.objects.create(
                        user=user,
                        plan_tier=PlanTier.PLUS,
                        billing_cycle=BillingCycle.ANNUAL,
                        status='active',
                        monthly_price=Decimal('0.00'),
                        current_period_start=timezone.now(),
                        current_period_end=timezone.now() + timedelta(days=3650)
                    )
                    logger.info(f"VIP account created via Apple Sign-In with Plus unlimited: {email}")
                except Exception as e_vip:
                    logger.error(f"Failed to create VIP subscription for {email}: {str(e_vip)}")
        return _login_user_and_response(request, user)
    except Exception as e:
        logger.error(f"apple_callback error: {e}")
        return JsonResponse({'success': False, 'error': 'Apple login failed'}, status=500)

# CSRF token endpoint
@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def csrf_token_api(request):
    """
    Return a CSRF token and ensure the CSRF cookie is set.
    GET /api/auth/csrf/
    """
    try:
        token = get_token(request)
        response = JsonResponse({
            'success': True,
            'csrf_token': token,
            'csrf_cookie_name': getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken')
        })
        # Explicitly set cookie to enforce attributes for cross-site requests
        response.set_cookie(
            key=getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken'),
            value=token,
            secure=getattr(settings, 'CSRF_COOKIE_SECURE', True),
            samesite=getattr(settings, 'CSRF_COOKIE_SAMESITE', 'None'),
            httponly=False,
        )
        return response
    except Exception as e:
        logger.error(f"CSRF token error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to obtain CSRF token',
            'error_code': 'CSRF_TOKEN_ERROR'
        }, status=500)

# Registration endpoint
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def register_api(request):
    """
    User registration endpoint
    POST /api/auth/register
    """
    try:
        # Prefer DRF parsed data, fallback to raw JSON
        data = getattr(request, 'data', None)
        if data is None or data == {}:
            data = json.loads(request.body) if request.body else {}

        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = (data.get('password') or '').strip()
        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()

        if not username or not email or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username, email, and password are required',
                'error_code': 'MISSING_FIELDS'
            }, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid email format',
                'error_code': 'INVALID_EMAIL'
            }, status=400)

        # Case-insensitive uniqueness checks to prevent duplicates that differ only by case
        if User.objects.filter(username__iexact=username).exists():
            return JsonResponse({
                'success': False,
                'error': 'Username already taken',
                'error_code': 'USERNAME_TAKEN'
            }, status=409)

        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'An account with this email already exists',
                'error_code': 'EMAIL_TAKEN'
            }, status=409)

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                # Ensure a profile exists
                profile, _ = UserProfile.objects.get_or_create(user=user)

                # VIP AUTO-UPGRADE: Check if this is a VIP email that should get Plus unlimited
                VIP_EMAILS = ['hamzashehata3000@gmail.com', 'carter.kiefer2010@outlook.com']
                if email.lower() in [e.lower() for e in VIP_EMAILS]:
                    try:
                        from billing.models import Subscription, PlanTier, BillingCycle
                        from decimal import Decimal
                        from datetime import timedelta

                        # Create Plus unlimited subscription for VIP account
                        Subscription.objects.create(
                            user=user,
                            plan_tier=PlanTier.PLUS,
                            billing_cycle=BillingCycle.ANNUAL,
                            status='active',
                            monthly_price=Decimal('0.00'),  # Complimentary
                            current_period_start=timezone.now(),
                            current_period_end=timezone.now() + timedelta(days=3650)  # 10 years
                        )
                        logger.info(f"VIP account created with Plus unlimited: {email}")
                    except Exception as e:
                        logger.error(f"Failed to create VIP subscription for {email}: {str(e)}")

                # Optional referral: apply 50% off first month and attach usage record
                # Accept from body, query, cookie, or X-Referral-Code header
                ref = (data.get('ref') or request.GET.get('ref') or request.COOKIES.get('ref') or request.META.get('HTTP_X_REFERRAL_CODE') or '').strip()
                if ref and len(ref) == 5 and ref.isalnum():
                    # If REF_ACTIVE is configured, enforce whitelist
                    allowed = _active_ref_codes()
                    if allowed and ref.upper() not in allowed:
                        # Skip creating referral code if not whitelisted
                        pass
                    else:
                    # Create or fetch a dynamic discount code REF_<ref> at 50% first payment only
                        code_str = f"REF_{ref.upper()}"
                        disc, _ = DiscountCode.objects.get_or_create(
                            code=code_str,
                            defaults={
                                'discount_percentage': 50,
                                'is_active': True,
                                'applies_to_first_payment_only': True,
                            }
                        )
                        # Track that this user is associated with this referral code (for lifetime attribution)
                        try:
                            UserDiscountUsage.objects.get_or_create(user=user, discount_code=disc)
                        except Exception:
                            pass
                        # Log trial event for partner analytics (code may be provided directly e.g., ADAM50)
                        try:
                            # If the client passes full code like ADAM50, allow that; else use parsed discount code
                            full_code = ref.upper() if ref.upper().startswith('ADAM') else disc.code
                            ReferralTrialEvent.objects.create(code=full_code, user=user)
                        except Exception:
                            pass
        except IntegrityError:
            # Handle rare race conditions where another request created the same user concurrently
            return JsonResponse({
                'success': False,
                'error': 'Username or email already exists',
                'error_code': 'USERNAME_OR_EMAIL_TAKEN'
            }, status=409)

        return JsonResponse({
            'success': True,
            'message': 'Registration successful',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_premium': getattr(profile, 'is_premium', False)
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Register error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Registration failed',
            'error_code': 'REGISTER_ERROR'
        }, status=500)

# Authentication endpoints
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login_api(request):
    """
    User login endpoint
    POST /api/auth/login
    """
    try:
        # Prefer DRF's parsed data, fallback to raw JSON body
        try:
            data = getattr(request, 'data', None)
        except ParseError as pe:
            logger.warning(f"Login ParseError: {str(pe)}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON format',
                'error_code': 'INVALID_JSON'
            }, status=400)

        if data is None or data == {}:
            try:
                data = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON format',
                    'error_code': 'INVALID_JSON'
                }, status=400)
        
        # Support common variants: identifier, username, email
        identifier = (data.get('identifier') or data.get('username') or data.get('email') or '').strip()
        password = (data.get('password') or '').strip()
        username = ''

        # Validate presence of credentials first
        if not identifier or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password are required',
                'error_code': 'MISSING_CREDENTIALS'
            }, status=400)

        # Resolve identifier to a username, handling duplicate emails gracefully
        user = None
        if '@' in identifier:
            # Multiple accounts may exist with the same email; try each with the provided password
            candidates = list(User.objects.filter(email__iexact=identifier).order_by('-is_active', '-last_login', '-date_joined'))
            if not candidates:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid username or password',
                    'error_code': 'INVALID_CREDENTIALS'
                }, status=401)
            for candidate in candidates:
                # Quick password check before calling authenticate to avoid side effects
                try:
                    if not candidate.check_password(password):
                        continue
                except Exception:
                    continue
                authed = authenticate(request, username=candidate.username, password=password)
                if authed is not None:
                    user = authed
                    break
        else:
            # Treat as username directly
            user = authenticate(request, username=identifier, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Get or create user profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Ensure the session has a key we can return for BearerSessionAuthentication
                try:
                    if not request.session.session_key:
                        request.session.save()
                except Exception:
                    pass

                response = JsonResponse({
                    'success': True,
                    'data': {
                        'user_id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_premium': profile.is_premium if hasattr(profile, 'is_premium') else False,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                        # Provide a session-based API token so SPA can authenticate via Authorization header
                        'api_token': request.session.session_key,
                    },
                    'message': 'Login successful'
                })

                # Ensure CSRF cookie is set for subsequent authenticated requests
                try:
                    csrf_token = get_token(request)
                    response.set_cookie(
                        key=getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken'),
                        value=csrf_token,
                        secure=getattr(settings, 'CSRF_COOKIE_SECURE', True),
                        samesite=getattr(settings, 'CSRF_COOKIE_SAMESITE', 'None'),
                        httponly=False,
                    )
                except Exception:
                    pass

                return response
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Account is inactive',
                    'error_code': 'ACCOUNT_INACTIVE'
                }, status=403)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid username or password',
                'error_code': 'INVALID_CREDENTIALS'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Login failed',
            'error_code': 'LOGIN_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """
    User logout endpoint
    POST /api/auth/logout
    """
    try:
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Logout failed',
            'error_code': 'LOGOUT_ERROR'
        }, status=500)

# User profile endpoints
@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """
    User profile management
    GET/POST /api/user/profile
    """
    try:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            return JsonResponse({
                'success': True,
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': getattr(profile, 'phone', ''),
                    'company': getattr(profile, 'company', ''),
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'is_premium': getattr(profile, 'is_premium', False)
                }
            })
        
        elif request.method == 'POST':
            data = json.loads(request.body) if request.body else {}
            
            # Update user fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                try:
                    validate_email(data['email'])
                    user.email = data['email']
                except ValidationError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid email format',
                        'error_code': 'INVALID_EMAIL'
                    }, status=400)
            
            # Update profile fields
            if 'phone' in data:
                profile.phone = data['phone']
            if 'company' in data:
                profile.company = data['company']
            
            user.save()
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully',
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': getattr(profile, 'phone', ''),
                    'company': getattr(profile, 'company', '')
                }
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Profile API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Profile operation failed',
            'error_code': 'PROFILE_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_api(request):
    """
    Change user password
    POST /api/user/change-password
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            return JsonResponse({
                'success': False,
                'error': 'All password fields are required',
                'error_code': 'MISSING_PASSWORDS'
            }, status=400)
        
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'error': 'New passwords do not match',
                'error_code': 'PASSWORD_MISMATCH'
            }, status=400)
        
        if len(new_password) < 8:
            return JsonResponse({
                'success': False,
                'error': 'Password must be at least 8 characters long',
                'error_code': 'PASSWORD_TOO_SHORT'
            }, status=400)
        
        user = request.user
        
        # Check current password
        if not user.check_password(current_password):
            return JsonResponse({
                'success': False,
                'error': 'Current password is incorrect',
                'error_code': 'INVALID_CURRENT_PASSWORD'
            }, status=400)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Password change failed',
            'error_code': 'PASSWORD_CHANGE_ERROR'
        }, status=500)

# Market data endpoint
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def market_data_api(request):
    """
    Get market overview data
    GET /api/market-data
    """
    try:
        from .models import Stock
        from django.db.models import Count, Q
        
        # Get market statistics
        total_stocks = Stock.objects.count()
        
        # Calculate gainers/losers based on price_change field
        gainers = Stock.objects.filter(price_change__gt=0).count()
        losers = Stock.objects.filter(price_change__lt=0).count()
        unchanged = total_stocks - gainers - losers
        
        return JsonResponse({
            'success': True,
            'market_overview': {
                'total_stocks': total_stocks,
                'gainers': gainers,
                'losers': losers,
                'unchanged': unchanged
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Market data error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve market data',
            'error_code': 'MARKET_DATA_ERROR'
        }, status=500)


# Token refresh endpoint (session-backed)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def refresh_token_api(request):
    """
    Refresh the session-backed API token.
    Returns current/rotated session key if the user is authenticated.

    POST /api/auth/refresh-token/
    Response: { "token": "<session_key>", "success": true }
    """
    try:
        # Ensure user is authenticated via session or bearer session
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)

        # Ensure session has a key; optionally rotate in future
        try:
            if not request.session.session_key:
                request.session.save()
        except Exception:
            pass

        token = request.session.session_key
        resp = JsonResponse({'success': True, 'token': token})

        # Also ensure CSRF cookie is present to support credentialed POSTs
        try:
            csrf_token = get_token(request)
            resp.set_cookie(
                key=getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken'),
                value=csrf_token,
                secure=getattr(settings, 'CSRF_COOKIE_SECURE', True),
                samesite=getattr(settings, 'CSRF_COOKIE_SAMESITE', 'None'),
                httponly=False,
            )
        except Exception:
            pass

        return resp
    except Exception as e:
        logger.error(f"refresh_token_api error: {e}")
        return JsonResponse({'success': False, 'message': 'Unable to refresh token'}, status=500)