"""
Authentication and User Management API Views
Provides comprehensive user authentication, profile management, and billing endpoints
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import json
import logging
from datetime import datetime, timedelta

from .models import UserProfile, BillingHistory, NotificationSettings
from .security_utils import secure_api_endpoint, validate_user_input

logger = logging.getLogger(__name__)

# Registration endpoint
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    """
    User registration endpoint
    POST /api/auth/register
    """
    try:
        data = json.loads(request.body) if request.body else {}

        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip()
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

        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'error': 'Username already taken',
                'error_code': 'USERNAME_TAKEN'
            }, status=409)

        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'An account with this email already exists',
                'error_code': 'EMAIL_TAKEN'
            }, status=409)

        user = User.objects.create_user(username=username, email=email, password=password,
                                        first_name=first_name, last_name=last_name)
        # Create profile
        profile = UserProfile.objects.create(user=user)

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
def login_api(request):
    """
    User login endpoint
    POST /api/auth/login
    """
    try:
        # Prefer DRF's parsed data, fallback to raw JSON body
        data = getattr(request, 'data', None)
        if data is None or data == {}:
            data = json.loads(request.body) if request.body else {}
        
        # Accept either username or email, trim whitespace
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip()
        password = (data.get('password') or '').strip()
        
        if not username and email:
            try:
                user_lookup = User.objects.get(email__iexact=email)
                username = user_lookup.username
            except User.DoesNotExist:
                # Fall through to invalid credentials
                username = ''
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password are required',
                'error_code': 'MISSING_CREDENTIALS'
            }, status=400)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Get or create user profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                return JsonResponse({
                    'success': True,
                    'data': {
                        'user_id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_premium': profile.is_premium if hasattr(profile, 'is_premium') else False,
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    },
                    'message': 'Login successful'
                })
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